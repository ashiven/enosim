from typing import Dict, List, Tuple

from types_ import Config, Secrets, SetupVariant, SimulationType

from .azure_converter import AzureConverter
from .hetzner_converter import HetznerConverter
from .local_converter import LocalConverter
from .team_generator import TeamGenerator


class SetupHelper:
    """
    A class that helps with the setup of the simulation.

    It is responsible for generating teams, converting templates, and getting ip addresses.

    Attributes:
        config (Config): The configuration file provided by the user.
        secrets (Secrets): The secrets file provided by the user.
        team_generator (TeamGenerator): A TeamGenerator object used to generate unique teams for the simulation.
        template_converters (Dict): A dictionary mapping setup variants to template converters.
    """

    def __init__(self, config: Config, secrets: Secrets, team_generator: TeamGenerator):
        """Initialize the SetupHelper class."""

        self.config = config
        self.secrets = secrets
        self.team_generator = team_generator
        if (
            self.config.settings.simulation_type
            == SimulationType.BASIC_STRESS_TEST.value
        ):
            self.config.settings.teams = 1
        self.template_converters = {
            SetupVariant.AZURE: AzureConverter(self.config, self.secrets),
            SetupVariant.HETZNER: HetznerConverter(self.config, self.secrets),
            SetupVariant.LOCAL: LocalConverter(self.config, self.secrets),
        }

    def generate_teams(self) -> Tuple[List, Dict]:
        """
        Generate teams for the simulation.

        Returns:
            A tuple containing:
                - A list of teams that will be used to generate a ctf.json file for the engine
                - A dictionary mapping team names to Team objects containing the team's information.
        """

        return self.team_generator.generate()

    async def convert_templates(self) -> None:
        """Convert the templates according to the chosen location."""

        converter = self.template_converters[
            SetupVariant.from_str(self.config.setup.location)
        ]
        await converter.convert_buildscript()
        await converter.convert_configure_script()
        await converter.convert_tf_files()
        await converter.convert_vm_scripts()

    async def get_ip_addresses(self) -> Tuple[Dict, Dict]:
        """
        Get ip addresses for each VM in the infrastructure.

        Returns:
            ip_addresses (Dict): A dictionary containing all public ip addresses in the infrastructure.
            private_ip_addresses (Dict): A dictionary containing all private ip addresses in the infrastructure.
        """

        converter = self.template_converters[
            SetupVariant.from_str(self.config.setup.location)
        ]
        return await converter.get_ip_addresses()
