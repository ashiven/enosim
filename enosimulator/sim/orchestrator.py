import secrets

import httpx
import jsons
from enochecker_core import (
    CheckerInfoMessage,
    CheckerMethod,
    CheckerResultMessage,
    CheckerTaskMessage,
    CheckerTaskResult,
)

#### Helpers ####


FLAG_REGEX_ASCII = r"ENO[A-Za-z0-9+\/=]{48}"
REQUEST_TIMEOUT = 10
CHAIN_ID_PREFIX = secrets.token_hex(20)


def _checker_request(
    method,
    round_id,
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
        team_id=0,
        team_name="teamname",
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


def _create_exploit_requests(round_id, team, all_teams):
    exploit_requests = dict()
    other_teams = [other_team for other_team in all_teams if other_team != team]
    for service, flagstores in team.exploiting.items():
        for flagstore_id, (flagstore, do_exploit) in enumerate(flagstores.items()):
            if do_exploit:
                for other_team in other_teams:
                    exploit_request = _checker_request(
                        method="exploit",
                        round_id=round_id,
                        variant_id=flagstore_id,
                        service_address=other_team.address,
                        flag_regex=FLAG_REGEX_ASCII,
                        # TODO: - figure out real values for these fields
                        flag="hmmmmmm",
                        flag_hash="hmmmmmmmmmm",
                        unique_variant_index="hmmmmmm",
                        attack_info="hmmmmmmmmmmmmmmmmmmmm",
                    )
                    exploit_requests[
                        other_team.name, service, flagstore
                    ] = exploit_request
    return exploit_requests


def _update_exploit_requests(exploit_requests, team, all_teams):
    other_teams = [other_team for other_team in all_teams if other_team != team]
    for other_team in other_teams:
        for service, flagstores in other_team.patched.items():
            for flagstore, do_patch in flagstores.items():
                if do_patch:
                    exploit_requests.pop((other_team.name, service, flagstore), None)


def _service_checker_ports(config):
    service_checker_ports = dict()
    for index, service in config["settings"]["services"]:
        service_checker_ports[service] = config["settings"]["checker-ports"][index]
    return service_checker_ports


#### End Helpers ####


class Orchestrator:
    def __init__(self, setup):
        self.setup = setup
        self.client = httpx.AsyncClient()

    async def update_teams(self):
        for service, settings in self.setup.services.items():
            # Get service info from checker
            checker_address = settings["checkers"][0]
            response = await self.client.get(f"{checker_address}/service")
            if response.status_code != 200:
                raise Exception(f"Failed to get {service}-info")
            info: CheckerInfoMessage = jsons.loads(
                response.content,
                CheckerInfoMessage,
                key_transformer=jsons.KEY_TRANSFORMER_SNAKECASE,
            )

            # Update Exploiting / Patched categories for each team
            for settings in self.setup.teams.values():
                settings.exploiting.update({info.service_name: {}})
                settings.patched.update({info.service_name: {}})
                for flagstore_id in range(info.exploit_variants):
                    settings.exploiting[info.service_name].update(
                        {f"Flagstore{flagstore_id}": False}
                    )
                    settings.patched[info.service_name].update(
                        {f"Flagstore{flagstore_id}": False}
                    )

    async def send_exploits(self, round_id, team, all_teams):
        # Create exploit requests for each service/flagstore that the team is exploiting
        exploit_requests = _create_exploit_requests(round_id, team, all_teams)

        # Remove exploit requests for each service/flagstore that the other team has patched
        _update_exploit_requests(exploit_requests, team, all_teams)

        # Send exploit requests to the teams exploit-checker
        service_checker_ports = _service_checker_ports(self.setup.config)
        for (
            _team_name,
            service,
            _flagstore,
            exploit_request,
        ) in exploit_requests.items():
            exploit_checker_ip = team.address
            exploit_checker_port = service_checker_ports[service]
            exploit_checker_address = (
                f"http://{exploit_checker_ip}:{exploit_checker_port}"
            )

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

            print(exploit_result.flag)
