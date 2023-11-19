import os
from typing import Dict, Tuple

import aiofiles
from types_ import Config, Secrets, VMType

from .base_converter import TemplateConverter
from .util import append_lines, copy_file, delete_lines, insert_after, replace_line


class HetznerConverter(TemplateConverter):
    """
    A class that converts configuration template files for Hetzner Cloud.

    This includes terraform files for provisioning the infrastructure,
    a build script that is used to invoke the build process and generate an SSH config file,
    and configuration scripts that are used to configure the VMs.

    Attributes:
        config: The configuration file provided by the user.
        secrets: The secrets file provided by the user.
        setup_path: The path to the hetzner setup directory.
        use_vm_images: Whether to use preconfigured VM images in the deployment.
    """

    def __init__(self, config: Config, secrets: Secrets):
        """Initializes the HetznerConverter class."""

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

        # Insert engine private ip
        ENGINE_PRIVATE_IP_LINE = 21
        await replace_line(
            f"{self.setup_path}/build.sh",
            ENGINE_PRIVATE_IP_LINE,
            f'engine_private_ip="10.1.{self.config.settings.teams + 2}.1"\n',
        )

        # Configure ip address parsing
        lines = []
        for vulnbox_id in range(1, self.config.settings.teams + 1):
            lines.append(
                f"vulnbox{vulnbox_id}_ip=$(grep -oP '\"vulnbox{vulnbox_id}\"\\s*=\\s*\\K[^\\s]+' ./logs/ip_addresses.log | sed 's/\"//g')\n"
            )
        await insert_after(f"{self.setup_path}/build.sh", "engine_ip=", lines)

        # Configure writing ssh config
        lines = []
        for vulnbox_id in range(1, self.config.settings.teams + 1):
            lines.append(
                f'echo -e "Host vulnbox{vulnbox_id}\\nUser root\\nHostName ${{vulnbox{vulnbox_id}_ip}}\\nIdentityFile ${{ssh_private_key_path}}\\nStrictHostKeyChecking no\\nLocalForward 1337 ${{engine_private_ip}}:1337\\n" >>${{ssh_config}}\n'
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
                f"retry scp -F ${{ssh_config}} ./data/vulnbox.sh vulnbox{vulnbox_id}:/root/vulnbox.sh\n"
            )
            lines.append(
                f"retry scp -F ${{ssh_config}} ./config/services.txt vulnbox{vulnbox_id}:/root/services.txt\n"
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

        # Add hetzner api token to versions.tf
        TF_LINE_HETZNER_API_TOKEN = 10
        await replace_line(
            f"{self.setup_path}/versions.tf",
            TF_LINE_HETZNER_API_TOKEN,
            f'  token = "{self.secrets.cloud_secrets.hetzner_api_token}"\n',
        )

        # Configure ssh key path in main.tf
        TF_LINE_SSH_KEY_PATH = 2
        await replace_line(
            f"{self.setup_path}/main.tf",
            TF_LINE_SSH_KEY_PATH,
            f'  public_key = file("{self.secrets.vm_secrets.ssh_public_key_path}")\n',
        )

        # Add subnet resources to main.tf
        lines = []
        lines.append(
            f'resource "hcloud_network_subnet" "snet" {{\n'
            f"  count = {self.config.settings.teams + 2}\n"
            '  type = "cloud"\n'
            + "  network_id = hcloud_network.vnet.id\n"
            + '  network_zone = "eu-central"\n'
            + f'  ip_range = "10.1.${{count.index + 1}}.0/24"\n'
            + "}\n"
        )
        await insert_after(
            f"{self.setup_path}/main.tf", "############# Subnets #############", lines
        )

        # Add vm resources to main.tf
        lines = []
        lines.append(
            'resource "hcloud_server" "checker_vm" {\n'
            '  name = "checker"\n'
            + f'  server_type = "{self.config.setup.vm_sizes[VMType.CHECKER.value]}"\n'
            + '  image = "ubuntu-20.04"\n'
            + '  location = "nbg1"\n'
            + "  ssh_keys = [\n  hcloud_ssh_key.ssh_key.id\n  ]\n"
            + f'  network {{\n    network_id = hcloud_network.vnet.id\n    ip = "10.1.{self.config.settings.teams + 1}.1"\n  }}\n'
            + "  public_net {\n    ipv4_enabled = true\n    ipv6_enabled = false\n  }\n"
            + f"  depends_on = [\n    hcloud_network_subnet.snet\n  ]\n"
            + "}\n"
        )
        lines.append(
            'resource "hcloud_server" "engine_vm" {\n'
            '  name = "engine"\n'
            + f'  server_type = "{self.config.setup.vm_sizes[VMType.ENGINE.value]}"\n'
            + '  image = "ubuntu-20.04"\n'
            + '  location = "nbg1"\n'
            + "  ssh_keys = [\n  hcloud_ssh_key.ssh_key.id\n  ]\n"
            + f'  network {{\n    network_id = hcloud_network.vnet.id\n    ip = "10.1.{self.config.settings.teams + 2}.1"\n  }}\n'
            + "  public_net {\n    ipv4_enabled = true\n    ipv6_enabled = false\n  }\n"
            + f"  depends_on = [\n    hcloud_network_subnet.snet\n  ]\n"
            + "}\n"
        )
        lines.append(
            'resource "hcloud_server" "vulnbox_vm" {\n'
            f"  count = {self.config.settings.teams}\n"
            f'  name = "vulnbox${{count.index + 1}}"\n'
            + f'  server_type = "{self.config.setup.vm_sizes[VMType.VULNBOX.value]}"\n'
            + '  image = "ubuntu-20.04"\n'
            + '  location = "nbg1"\n'
            + "  ssh_keys = [\n  hcloud_ssh_key.ssh_key.id\n  ]\n"
            + f'  network {{\n    network_id = hcloud_network.vnet.id\n    ip = "10.1.${{count.index + 1}}.1"\n  }}\n'
            + "  public_net {\n    ipv4_enabled = true\n    ipv6_enabled = false\n  }\n"
            + f"  depends_on = [\n    hcloud_network_subnet.snet\n  ]\n"
            + "}\n"
        )
        await insert_after(
            f"{self.setup_path}/main.tf", "############# VMs #############", lines
        )

        # Include vm image references in variables.tf
        if self.use_vm_images:
            lines = []
            lines.append(
                'data "hcloud_image" "engine" {\n'
                + f'  with_selector = "name={self.config.setup.vm_image_references[VMType.ENGINE.value]}"\n'
                + "}\n"
            )
            lines.append(
                'data "hcloud_image" "checker" {\n'
                + f'  with_selector = "name={self.config.setup.vm_image_references[VMType.CHECKER.value]}"\n'
                + "}\n"
            )
            lines.append(
                'data "hcloud_image" "vulnbox" {\n'
                + f'  with_selector = "name={self.config.setup.vm_image_references[VMType.VULNBOX.value]}"\n'
                + "}\n"
            )
            await append_lines(f"{self.setup_path}/variables.tf", lines)

            # Configure vm image references in main.tf
            TF_LINE_CHECKER_IMAGE = 23
            TF_LINE_ENGINE_IMAGE = 43
            TF_LINE_VULNBOX_IMAGE = 64
            await replace_line(
                f"{self.setup_path}/main.tf",
                TF_LINE_CHECKER_IMAGE,
                "  image = data.hcloud_image.checker.id\n",
            )
            await replace_line(
                f"{self.setup_path}/main.tf",
                TF_LINE_ENGINE_IMAGE,
                "  image = data.hcloud_image.engine.id\n",
            )
            await replace_line(
                f"{self.setup_path}/main.tf",
                TF_LINE_VULNBOX_IMAGE,
                "  image = data.hcloud_image.vulnbox.id\n",
            )

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

        # Parse public ip addresses from ip_addresses.log
        ip_addresses = dict()
        async with aiofiles.open(
            f"{self.setup_path}/logs/ip_addresses.log",
            "r",
        ) as ip_file:
            lines = await ip_file.readlines()
            for line in lines:
                if line.startswith("vulnbox") or line.startswith("}"):
                    continue
                parts = line.split("=")
                key = parts[0].strip().replace('"', "")
                value = parts[1].strip().replace('"', "")
                ip_addresses[key] = value

        # Set private ip addresses
        private_ip_addresses = dict()
        for vulnbox_id in range(1, self.config.settings.teams + 1):
            private_ip_addresses[f"vulnbox{vulnbox_id}"] = f"10.1.{vulnbox_id}.1"
        private_ip_addresses[
            VMType.CHECKER.value
        ] = f"10.1.{self.config.settings.teams + 1}.1"
        private_ip_addresses[
            VMType.ENGINE.value
        ] = f"10.1.{self.config.settings.teams + 2}.1"

        return ip_addresses, private_ip_addresses
