import asyncio
import os
import random
import sys
from concurrent.futures import ThreadPoolExecutor
from threading import Thread
from time import time
from typing import Dict, List

from rich.console import Console
from rich.table import Table
from setup.types import OrchestratorType, SetupType, Team

from .orchestrator import Orchestrator
from .util import async_lock


class Simulation:
    def __init__(
        self,
        setup: SetupType,
        orchestrator: OrchestratorType,
        locks: Dict,
        verbose: bool,
    ):
        self.setup = setup
        self.locks = locks
        self.orchestrator = orchestrator
        self.verbose = verbose
        self.console = Console()
        self.round_id = 0
        self.total_rounds = setup.config.settings.duration_in_minutes * (
            60 // setup.config.ctf_json.round_length_in_seconds
        )
        self.round_length = setup.config.ctf_json.round_length_in_seconds

    @classmethod
    async def new(cls, setup: SetupType, locks: Dict, verbose: bool = False):
        orchestrator = Orchestrator(setup, locks, verbose)
        await orchestrator.update_team_info()
        return cls(setup, orchestrator, locks, verbose)

    async def run(self):
        await self._scoreboard_available()

        for round_ in range(self.total_rounds):
            start = time()

            # Go through all teams and perform the random test
            info_messages = await self._update_exploiting_and_patched()

            # Get the current round id and attack info
            self.round_id = await self.orchestrator.get_round_info()

            # Display all info relevant to the current round and parse the current scores from the scoreboard
            scoreboard_thread = Thread(target=self.orchestrator.parse_scoreboard)
            scoreboard_thread.start()
            self.round_info(info_messages, self.total_rounds - round_)
            scoreboard_thread.join()

            # Instruct orchestrator to send out exploit requests
            team_flags = await self._exploit_all_teams()

            # Instruct orchestrator to submit flags
            self._submit_all_flags(team_flags)

            # Send system statistics to the analytics server at the end of each round
            await self.orchestrator.system_analytics()

            # Wait for the round to end
            end = time()
            round_duration = end - start
            if round_duration < self.round_length:
                await asyncio.sleep(self.round_length - round_duration)

    def round_info(self, info_messages: List[str], remaining: int):
        os.system("cls" if sys.platform == "win32" else "clear")
        self.console.print("\n")
        self.console.log(
            f"[bold blue]Round {self.round_id} info ({remaining} rounds remaining):\n"
        )

        if self.verbose:
            self.setup.info()
            self.console.print("\n[bold red]Attack info:")
            self.console.print(self.orchestrator.attack_info)

        self.orchestrator.container_stats(self.setup.ips.public_ip_addresses)
        self.orchestrator.system_stats(self.setup.ips.public_ip_addresses)
        self.console.print("\n")

        with self.locks["team"]:
            self._team_info(self.setup.teams.values())

        if self.verbose:
            self.console.print("\n")
            for info_message in info_messages:
                self.console.print(info_message)
            self.console.print("\n")

    async def _scoreboard_available(self):
        with self.console.status(
            "[bold green]Waiting for scoreboard to become available ..."
        ):
            while not self.orchestrator.attack_info:
                await self.orchestrator.get_round_info()
                await asyncio.sleep(2)

    def _random_test(self, team: Team):
        probability = team.experience.value[0]
        random_value = random.random()
        return random_value < probability

    def _exploit_or_patch(self, team: Team):
        random_variant = random.choice(["exploiting", "patched"])
        if random_variant == "exploiting":
            random_service = random.choice(list(team.exploiting))
            random_flagstore = random.choice(list(team.exploiting[random_service]))
        else:
            random_service = random.choice(list(team.patched))
            random_flagstore = random.choice(list(team.patched[random_service]))

        return random_variant, random_service, random_flagstore

    def _update_team(self, team_name: str, variant: str, service: str, flagstore: str):
        if variant == "exploiting":
            self.setup.teams[team_name].exploiting[service][flagstore] = True
            info_text = "started exploiting"
        elif variant == "patched":
            self.setup.teams[team_name].patched[service][flagstore] = True
            info_text = "patched"
        return f"[bold red][!] Team {team_name} {info_text} {service}-{flagstore}"

    async def _update_exploiting_and_patched(self):
        info_messages = []
        if self.setup.config.settings.simulation_type == "realistic":
            async with async_lock(self.locks["team"]):
                for team_name, team in self.setup.teams.items():
                    if self._random_test(team):
                        variant, service, flagstore = self._exploit_or_patch(team)
                        info_message = self._update_team(
                            team_name, variant, service, flagstore
                        )
                        info_messages.append(info_message)

        return info_messages

    def _team_info(self, teams: List[Team]):
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
            self.console.print(table)

    async def _exploit_all_teams(self) -> List:
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

        return team_flags

    def _submit_all_flags(self, team_flags: List):
        with ThreadPoolExecutor(max_workers=20) as executor:
            for team_address, flags in team_flags:
                if flags:
                    executor.submit(self.orchestrator.submit_flags, team_address, flags)
