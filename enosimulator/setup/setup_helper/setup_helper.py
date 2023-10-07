from ..types import SetupVariant
from .azure import AzureSetupHelper
from .hetzner import HetznerSetupHelper
from .local import LocalSetupHelper
from .util import TeamGenerator


class SetupHelper:
    def __init__(self, config, secrets):
        self.config = config
        self.secrets = secrets
        self.helpers = {
            SetupVariant.AZURE: AzureSetupHelper(config, secrets),
            SetupVariant.HETZNER: HetznerSetupHelper(config, secrets),
            SetupVariant.LOCAL: LocalSetupHelper(config, secrets),
        }
        self.team_gen = TeamGenerator(config)

    def generate_teams(self):
        return self.team_gen.generate()

    async def convert_templates(self):
        helper = self.helpers[SetupVariant.from_str(self.config.setup.location)]
        await helper.convert_buildscript()
        await helper.convert_deploy_script()
        await helper.convert_tf_files()
        await helper.convert_vm_scripts()

    async def get_ip_addresses(self):
        helper = self.helpers[SetupVariant.from_str(self.config.setup.location)]
        return await helper.get_ip_addresses()
