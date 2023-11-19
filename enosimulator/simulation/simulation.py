import asyncio
import os
import random
import sys
from concurrent.futures import ThreadPoolExecutor
from time import time
from typing import Dict, List, Tuple

from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from setup import Setup
from types_ import SimulationType, Team

from .orchestrator import Orchestrator
from .util import async_lock


class Simulation:
    """
    A Class representing the simulation.

    The main logic of the simulation is contained in this class.

    It is responsible for:
        - Running the main simulation loop
        - Updating the team's exploiting and patched flags
        - Interacting with the orchestrator interface
        - Printing the simulation status


    Attributes:
        setup: The setup object containing all information relevant to the simulation.
        locks: The locks used for synchronizing the simulation.
        orchestrator: The orchestrator used for communicating with the game network.
        verbose: Whether to print verbose output.
        debug: Whether to print debug output.
        console: The console used for printing.
        round_id: The current round ID.
        round_start: The time the current round started.
        round_length: The length of a round in seconds.
        total_rounds: The total number of rounds in the simulation.
        remaining_rounds: The number of rounds remaining in the simulation.
    """

    def __init__(
        self,
        setup: Setup,
        orchestrator: Orchestrator,
        locks: Dict,
        console: Console,
        verbose: bool,
        debug: bool,
    ):
        """Initialize the Simulation class."""

        self.setup = setup
        self.locks = locks
        self.orchestrator = orchestrator
        self.verbose = verbose
        self.debug = debug
        self.console = console
        self.round_id = 0
        self.round_start = 0
        self.round_length = setup.config.ctf_json.round_length_in_seconds
        self.total_rounds = setup.config.settings.duration_in_minutes * (
            60 // setup.config.ctf_json.round_length_in_seconds
        )
        self.remaining_rounds = self.total_rounds

    async def run(self) -> None:
        """
        Run the simulation.

        This is the main simulation loop.
        It ensures that the simulation runs for the specified duration and that the right sequence of events is executed in each round.

        The main simulation loop consists of the following steps:
            1. Update the team's exploiting and patched categories randomly
            2. Send out exploit requests to the team's checkers
            3. Submit flags
            4. Collect system analytics
            5. Print system analytics
            6. Store system analytics in the database
        """

        await self.orchestrator.update_team_info()
        await self._scoreboard_available()

        for round_ in range(self.total_rounds):
            async with async_lock(self.locks["round_info"]):
                self.round_start = time()
                self.remaining_rounds = self.total_rounds - round_
                self.round_id = await self.orchestrator.get_round_info()

            info_messages = await self._update_teams()
            self.info(info_messages)

            self.orchestrator.parse_scoreboard()

            # Send out exploit tasks while collecting system analytics
            exploit_task = asyncio.get_event_loop().create_task(
                self._exploit_all_teams()
            )
            container_panels, system_panels = self._system_analytics()

            # Submit collected flags
            flags = await exploit_task
            self._submit_all_flags(flags)

            # Print system analytics and store them in the database
            self._print_system_analytics(container_panels, system_panels)
            await self.orchestrator.collect_system_analytics()

            round_end = time()
            round_duration = round_end - self.round_start
            if round_duration < self.round_length:
                await asyncio.sleep(self.round_length - round_duration)

    def info(self, info_messages: List[str]) -> None:
        """
        Print the simulation status.

        This method prints the simulation status to the console.
        It prints the following information:
            - The current round ID
            - The number of rounds remaining
            - The infrastructure info
            - The team's exploiting and patched categories
            - The attack info
            - The info messages (optional)

        Args:
            info_messages (List[str]): The info messages to print in addition to the simulation status.
        """

        os.system("cls" if sys.platform == "win32" else "clear")
        self.console.print("\n")
        self.console.log(
            f"[bold blue]Round {self.round_id} ({self.remaining_rounds} rounds remaining):\n"
        )

        if self.verbose:
            self.setup.info()
            self.console.print("\n\n[bold red]Attack info:")
            self.console.print(self.orchestrator.attack_info)

        self.console.print("\n")

        with self.locks["team"]:
            self._team_info(self.setup.teams.values())

        self.console.print("\n")
        if self.verbose:
            for info_message in info_messages:
                self.console.print(info_message)
            self.console.print("\n")

    async def _scoreboard_available(self) -> None:
        """
        A helper method to wait for the scoreboard to become available.

        It tries to get the round info every 2 seconds until the attack info becomes
        available on the engine VM.
        """

        with self.console.status(
            "[bold green]Waiting for scoreboard to become available ..."
        ):
            while not self.orchestrator.attack_info:
                await self.orchestrator.get_round_info()
                await asyncio.sleep(2)

    def _team_info(self, teams: List[Team]) -> None:
        """
        Print the team's exploiting and patched categories.

        This method prints the team's exploiting and patched categories to the console.
        It prints the following information:
            - The team's name
            - The team's experience
            - The team's exploiting and patched categories

        Args:
            teams (List[Team]): The teams to print the info for.
        """

        tables = []
        for team in teams:
            table = Table(
                title=f"Team {team.name} - {str(team.experience)}",
                title_style="bold magenta",
                title_justify="left",
            )
            table.add_column("Exploiting", justify="center", style="magenta")
            table.add_column("Patched", justify="center", style="cyan")

            exploiting = []
            for service, flagstores in team.exploiting.items():
                for flagstore, do_exploit in flagstores.items():
                    if do_exploit:
                        exploiting.append(service + "-" + flagstore)

            patched = []
            for service, flagstores in team.patched.items():
                for flagstore, do_patch in flagstores.items():
                    if do_patch:
                        patched.append(service + "-" + flagstore)
            max_len = max(len(exploiting), len(patched))
            info_list = [
                (
                    exploiting[i] if i < len(exploiting) else None,
                    patched[i] if i < len(patched) else None,
                )
                for i in range(max_len)
            ]

            for exploit_info, patch_info in info_list:
                table.add_row(exploit_info, patch_info)
            tables.append(table)
        self.console.print(Columns(tables))

    def _random_test(self, team: Team) -> bool:
        """
        A helper method to determine whether a team should be updated.

        This method determines whether a team should be updated randomly.
        It does this by comparing a random value to the team's experience.

        Args:
            team (Team): The team to determine whether it should be updated.

        Returns:
            bool: Whether the team should be updated.
        """

        probability = team.experience.value[0]
        random_value = random.random()
        return random_value < probability

    def _choose_random(self, team: Team) -> Tuple[str, str, str]:
        """
        A helper method to choose a random service and flagstore to update.

        This method chooses a random service and flagstore to update.
        It does this by randomly choosing between exploiting and patched.
        Then, it chooses a random service and flagstore from the chosen category.

        Args:
            team (Team): The team to choose a random service and flagstore for.

        Returns:
            Tuple[str, str, str]: The chosen category, service and flagstore.
        """

        try:
            random_variant = random.choice(["exploiting", "patched"])
            if random_variant == "exploiting":
                available_services = {
                    service: flagstores
                    for service, flagstores in team.exploiting.items()
                    if not all(flagstores.values())
                }
                random_service = random.choice(list(available_services))

                exploit_dict = team.exploiting[random_service]
                currently_not_exploiting = {
                    flagstore: exploiting
                    for flagstore, exploiting in exploit_dict.items()
                    if not exploiting
                }
                random_flagstore = random.choice(list(currently_not_exploiting))
            else:
                available_services = {
                    service: flagstores
                    for service, flagstores in team.patched.items()
                    if not all(flagstores.values())
                }
                random_service = random.choice(list(available_services))

                patched_dict = team.patched[random_service]
                currently_not_patched = {
                    flagstore: patched
                    for flagstore, patched in patched_dict.items()
                    if not patched
                }
                random_flagstore = random.choice(list(currently_not_patched))

            return random_variant, random_service, random_flagstore

        except IndexError:
            return None, None, None

    def _update_team(
        self, team_name: str, variant: str, service: str, flagstore: str
    ) -> str:
        """
        A helper method to update a team's exploiting and patched categories.

        This method updates a team's exploiting and patched categories.
        It does this by setting the corresponding category to True.

        Args:
            team_name (str): The name of the team to update.
            variant (str): The category to update.
            service (str): The service to update.
            flagstore (str): The flagstore to update.

        Returns:
            str: An info message about the update.
        """

        if variant == "exploiting":
            self.setup.teams[team_name].exploiting[service][flagstore] = True
            info_text = "started exploiting"
        elif variant == "patched":
            self.setup.teams[team_name].patched[service][flagstore] = True
            info_text = "patched"
        else:
            return ""

        return f"[bold red][!] Team {team_name} {info_text} {service}-{flagstore}"

    async def _update_teams(self) -> List[str]:
        """
        A helper method to update the team's exploiting and patched categories.

        This method updates the team's exploiting and patched categories.
        It does this by randomly choosing a category to update if a team passes the random test.
        Then, it randomly chooses and updates a service and flagstore in the given category.

        Returns:
            List[str]: A list of info messages about the updates.
        """

        info_messages = []
        if self.setup.config.settings.simulation_type == SimulationType.REALISTIC.value:
            async with async_lock(self.locks["team"]):
                for team_name, team in self.setup.teams.items():
                    if self._random_test(team):
                        random_choice = self._choose_random(team)
                        variant, service, flagstore = random_choice
                        info_message = self._update_team(
                            team_name, variant, service, flagstore
                        )
                        info_messages.append(info_message)

        return info_messages

    async def _exploit_all_teams(self) -> List:
        """
        A helper method to send out exploit requests to the team's checkers.

        This method sends out exploit requests to the team's checkers.
        It does this by creating a task for each team and waiting for them to finish.

        Returns:
            List: A list containing the team's IP address and the flags that were collected.
        """

        exploit_status = self.console.status("[bold green]Sending exploits ...")
        if not self.debug:
            exploit_status.start()

        team_flags = []
        for team in self.setup.teams.values():
            team_flags.append([team.address])

        async with asyncio.TaskGroup() as task_group:
            tasks = [
                task_group.create_task(
                    self.orchestrator.exploit(
                        self.round_id, team, self.setup.teams.values()
                    )
                )
                for team in self.setup.teams.values()
            ]

        for task_index, task in enumerate(tasks):
            team_flags[task_index].append(task.result())

        if not self.debug:
            exploit_status.stop()

        return team_flags

    def _system_analytics(self) -> Tuple[Dict[str, Panel], Dict[str, List[Panel]]]:
        """
        A helper method to collect system analytics.

        This method collects system analytics.
        It does this by calling the orchestrator's container_stats and system_stats methods.

        Returns:
            Tuple[Dict[str, Panel], Dict[str, List[Panel]]]: A tuple containing the Docker container and system statistics panels.
        """

        container_panels = self.orchestrator.container_stats(
            self.setup.ips.public_ip_addresses
        )
        system_panels = self.orchestrator.system_stats(
            self.setup.ips.public_ip_addresses
        )

        return container_panels, system_panels

    def _submit_all_flags(self, team_flags: List) -> None:
        """
        A helper method to submit flags.

        This method submits flags.
        It does this by creating a thread for each team and waiting for them to finish.

        Args:
            team_flags (List): A list containing the team's IP address and the flags that were collected.
        """

        with ThreadPoolExecutor(
            max_workers=self.setup.config.settings.teams
        ) as executor:
            for team_address, flags in team_flags:
                if flags:
                    executor.submit(self.orchestrator.submit_flags, team_address, flags)

    def _print_system_analytics(self, container_panels, system_panels) -> None:
        """
        A helper method to print system analytics.

        This method prints system analytics to the console.
        It does this by printing the Docker container and system statistics panels.

        Args:
            container_panels (Dict[str, Panel]): A dictionary containing the Docker container statistics panels.
            system_panels (Dict[str, List[Panel]]): A dictionary containing the system statistics panels.
        """

        if self.verbose:
            for name, container_stat_panel in container_panels.items():
                self.console.print(f"[bold red]Docker stats for {name}:")
                self.console.print(container_stat_panel)
                self.console.print("")

            for name, system_stat_panel in system_panels.items():
                self.console.print(f"[bold red]System stats for {name}:")
                self.console.print(Columns(system_stat_panel))
                self.console.print("")

            self.console.print("\n")
