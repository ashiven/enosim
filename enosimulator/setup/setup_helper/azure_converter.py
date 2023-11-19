import os
import re
from typing import Dict, Tuple

import aiofiles
from types_ import Config, Secrets, VMType

from .base_converter import TemplateConverter
from .util import append_lines, copy_file, delete_lines, insert_after, replace_line


class AzureConverter(TemplateConverter):
    """
    A class that converts configuration template files for Azure.

    This includes terraform files for provisioning an infrastructure,
    a build script that is used to invoke the build process and generate an SSH config file,
    and configuration scripts that are used to configure the VMs.

    Attributes:
        config (Config): The configuration file provided by the user.
        secrets (Secrets): The secrets file provided by the user.
        setup_path (str): The path to the azure setup directory.
        use_vm_images (bool): Whether to use preconfigured VM images in the deployment.
    """

    def __init__(self, config: Config, secrets: Secrets):
        """Initialize the AzureConverter class."""

        self.config = config
        self.secrets = secrets
        dir_path = os.path.dirname(os.path.abspath(__file__))
        dir_path = dir_path.replace("\\", "/")
        self.setup_path = f"{dir_path}/../../infra/{config.setup.location}"
        self.use_vm_images = any(
            ref != "" for ref in self.config.setup.vm_image_references.values()
        )

    async def convert_buildscript(self) -> None:
        """Convert the template build script according to the configuration file."""

        # Copy build.sh template for configuration
        await copy_file(
            f"{self.setup_path}/templates/build.sh",
            f"{self.setup_path}/build.sh",
        )

        # Configure setup_path, ssh_config_path and ssh_private_key_path
        ABSOLUTE_SETUP_PATH_LINE = 4
        SSH_CONFIG_PATH_LINE = 5
        SSH_PRIVATE_KEY_PATH_LINE = 6
        await replace_line(
            f"{self.setup_path}/build.sh",
            ABSOLUTE_SETUP_PATH_LINE,
            f'setup_path="{os.path.abspath(self.setup_path)}"\n',
        )
        await replace_line(
            f"{self.setup_path}/build.sh",
            SSH_CONFIG_PATH_LINE,
            f'ssh_config="{self.config.setup.ssh_config_path}"\n',
        )
        await replace_line(
            f"{self.setup_path}/build.sh",
            SSH_PRIVATE_KEY_PATH_LINE,
            f'ssh_private_key_path="{self.secrets.vm_secrets.ssh_private_key_path}"\n',
        )

        # Configure ip address parsing
        lines = []
        for vulnbox_id in range(1, self.config.settings.teams + 1):
            lines.append(
                f'vulnbox{vulnbox_id}_ip=$(grep -oP "vulnbox{vulnbox_id}\\s*=\\s*\\K[^\\s]+" ./logs/ip_addresses.log | sed \'s/"//g\')\n'
            )
        await insert_after(f"{self.setup_path}/build.sh", "engine_ip=", lines)

        # Configure writing ssh config
        lines = []
        for vulnbox_id in range(1, self.config.settings.teams + 1):
            lines.append(
                f'echo -e "Host vulnbox{vulnbox_id}\\nUser groot\\nHostName ${{vulnbox{vulnbox_id}_ip}}\\nIdentityFile ${{ssh_private_key_path}}\\nStrictHostKeyChecking no\\nLocalForward 1337 ${{engine_private_ip}}:1337\\n" >>${{ssh_config}}\n'
            )
        await insert_after(f"{self.setup_path}/build.sh", 'echo -e "Host engine', lines)

    async def convert_configure_script(self) -> None:
        """Convert the configure script according to the configuration file."""

        # Copy configure.sh template for configuration
        await copy_file(
            f"{self.setup_path}/templates/configure.sh",
            f"{self.setup_path}/configure.sh",
        )

        # Configure setup_path, ssh_config_path
        ABSOLUTE_SETUP_PATH_LINE = 4
        SSH_CONFIG_PATH_LINE = 5
        await replace_line(
            f"{self.setup_path}/configure.sh",
            ABSOLUTE_SETUP_PATH_LINE,
            f'setup_path="{os.path.abspath(self.setup_path)}"\n',
        )
        await replace_line(
            f"{self.setup_path}/configure.sh",
            SSH_CONFIG_PATH_LINE,
            f'ssh_config="{self.config.setup.ssh_config_path}"\n',
        )

        # Vulnbox configuration
        lines = []
        for vulnbox_id in range(1, self.config.settings.teams + 1):
            lines.append(
                f'\necho -e "\\n\\033[32m[+] Configuring vulnbox{vulnbox_id} ...\\033[0m"\n'
            )
            lines.append(
                f"retry scp -F ${{ssh_config}} ./data/vulnbox.sh vulnbox{vulnbox_id}:/home/groot/vulnbox.sh\n"
            )
            lines.append(
                f"retry scp -F ${{ssh_config}} ./config/services.txt vulnbox{vulnbox_id}:/home/groot/services.txt\n"
            )
            lines.append(
                f'retry ssh -F ${{ssh_config}} vulnbox{vulnbox_id} "chmod +x vulnbox.sh && ./vulnbox.sh" > ./logs/vulnbox{vulnbox_id}_config.log 2>&1 &\n'
            )
        await insert_after(
            f"{self.setup_path}/configure.sh",
            "retry ssh -F ${ssh_config} checker",
            lines,
        )

    async def convert_tf_files(self) -> None:
        """Convert the terraform files according to the configuration file."""

        # Copy terraform file templates for configuration
        await copy_file(
            f"{self.setup_path}/templates/versions.tf",
            f"{self.setup_path}/versions.tf",
        )
        await copy_file(
            f"{self.setup_path}/templates/main.tf",
            f"{self.setup_path}/main.tf",
        )
        await copy_file(
            f"{self.setup_path}/templates/variables.tf",
            f"{self.setup_path}/variables.tf",
        )
        await copy_file(
            f"{self.setup_path}/templates/outputs.tf",
            f"{self.setup_path}/outputs.tf",
        )

        # Add service principal credentials to versions.tf
        TF_SUBSCRIPTION_ID_LINE = 11
        TF_CLIENT_ID_LINE = 12
        TF_CLIENT_SECRET_LINE = 13
        TF_TENANT_ID_LINE = 14
        await replace_line(
            f"{self.setup_path}/versions.tf",
            TF_SUBSCRIPTION_ID_LINE,
            f"  subscription_id = \"{self.secrets.cloud_secrets.azure_service_principal['subscription-id']}\"\n",
        )
        await replace_line(
            f"{self.setup_path}/versions.tf",
            TF_CLIENT_ID_LINE,
            f"  client_id       = \"{self.secrets.cloud_secrets.azure_service_principal['client-id']}\"\n",
        )
        await replace_line(
            f"{self.setup_path}/versions.tf",
            TF_CLIENT_SECRET_LINE,
            f"  client_secret   = \"{self.secrets.cloud_secrets.azure_service_principal['client-secret']}\"\n",
        )
        await replace_line(
            f"{self.setup_path}/versions.tf",
            TF_TENANT_ID_LINE,
            f"  tenant_id       = \"{self.secrets.cloud_secrets.azure_service_principal['tenant-id']}\"\n",
        )

        # Configure ssh key path in main.tf
        TF_LINE_SSH_KEY_PATH = 60
        await replace_line(
            f"{self.setup_path}/main.tf",
            TF_LINE_SSH_KEY_PATH,
            f'    public_key = file("{self.secrets.vm_secrets.ssh_public_key_path}")\n',
        )

        # Configure vm image references in main.tf
        TF_LINE_SOURCE_IMAGE = 68
        if self.use_vm_images:
            await replace_line(
                f"{self.setup_path}/main.tf",
                TF_LINE_SOURCE_IMAGE,
                "  source_image_id = each.value.source_image_id\n",
            )
            await delete_lines(
                f"{self.setup_path}/main.tf",
                [
                    line
                    for line in range(
                        TF_LINE_SOURCE_IMAGE + 1, TF_LINE_SOURCE_IMAGE + 6
                    )
                ],
            )

        # Configure vulnbox count in variables.tf
        TF_LINE_COUNT = 2
        await replace_line(
            f"{self.setup_path}/variables.tf",
            TF_LINE_COUNT,
            f"  default = {self.config.settings.teams}\n",
        )

        # Configure vm image references in variables.tf
        sub_id = self.secrets.cloud_secrets.azure_service_principal["subscription-id"]
        basepath = f"/subscriptions/{sub_id}/resourceGroups/vm-images/providers/Microsoft.Compute/images"
        await insert_after(
            f"{self.setup_path}/variables.tf",
            "    name = string",
            "    subnet_id = number\n"
            + "    size = string\n"
            + "    source_image_id = string\n"
            if self.use_vm_images
            else "",
        )
        await insert_after(
            f"{self.setup_path}/variables.tf",
            '      name = "engine"',
            f"      subnet_id = {self.config.settings.teams + 2}\n"
            + f'      size = "{self.config.setup.vm_sizes[VMType.ENGINE.value]}"\n'
            + f'      source_image_id = "{basepath}/{self.config.setup.vm_image_references[VMType.ENGINE.value]}"\n'
            if self.use_vm_images
            else "",
        )
        await insert_after(
            f"{self.setup_path}/variables.tf",
            '      name = "checker"',
            f"      subnet_id = {self.config.settings.teams + 1}\n"
            + f'      size = "{self.config.setup.vm_sizes[VMType.CHECKER.value]}"\n'
            + f'      source_image_id = "{basepath}/{self.config.setup.vm_image_references[VMType.CHECKER.value]}"\n'
            if self.use_vm_images
            else "",
        )
        await insert_after(
            f"{self.setup_path}/variables.tf",
            '        name = "vulnbox${vulnbox_id}"',
            f"        subnet_id = vulnbox_id\n"
            + f'        size = "{self.config.setup.vm_sizes[VMType.VULNBOX.value]}"\n'
            + f'        source_image_id = "{basepath}/{self.config.setup.vm_image_references[VMType.VULNBOX.value]}"\n'
            if self.use_vm_images
            else "",
        )

        # Add terraform outputs for private and public ip addresses
        lines = []
        for vulnbox_id in range(1, self.config.settings.teams + 1):
            lines.append(
                f'output "vulnbox{vulnbox_id}" {{\n  value = azurerm_public_ip.vm_pip["vulnbox{vulnbox_id}"].ip_address\n}}\n'
            )
        await append_lines(f"{self.setup_path}/outputs.tf", lines)

    async def convert_vm_scripts(self) -> None:
        """Convert the vm configuration scripts according to the configuration file."""

        # Copy vm script templates for configuration
        await copy_file(
            f"{self.setup_path}/templates/data/vulnbox.sh",
            f"{self.setup_path}/data/vulnbox.sh",
        )
        await copy_file(
            f"{self.setup_path}/templates/data/checker.sh",
            f"{self.setup_path}/data/checker.sh",
        )
        await copy_file(
            f"{self.setup_path}/templates/data/engine.sh",
            f"{self.setup_path}/data/engine.sh",
        )
        await copy_file(
            f"{self.setup_path}/templates/data/docker-compose.yml",
            f"{self.setup_path}/data/docker-compose.yml",
        )

        # Configure github personal access token
        PAT_LINE = 22
        PAT_LINE_ENGINE = 28
        await replace_line(
            f"{self.setup_path}/data/vulnbox.sh",
            PAT_LINE,
            f'pat="{self.secrets.vm_secrets.github_personal_access_token}"\n',
        )
        await replace_line(
            f"{self.setup_path}/data/checker.sh",
            PAT_LINE,
            f'pat="{self.secrets.vm_secrets.github_personal_access_token}"\n',
        )
        await replace_line(
            f"{self.setup_path}/data/engine.sh",
            PAT_LINE_ENGINE,
            f'pat="{self.secrets.vm_secrets.github_personal_access_token}"\n',
        )

        # Omit configuration when using vm images
        VULNBOX_CHECKER_CONFIG_LINES_START = 4
        VULNBOX_CHECKER_CONFIG_LINES_END = 21
        ENGINE_CONFIG_LINES_START = 4
        ENGINE_CONFIG_LINES_END = 27
        if self.use_vm_images:
            await delete_lines(
                f"{self.setup_path}/data/vulnbox.sh",
                [
                    line
                    for line in range(
                        VULNBOX_CHECKER_CONFIG_LINES_START,
                        VULNBOX_CHECKER_CONFIG_LINES_END + 1,
                    )
                ],
            )
            await delete_lines(
                f"{self.setup_path}/data/checker.sh",
                [
                    line
                    for line in range(
                        VULNBOX_CHECKER_CONFIG_LINES_START,
                        VULNBOX_CHECKER_CONFIG_LINES_END + 1,
                    )
                ],
            )
            await delete_lines(
                f"{self.setup_path}/data/engine.sh",
                [
                    line
                    for line in range(
                        ENGINE_CONFIG_LINES_START, ENGINE_CONFIG_LINES_END + 1
                    )
                ],
            )

    async def get_ip_addresses(self) -> Tuple[Dict, Dict]:
        """
        Parse ip addresses from ip_addresses.log after the infrastructure has been
        provisioned.

        Returns:
            ip_addresses (Dict): A dictionary containing all public ip addresses in the infrastructure.
            private_ip_addresses (Dict): A dictionary containing all private ip addresses in the infrastructure.
        """

        # Parse ip addresses from ip_addresses.log
        ip_addresses = dict()
        async with aiofiles.open(
            f"{self.setup_path}/logs/ip_addresses.log",
            "r",
        ) as ip_file:
            lines = await ip_file.readlines()
            pattern = r"(\w+)\s*=\s*(.+)"
            for index, line in enumerate(lines):
                m = re.match(pattern, line)
                if m:
                    key = m.group(1)
                    value = m.group(2).strip().replace('"', "")
                    if key == "private_ip_addresses":
                        while "}" not in value:
                            line = lines.pop(index + 1)
                            value += line.strip().replace("=", ":") + ", "
                        value = value[:-2]
                        private_ip_addresses = eval(value)
                    else:
                        ip_addresses[key] = value
        return ip_addresses, private_ip_addresses
