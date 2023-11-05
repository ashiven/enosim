from typing import Dict, List, Tuple

from aenum import extend_enum
from types_ import Config, Experience, Secrets, SetupVariant, Team

from .azure import AzureSetupHelper
from .hetzner import HetznerSetupHelper
from .local import LocalSetupHelper
from .team_generator import TeamGenerator


class SetupHelper:
    def __init__(self, config: Config, secrets: Secrets, team_generator: TeamGenerator):
        self.config = config
        self.secrets = secrets
        self.team_generator = team_generator
        if self.config.settings.simulation_type == "basic-stress-test":
            self.config.settings.teams = 1
        self.helpers = {
            SetupVariant.AZURE: AzureSetupHelper(self.config, self.secrets),
            SetupVariant.HETZNER: HetznerSetupHelper(self.config, self.secrets),
            SetupVariant.LOCAL: LocalSetupHelper(self.config, self.secrets),
        }

    def generate_teams(self) -> Tuple[List, Dict]:
        return self.team_generator.generate()

    async def convert_templates(self) -> None:
        helper = self.helpers[SetupVariant.from_str(self.config.setup.location)]
        await helper.convert_buildscript()
        await helper.convert_deploy_script()
        await helper.convert_tf_files()
        await helper.convert_vm_scripts()

    async def get_ip_addresses(self) -> Tuple[Dict, Dict]:
        helper = self.helpers[SetupVariant.from_str(self.config.setup.location)]
        return await helper.get_ip_addresses()
