import secrets
import urllib
from typing import Dict, List

import httpx
import jsons
from bs4 import BeautifulSoup
from enochecker_core import (
    CheckerInfoMessage,
    CheckerMethod,
    CheckerResultMessage,
    CheckerTaskMessage,
    CheckerTaskResult,
)
from rich.console import Console
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from setup.types import IpAddresses, SetupType, Team
from webdriver_manager.chrome import ChromeDriverManager

from .flagsubmitter import FlagSubmitter
from .statchecker import StatChecker
from .util import async_lock

FLAG_REGEX_ASCII = r"ENO[A-Za-z0-9+\/=]{48}"
CHAIN_ID_PREFIX = secrets.token_hex(20)
REQUEST_TIMEOUT = 10

#### Helpers ####


def _checker_request(
    method: str,
    round_id: int,
    team_id: int,
    team_name: str,
    variant_id: int,
    service_address: str,
    flag: str,
    unique_variant_index: int,
    flag_regex: str,
    flag_hash: str,
    attack_info: str,
):
    # Generate a unique task chain id for each task according to enoengine specs
    if not unique_variant_index:
        unique_variant_index = variant_id
    prefix = "havoc"
    if method in ("putflag", "getflag"):
        prefix = "flag"
    elif method in ("putnoise", "getnoise"):
        prefix = "noise"
    elif method == "exploit":
        prefix = "exploit"
    task_chain_id = (
        f"{CHAIN_ID_PREFIX}_{prefix}_s0_r{round_id}_t0_i{unique_variant_index}"
    )

    return CheckerTaskMessage(
        task_id=round_id,
        method=CheckerMethod(method),
        address=service_address,
        team_id=team_id,
        team_name=team_name,
        current_round_id=round_id,
        related_round_id=round_id,
        flag=flag,
        variant_id=variant_id,
        timeout=REQUEST_TIMEOUT * 1000,
        round_length=60000,
        task_chain_id=task_chain_id,
        flag_regex=flag_regex,
        flag_hash=flag_hash,
        attack_info=attack_info,
    )


def _req_to_json(request_message: CheckerTaskMessage):
    return jsons.dumps(
        request_message,
        use_enum_name=False,
        key_transformer=jsons.KEY_TRANSFORMER_CAMELCASE,
        strict=True,
    )


def _port_from_address(address: str):
    url = urllib.parse.urlparse(address)
    host, _, port = url.netloc.partition(":")
    return port


def _parse_rounds(attack_info: Dict):
    try:
        first_service = list(attack_info["services"].values())[0]
        first_team = list(first_service.values())[0]
        prev_round = list(first_team.keys())[0]
        current_round = list(first_team.keys())[1]
    except:
        prev_round, current_round = 1, 1
    return int(prev_round), int(current_round)


def _private_to_public_ip(ip_addresses: IpAddresses, team_address: str):
    for name, ip_address in ip_addresses.private_ip_addresses.items():
        if ip_address == team_address:
            return ip_addresses.public_ip_addresses[name]


#### End Helpers ####


