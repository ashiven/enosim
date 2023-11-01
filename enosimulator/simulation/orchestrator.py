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
from types_ import Team
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
                                == "realistic"
                                or self.setup.config.settings.simulation_type
                                == "basic-stress-test"
                                else {f"Flagstore{flagstore_id}": True}
                            )
                            team.patched[info.service_name].update(
                                {f"Flagstore{flagstore_id}": False}
                            )

    async def get_round_info(self) -> int:
        attack_info_text = await self.client.get(
            f'http://{self.setup.ips.public_ip_addresses["engine"]}:5001/scoreboard/attack.json'
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
        with self.console.status("[bold green]Parsing scoreboard ..."):
            team_scores = self._get_team_scores()
            with self.locks["team"]:
                for team in self.setup.teams.values():
                    team.points = team_scores[team.name][0]
                    team.gain = team_scores[team.name][1]

    def container_stats(self, team_addresses: Dict[str, str]) -> Dict[str, Panel]:
        return self.stat_checker.check_containers(team_addresses)

    def system_stats(self, team_addresses: Dict[str, str]) -> Dict[str, List[Panel]]:
        return self.stat_checker.check_system(team_addresses)

    async def exploit(
        self, round_id: int, team: Team, all_teams: List[Team]
    ) -> List[str]:
        exploit_requests = self._create_exploit_requests(round_id, team, all_teams)
        flags = await self._send_exploit_requests(team, exploit_requests)
        return flags

    def submit_flags(self, team_address: str, flags: List[str]) -> None:
        self.flag_submitter.submit_flags(team_address, flags)

    async def collect_system_analytics(self) -> None:
        with self.console.status("[bold green]Collecting analytics ..."):
            await self.stat_checker.system_analytics()

    @retry(stop=stop_after_attempt(10))
    async def _get_service_info(self, service: Service) -> CheckerInfoMessage:
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
        try:
            first_service = list(attack_info["services"].values())[0]
            first_team = list(first_service.values())[0]
            prev_round = list(first_team.keys())[0]
            current_round = list(first_team.keys())[1]
        except:
            prev_round, current_round = 1, 1
        return int(prev_round), int(current_round)

    @retry(stop=stop_after_attempt(10))
    def _get_team_scores(self) -> Dict[str, Tuple[float, float]]:
        team_scores = dict()
        scoreboard_url = (
            f'http://{self.setup.ips.public_ip_addresses["engine"]}:5001/scoreboard'
        )

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
    ) -> Dict[Tuple[str, str, str], CheckerTaskMessage]:
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
                            attack_info = ",".join(
                                self.attack_info["services"][
                                    self.service_info[service][1]
                                ][other_team.address][str(round_id)][str(flagstore_id)]
                            )
                        except:
                            attack_info = None

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
                            attack_info=attack_info,
                        )

                        exploit_requests[
                            other_team.name, service, flagstore
                        ] = exploit_request

        return exploit_requests

    async def _send_exploit_requests(
        self, team: Team, exploit_requests: Dict
    ) -> List[str]:
        flags = []
        for (
            (team_name, service, flagstore),
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

            try:
                r = await self.client.post(
                    exploit_checker_address,
                    data=req_to_json(exploit_request),
                    headers={"Content-Type": "application/json"},
                    timeout=REQUEST_TIMEOUT,
                )

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
            except:
                pass

        return flags
