from typing import Dict, List, Tuple

from types_ import Config, Secrets, SetupVariant

from .azure_converter import AzureConverter
from .hetzner_converter import HetznerConverter
from .local_converter import LocalConverter
from .team_generator import TeamGenerator


class SetupHelper:
    def __init__(self, config: Config, secrets: Secrets, team_generator: TeamGenerator):
        self.config = config
        self.secrets = secrets
        self.team_generator = team_generator
        if self.config.settings.simulation_type == "basic-stress-test":
            self.config.settings.teams = 1
        self.template_converters = {
            SetupVariant.AZURE: AzureConverter(self.config, self.secrets),
            SetupVariant.HETZNER: HetznerConverter(self.config, self.secrets),
            SetupVariant.LOCAL: LocalConverter(self.config, self.secrets),
        }

    def generate_teams(self) -> Tuple[List, Dict]:
        return self.team_generator.generate()

    async def convert_templates(self) -> None:
        converter = self.template_converters[
            SetupVariant.from_str(self.config.setup.location)
        ]
        await converter.convert_buildscript()
        await converter.convert_deploy_script()
        await converter.convert_tf_files()
        await converter.convert_vm_scripts()

    async def get_ip_addresses(self) -> Tuple[Dict, Dict]:
        converter = self.template_converters[
            SetupVariant.from_str(self.config.setup.location)
        ]
        return await converter.get_ip_addresses()