class Orchestrator:
    def __init__(self, setup: SetupType, locks: Dict, verbose: bool = False):
        self.setup = setup
        self.verbose = verbose
        self.locks = locks
        self.service_info = dict()
        self.attack_info = None
        self.client = httpx.AsyncClient()
        self.flag_submitter = FlagSubmitter(
            setup.ips, setup.config, setup.secrets, self.verbose
        )
        self.stat_checker = StatChecker(setup.config, setup.secrets, verbose)
        self.console = Console()

    async def update_team_info(self):
        async with async_lock(self.locks["service"]):
            for service_name, service in self.setup.services.items():
                # Get service info from checker
                checker_address = service.checkers[0]
                response = await self.client.get(f"{checker_address}/service")
                if response.status_code != 200:
                    raise Exception(f"Failed to get {service_name}-info")
                info: CheckerInfoMessage = jsons.loads(
                    response.content,
                    CheckerInfoMessage,
                    key_transformer=jsons.KEY_TRANSFORMER_SNAKECASE,
                )

                # Store service checker port for later use
                self.service_info[info.service_name] = (
                    _port_from_address(checker_address),
                    service_name,
                )

                async with async_lock(self.locks["team"]):
                    # Update Exploiting / Patched categories for each team
                    for team in self.setup.teams.values():
                        team.exploiting.update({info.service_name: {}})
                        team.patched.update({info.service_name: {}})
                        for flagstore_id in range(info.exploit_variants):
                            team.exploiting[info.service_name].update(
                                {f"Flagstore{flagstore_id}": False}
                            )
                            team.patched[info.service_name].update(
                                {f"Flagstore{flagstore_id}": False}
                            )

    async def get_round_info(self):
        attack_info_text = await self.client.get(
            f'http://{self.setup.ips.public_ip_addresses["engine"]}:5001/scoreboard/attack.json'
        )
        if attack_info_text.status_code != 200:
            return None

        attack_info = jsons.loads(attack_info_text.content)
        if not attack_info["services"]:
            return None

        self.attack_info = attack_info
        _prev_round, current_round = _parse_rounds(self.attack_info)
        return current_round

    def parse_scoreboard(self):
        team_scores = self._get_team_scores()
        with self.locks["team"]:
            for team in self.setup.teams.values():
                team.points = team_scores[team.name][0]
                team.gain = team_scores[team.name][1]

    async def exploit(self, round_id: int, team: Team, all_teams: List[Team]):
        exploit_requests = self._create_exploit_requests(round_id, team, all_teams)
        flags = await self._send_exploit_requests(team, exploit_requests)
        return flags

    def submit_flags(self, team_address: str, flags: List[str]):
        self.flag_submitter.submit_flags(team_address, flags)

    # TODO: -figure out why the status doesn't disappear from stdout
    def container_stats(self, team_addresses: Dict[str, str]):
        with self.console.status("[bold green]Getting container stats ..."):
            self.stat_checker.check_containers(team_addresses)

    # TODO: -figure out why the status doesn't disappear from stdout
    def system_stats(self, team_addresses: Dict[str, str]):
        with self.console.status("[bold green]Getting system stats ..."):
            self.stat_checker.check_system(team_addresses)

    async def system_analytics(self):
        with self.console.status("[bold green]Sending analytic data ..."):
            await self.stat_checker.system_analytics()

    def _create_exploit_requests(
        self, round_id: int, team: Team, all_teams: List[Team]
    ):
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

                        exploit_request = _checker_request(
                            method="exploit",
                            round_id=round_id,
                            team_id=other_team.id,
                            team_name=other_team.name,
                            variant_id=flagstore_id,
                            service_address=other_team.address,
                            flag_regex=FLAG_REGEX_ASCII,
                            flag=None,
                            flag_hash="ignore_flag_hash",
                            unique_variant_index=None,
                            attack_info=attack_info,
                        )
                        exploit_requests[
                            other_team.name, service, flagstore
                        ] = exploit_request
        return exploit_requests

    async def _send_exploit_requests(self, team: Team, exploit_requests: Dict):
        flags = []
        for (
            (_team_name, service, _flagstore),
            exploit_request,
        ) in exploit_requests.items():
            exploit_checker_ip = _private_to_public_ip(self.setup.ips, team.address)
            exploit_checker_port = self.service_info[service][0]
            exploit_checker_address = (
                f"http://{exploit_checker_ip}:{exploit_checker_port}"
            )

            if self.verbose:
                self.console.log(
                    f"[bold green]{team.name} :anger_symbol: {_team_name}-{service}-{_flagstore}"
                )
                self.console.log(exploit_request)

            r = await self.client.post(
                exploit_checker_address,
                data=_req_to_json(exploit_request),
                headers={"Content-Type": "application/json"},
                timeout=REQUEST_TIMEOUT,
            )

            exploit_result = jsons.loads(
                r.content,
                CheckerResultMessage,
                key_transformer=jsons.KEY_TRANSFORMER_SNAKECASE,
            )

            if CheckerTaskResult(exploit_result.result) is not CheckerTaskResult.OK:
                print(exploit_result.message)
            else:
                if self.verbose:
                    self.console.log(
                        f"[bold green]:triangular_flag:: {exploit_result.flag}\n"
                    )
                flags.append(exploit_result.flag)

        return flags

    def _get_team_scores(self):
        team_scores = dict()
        scoreboard_url = (
            f'http://{self.setup.ips.public_ip_addresses["engine"]}:5001/scoreboard'
        )

        options = Options()
        options.headless = True
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
