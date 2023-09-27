import secrets

import jsons
from enochecker_core import CheckerInfoMessage, CheckerMethod, CheckerTaskMessage
from requests import Session
from requests.adapters import HTTPAdapter, Retry

#### Helpers ####


FLAG_REGEX_ASCII = r"ENO[A-Za-z0-9+\/=]{48}"
FLAG_REGEX_UTF8 = r"🥺[A-Za-z0-9+\/=]{48}🥺🥺"
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


#### End Helpers ####


class Orchestrator:
    def __init__(self, setup):
        self.setup = setup
        self.session = Session()
        retry_strategy = Retry(
            total=5,
            backoff_factor=1,
        )
        self.session.mount("http://", HTTPAdapter(max_retries=retry_strategy))

    def update_teams(self):
        for service, settings in self.setup.services.items():
            # Get service info from checker
            checker_address = settings["checkers"][0]
            response = self.session.get(f"{checker_address}/service")
            if response.status_code != 200:
                raise Exception(f"Failed to get {service}-info")
            info: CheckerInfoMessage = jsons.loads(
                response.content,
                CheckerInfoMessage,
                key_transformer=jsons.KEY_TRANSFORMER_SNAKECASE,
            )

            # Update Exploiting / Patched categories for each team
            for settings in self.setup.teams.values():
                settings["exploiting"].update({info.service_name: {}})
                settings["patched"].update({info.service_name: {}})
                for flagstore_id in range(info.exploit_variants):
                    settings["exploiting"][info.service_name].update(
                        {f"Flagstore{flagstore_id}": False}
                    )
                    settings["patched"][info.service_name].update(
                        {f"Flagstore{flagstore_id}": False}
                    )

    def send_exploit(source_team, target_team, service, flagstore):
        pass
