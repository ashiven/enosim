import asyncio
from typing import Dict, List, Tuple

import jsons
from bs4 import BeautifulSoup
from enochecker_core import (
    CheckerInfoMessage,
    CheckerResultMessage,
    CheckerTaskMessage,
    CheckerTaskResult,
)
from httpx import AsyncClient
from rich.console import Console
from rich.panel import Panel
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from setup import Setup
from tenacity import retry, stop_after_attempt
from types_ import SimulationType, Team, VMType
from webdriver_manager.chrome import ChromeDriverManager

from .flagsubmitter import FlagSubmitter
from .statchecker import StatChecker
from .util import (
    REQUEST_TIMEOUT,
    async_lock,
    checker_request,
    port_from_address,
    private_to_public_ip,
    req_to_json,
)

FLAG_REGEX_ASCII = r"ENO[A-Za-z0-9+\/=]{48}"
FLAG_HASH = "ignore_flag_hash"


class Orchestrator:
    """
    A Class for orchestrating the simulation.

    This class is provides an interface for all tasks that involve interacting with the infrastructure including:
        - Getting the current round's attack information.
        - Parsing the scoreboard.
        - Collecting system analytics.
        - Instructing teams to exploit other teams.
        - Submitting flags for teams.

    Attributes:
        setup: The setup object containing all information about the simulation setup.
        verbose: Whether to print verbose output.
        debug: Whether to print debug output.
        locks: The locks used for synchronizing access to shared resources with the Flask server running in a separate thread.
        service_info: A dictionary containing information about each service.
        private_to_public_ip: A dictionary mapping private IP addresses to public IP addresses.
        attack_info: A dictionary containing the current round's attack information.
        client: The HTTP client used for sending requests.
        flag_submitter: The flag submitter used for submitting flags.
        stat_checker: The stat checker used for collecting system analytics.
        console: The console used for printing.
    """

    def __init__(
        self,
        setup: Setup,
        locks: Dict,
        client: AsyncClient,
        flag_submitter: FlagSubmitter,
        stat_checker: StatChecker,
        console: Console,
        verbose: bool = False,
        debug: bool = False,
    ):
        """Initialize the Orchestrator class."""

        self.setup = setup
        self.verbose = verbose
        self.debug = debug
        self.locks = locks
        self.service_info = dict()
        self.private_to_public_ip = private_to_public_ip(setup.ips)
        self.attack_info = None
        self.client = client
        self.flag_submitter = flag_submitter
        self.stat_checker = stat_checker
        self.console = console

    async def update_team_info(self) -> None:
        """
        Update the team information for each team.

        For each service played in the competition, each team's exploiting and patched
        categories are initialized.

        In realistic or basic-stress-test simulation setups, the exploiting and patched
        categories are initialized to False for every service / flagstore. In all other
        simulation setups (stress-test, intesive-stress-test), the exploiting category
        is initialized to True for every service / flagstore.
        """

        async with async_lock(self.locks["service"]):
            for service in self.setup.services.values():
                info = await self._get_service_info(service)

                async with async_lock(self.locks["team"]):
                    # Update Exploiting / Patched categories for each team
                    for team in self.setup.teams.values():
                        team.exploiting.update({info.service_name: {}})
                        team.patched.update({info.service_name: {}})
                        for flagstore_id in range(info.exploit_variants):
                            team.exploiting[info.service_name].update(
                                {f"Flagstore{flagstore_id}": False}
                                if self.setup.config.settings.simulation_type
                                == SimulationType.REALISTIC.value
                                or self.setup.config.settings.simulation_type
                                == SimulationType.BASIC_STRESS_TEST.value
                                else {f"Flagstore{flagstore_id}": True}
                            )
                            team.patched[info.service_name].update(
                                {f"Flagstore{flagstore_id}": False}
                            )

    async def get_round_info(self) -> int:
        """
        Get the current round's attack information and round id and store the attack
        information in the attack_info attribute.

        The attack information later gets used for constructing checker task requests for exploiting other teams.

        Returns:
            int: The current round's ID.
        """

        attack_info_text = await self.client.get(
            f"http://{self.setup.ips.public_ip_addresses[VMType.ENGINE.value]}:5001/scoreboard/attack.json"
        )
        if attack_info_text.status_code != 200:
            return None

        attack_info = jsons.loads(attack_info_text.content)
        if not attack_info["services"]:
            return None

        self.attack_info = attack_info
        _prev_round, current_round = self._parse_rounds(self.attack_info)
        return current_round

    def parse_scoreboard(self) -> None:
        """
        Parse the scoreboard and update each team's points and gain.

        These values become accessible through the Flask server's API.
        """

        with self.console.status("[bold green]Parsing scoreboard ..."):
            team_scores = self._get_team_scores()
            with self.locks["team"]:
                for team in self.setup.teams.values():
                    team.points = team_scores[team.name][0]
                    team.gain = team_scores[team.name][1]

    def container_stats(self, addresses: Dict[str, str]) -> Dict[str, Panel]:
        """
        Get the Docker container statistics for a set of VMs.

        Args:
            addresses (Dict[str, str]): A dictionary mapping vm names to their public IP addresses.

        Returns:
            Dict[str, Panel]: A dictionary mapping vm names to container statistics panels.
        """

        return self.stat_checker.check_containers(addresses)

    def system_stats(self, addresses: Dict[str, str]) -> Dict[str, List[Panel]]:
        """
        Get the system statistics for a set of VMs.

        Args:
            addresses (Dict[str, str]): A dictionary mapping vm names to their public IP addresses.

        Returns:
            Dict[str, List[Panel]]: A dictionary mapping vm names to lists of system statistics panels.
        """

        return self.stat_checker.check_system(addresses)

    async def exploit(
        self, round_id: int, team: Team, all_teams: List[Team]
    ) -> List[str]:
        """
        Exploit all other teams for a given team.

        Args:
            round_id (int): The current round's ID.
            team (Team): The team to exploit for.
            all_teams (List[Team]): A list of all participating teams.

        Returns:
            List[str]: A list of flags that were obtained by exploiting other teams.
        """

        exploit_requests = self._create_exploit_requests(round_id, team, all_teams)
        flags = await self._send_exploit_requests(team, exploit_requests)
        return flags

    def submit_flags(self, team_address: str, flags: List[str]) -> None:
        """
        Submit flags for a given team.

        Args:
            team_address (str): The IP address of the team's VM.
            flags (List[str]): The flags to submit.
        """

        self.flag_submitter.submit_flags(team_address, flags)

    async def collect_system_analytics(self) -> None:
        """
        Collect system analytics for each VM.

        The system statistics and Docker statistics retrieved in each round are
        propagated to the database and become accessible through the Flask server's API.
        """

        with self.console.status("[bold green]Collecting analytics ..."):
            await self.stat_checker.system_analytics()

    @retry(stop=stop_after_attempt(10))
    async def _get_service_info(self, service: Service) -> CheckerInfoMessage:
        """
        Get the service information from the checker for a given Service object.

        Args:
            service (Service): The Service object to obtain the information for.

        Returns:
            CheckerInfoMessage: The service information for the given Service object.
        """

        checker_address = service.checkers[0]
        response = await self.client.get(f"{checker_address}/service")
        if response.status_code != 200:
            raise Exception(f"Failed to get {service.name}-info")
        info = jsons.loads(
            response.content,
            CheckerInfoMessage,
            key_transformer=jsons.KEY_TRANSFORMER_SNAKECASE,
        )

        # Store service checker port for later use
        self.service_info[info.service_name] = (
            port_from_address(checker_address),
            service.name,
        )

        return info

    def _parse_rounds(self, attack_info: Dict) -> Tuple[int, int]:
        """
        Parse the round IDs from the attack information.

        Args:
            attack_info (Dict): The attack information to parse.

        Returns:
            Tuple[int, int]: A tuple containing the previous round's ID and the current round's ID.
        """

        try:
            first_service = list(attack_info["services"].values())[0]
            first_team = list(first_service.values())[0]
            prev_round = list(first_team.keys())[0]
            current_round = list(first_team.keys())[1]
        except Exception:
            prev_round, current_round = 1, 1
        return int(prev_round), int(current_round)

    @retry(stop=stop_after_attempt(10))
    def _get_team_scores(self) -> Dict[str, Tuple[float, float]]:
        """
        Get the team scores from the scoreboard.

        Uses Selenium in headless mode to parse the current team scores from the scoreboard running on the engine VM.

        Returns:
            Dict[str, Tuple[float, float]]: A dictionary mapping team names to tuples containing the team's points and gain.
        """

        team_scores = dict()
        scoreboard_url = f"http://{self.setup.ips.public_ip_addresses[VMType.ENGINE.value]}:5001/scoreboard"

        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), options=options
        )
        driver.get(scoreboard_url)

        wait = WebDriverWait(driver, 10)
        wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "otherrow")))

        soup = BeautifulSoup(driver.page_source, "html.parser")
        rows = soup.find_all("tr", class_="otherrow")

        for row in rows:
            [points, gain] = row.find("td", class_="team-score").text.strip().split(" ")
            team_name = row.find("div", class_="team-name").find("a").text.strip()
            team_scores[team_name] = (float(points), float(gain[2:-1]))

        driver.quit()

        return team_scores

    def _create_exploit_requests(
        self, round_id: int, team: Team, all_teams: List[Team]
    ) -> Dict[Tuple[str, str, str, str], CheckerTaskMessage]:
        """
        Create checker task requests for a team to exploit all other teams.

        Args:
            round_id (int): The current round's ID.
            team (Team): The team to exploit for.
            all_teams (List[Team]): A list of all participating teams.

        Returns:
            Dict[Tuple[str, str, str, str], CheckerTaskMessage]: A dictionary mapping tuples containing the team name, service name, flagstore, and attack info to checker task requests.
        """

        exploit_requests = dict()
        other_teams = [other_team for other_team in all_teams if other_team != team]
        for service, flagstores in team.exploiting.items():
            for flagstore_id, (flagstore, do_exploit) in enumerate(flagstores.items()):
                if do_exploit:
                    for other_team in other_teams:
                        if (
                            other_team.patched[service][flagstore]
                            or other_team.address == team.address
                        ):
                            continue

                        try:
                            service_name = self.service_info[service][1]
                            attack_info = self.attack_info["services"][service_name][
                                other_team.address
                            ][str(round_id)][str(flagstore_id)]
                        except Exception:
                            attack_info = None

                        if attack_info:
                            for info in attack_info:
                                exploit_request = checker_request(
                                    method="exploit",
                                    round_id=round_id,
                                    team_id=other_team.id,
                                    team_name=other_team.name,
                                    variant_id=flagstore_id,
                                    service_address=other_team.address,
                                    flag_regex=FLAG_REGEX_ASCII,
                                    flag=None,
                                    flag_hash=FLAG_HASH,
                                    unique_variant_index=None,
                                    attack_info=info,
                                )

                                exploit_requests[
                                    other_team.name, service, flagstore, info
                                ] = exploit_request

        return exploit_requests

    async def _send_exploit_requests(
        self, team: Team, exploit_requests: Dict
    ) -> List[str]:
        """
        Send exploit checker task requests to the specified team's checker.

        Args:
            team (Team): The team to exploit for.
            exploit_requests (Dict): A dictionary mapping tuples containing the team name, service name, flagstore, and attack info to checker task requests.

        Returns:
            List[str]: A list of flags that were obtained by exploiting other teams.
        """

        tasks = []
        async with asyncio.TaskGroup() as task_group:
            for (
                (team_name, service, flagstore, _info),
                exploit_request,
            ) in exploit_requests.items():
                exploit_checker_ip = self.private_to_public_ip[team.address]
                exploit_checker_port = self.service_info[service][0]
                exploit_checker_address = (
                    f"http://{exploit_checker_ip}:{exploit_checker_port}"
                )

                if self.debug:
                    self.console.log(
                        f"[bold green]{team.name} :anger_symbol: {team_name}-{service}-{flagstore}"
                    )
                    self.console.log(exploit_request)

                    exploit_task = task_group.create_task(
                        self.client.post(
                            exploit_checker_address,
                            data=req_to_json(exploit_request),
                            headers={"Content-Type": "application/json"},
                            timeout=REQUEST_TIMEOUT,
                        )
                    )
                    tasks.append(exploit_task)

        results = [task.result() for task in tasks]

        flags = []
        for r in results:
            exploit_result = jsons.loads(
                r.content,
                CheckerResultMessage,
                key_transformer=jsons.KEY_TRANSFORMER_SNAKECASE,
            )

            if CheckerTaskResult(exploit_result.result) is not CheckerTaskResult.OK:
                if self.debug:
                    self.console.print(exploit_result.message)
            else:
                if self.debug:
                    self.console.log(
                        f"[bold green]:triangular_flag:: {exploit_result.flag}\n"
                    )
                flags.append(exploit_result.flag)

        return flags
