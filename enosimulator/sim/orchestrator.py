import secrets
import urllib

import httpx
import jsons
from enochecker_core import (
    CheckerInfoMessage,
    CheckerMethod,
    CheckerResultMessage,
    CheckerTaskMessage,
    CheckerTaskResult,
)
from sim.flagsubmitter import FlagSubmitter

FLAG_REGEX_ASCII = r"ENO[A-Za-z0-9+\/=]{48}"
CHAIN_ID_PREFIX = secrets.token_hex(20)
REQUEST_TIMEOUT = 10

#### Helpers ####


def _checker_request(
    method,
    round_id,
    team_id,
    team_name,
    variant_id,
    service_address,
    flag,
    unique_variant_index,
    flag_regex,
    flag_hash,
    attack_info,
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


def _req_to_json(request_message):
    return jsons.dumps(
        request_message,
        use_enum_name=False,
        key_transformer=jsons.KEY_TRANSFORMER_CAMELCASE,
        strict=True,
    )


def _port_from_address(address):
    url = urllib.parse.urlparse(address)
    host, _, port = url.netloc.partition(":")
    return port


#### End Helpers ####


class Orchestrator:
    def __init__(self, setup):
        self.setup = setup
        self.client = httpx.AsyncClient()
        self.flag_submitter = FlagSubmitter(setup)
        self.service_checker_ports = dict()
        self.attack_info = None

    async def update_team_info(self):
        for service_name, service in self.setup.services.items():
            # Get service info from checker
            checker_address = service["checkers"][0]
            response = await self.client.get(f"{checker_address}/service")
            if response.status_code != 200:
                raise Exception(f"Failed to get {service_name}-info")
            info: CheckerInfoMessage = jsons.loads(
                response.content,
                CheckerInfoMessage,
                key_transformer=jsons.KEY_TRANSFORMER_SNAKECASE,
            )

            # Store service checker port for later use
            self.service_checker_ports[info.service_name] = _port_from_address(
                checker_address
            )

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

    # TODO:
    # - before i can do these things i need to make sure that the enolandingpage gets launched on the engine
    # - parse the round_id from the scoreboard and return it
    # - if it is too much effort to set up the scoreboard, the round_id is probably not
    # - that important for now (flag validity is not dependent on round_id)
    # - parse the attack_info and set it for self.attack_info
    async def get_round_info(self):
        pass

    async def exploit(self, round_id, team, all_teams):
        # Create exploit requests for each service/flagstore that the team is exploiting
        exploit_requests = self._create_exploit_requests(round_id, team, all_teams)

        # Send exploit requests to the teams exploit-checker
        flags = await self._send_exploit_requests(team, exploit_requests)

        return flags

    # TODO: - test
    def submit_flags(self, team, flags):
        self.flag_submitter.submit_flags(team, flags)

    def _create_exploit_requests(self, round_id, team, all_teams):
        exploit_requests = dict()
        other_teams = [other_team for other_team in all_teams if other_team != team]
        for service, flagstores in team.exploiting.items():
            for flagstore_id, (flagstore, do_exploit) in enumerate(flagstores.items()):
                if do_exploit:
                    for other_team in other_teams:
                        if other_team.patched[service][flagstore]:
                            continue
                        exploit_request = _checker_request(
                            method="exploit",
                            round_id=round_id,
                            team_id=other_team.id,
                            team_name=other_team.name,
                            variant_id=flagstore_id,
                            service_address=other_team.address,
                            flag_regex=FLAG_REGEX_ASCII,
                            flag=None,
                            flag_hash="simulation",
                            unique_variant_index=None,
                            attack_info=self.attack_info[service][flagstore],
                        )
                        exploit_requests[
                            other_team.name, service, flagstore
                        ] = exploit_request
        return exploit_requests

    async def _send_exploit_requests(self, team, exploit_requests):
        flags = []
        for (
            (_team_name, service, _flagstore),
            exploit_request,
        ) in exploit_requests.items():
            exploit_checker_ip = team.address
            exploit_checker_port = self.service_checker_ports[service]
            exploit_checker_address = (
                f"http://{exploit_checker_ip}:{exploit_checker_port}"
            )

            """
            print(
                f"[!] {team.name} exploiting {_team_name} on {service}-{_flagstore}..."
            )
            print(f"[!] Sending exploit request to {exploit_checker_address}...")
            print(f"[!] {exploit_request}")
            """

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
                flags.append(exploit_result.flag)

        return flags
