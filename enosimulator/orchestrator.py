import jsons
from enochecker_core import CheckerInfoMessage
from requests import Session
from requests.adapters import HTTPAdapter, Retry


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
        for service in self.setup.services:
            # Get service info from checker
            checker_address = service.checkers[0]
            response = self.session.get(f"{checker_address}/service")
            if response.status_code != 200:
                raise Exception("Failed to get service info from checker")
            info: CheckerInfoMessage = jsons.loads(
                response.content,
                CheckerInfoMessage,
                key_transformer=jsons.KEY_TRANSFORMER_SNAKECASE,
            )

            # Update Exploiting / Patched categories for each team
            for team in self.setup.teams:
                team["exploiting"].update({info.service.name: {}})
                team["patched"].update({info.service.name: {}})
                for flagstore_id in range(1, info.exploit_variants + 1):
                    team["exploiting"][info.service_name].update(
                        {f"{service.name}-Flag{flagstore_id}": False}
                    )
                    team["patched"][info.service_name].update(
                        {f"{service.name}-Flag{flagstore_id}": False}
                    )
