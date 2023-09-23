import os
from abc import ABC, abstractmethod
from enum import Enum
from hmac import new

from matplotlib import lines


class SetupVariant(Enum):
    AZURE = "azure"
    LOCAL = "local"

    @staticmethod
    def from_str(s):
        if s == "azure":
            return SetupVariant.AZURE
        elif s == "local":
            return SetupVariant.LOCAL
        else:
            raise NotImplementedError


####  Helpers ####


def _copy_file(src, dst):
    if os.path.exists(src):
        with open(src, "rb") as src_file:
            with open(dst, "wb") as dst_file:
                dst_file.write(src_file.read())


def _replace_line(path, line_number, new_line):
    with open(path, "rb+") as file:
        lines = file.readlines()
        lines[line_number] = new_line.encode("utf-8")
        file.seek(0)
        file.writelines(lines)
        file.truncate()


def _insert_after(path, after, insert_lines):
    new_lines = []
    with open(path, "rb") as file:
        lines = file.readlines()
        for line in lines:
            new_lines.append(line)
            if line.startswith(after.encode("utf-8")):
                for insert_line in insert_lines:
                    new_lines.append(insert_line.encode("utf-8"))
    with open(path, "wb") as file:
        file.writelines(new_lines)


#### End Helpers ####


class Converter(ABC):
    @abstractmethod
    def convert_buildscript(self):
        pass

    @abstractmethod
    def convert_deploy_script(self):
        pass

    @abstractmethod
    def convert_tf_files(self):
        pass

    @abstractmethod
    def convert_vm_scripts(self):
        pass


class AzureTemplateConverter(Converter):
    def __init__(self, config, secrets):
        self.config = config
        self.secrets = secrets
        self.setup_path = f"../test-setup/{config['setup']['location']}"

    def convert_buildscript(self):
        # Copy build.sh template for configuration
        _copy_file(
            f"{self.setup_path}/templates/build.sh",
            f"{self.setup_path}/build.sh",
        )

        # Configure setup_path, ssh_config_path and ssh_private_key_path
        ABSOLUTE_SETUP_PATH_LINE = 4
        SSH_CONFIG_PATH_LINE = 5
        SSH_PRIVATE_KEY_PATH_LINE = 6
        _replace_line(
            f"{self.setup_path}/build.sh",
            ABSOLUTE_SETUP_PATH_LINE,
            f'setup_path="{os.path.abspath(self.setup_path)}"\n',
        )
        _replace_line(
            f"{self.setup_path}/build.sh",
            SSH_CONFIG_PATH_LINE,
            f"ssh_config=\"{self.config['setup']['ssh-config-path']}\"\n",
        )
        _replace_line(
            f"{self.setup_path}/build.sh",
            SSH_PRIVATE_KEY_PATH_LINE,
            f"ssh_private_key_path=\"{self.secrets['vm-secrets']['ssh-private-key-path']}\"\n",
        )

        # Configure ip address parsing
        lines = []
        for vulnbox_id in range(1, self.config["settings"]["vulnboxes"] + 1):
            lines.append(
                f'vulnbox{vulnbox_id}_ip=$(grep -oP "vulnbox{vulnbox_id}_ip\s*=\s*\K[^\s]+" ./logs/ip_addresses.log)\n'
            )
        _insert_after(f"{self.setup_path}/build.sh", "engine_ip=", lines)

        # Configure writing ssh config
        lines = []
        for vulnbox_id in range(1, self.config["settings"]["vulnboxes"] + 1):
            lines.append(
                f'echo -e "Host vulnbox{vulnbox_id}\\nUser groot\\nHostName ${{vulnbox{vulnbox_id}_ip}}\\nIdentityFile ${{ssh_private_key_path}}\\nStrictHostKeyChecking no\\n" >>${{ssh_config}}\n'
            )
        _insert_after(f"{self.setup_path}/build.sh", 'echo -e "Host engine', lines)

    def convert_deploy_script(self):
        # Copy deploy.sh template for configuration
        _copy_file(
            f"{self.setup_path}/templates/deploy.sh",
            f"{self.setup_path}/deploy.sh",
        )
        # TODO:
        # - implement

    def convert_tf_files(self):
        # Copy terraform file templates for configuration
        _copy_file(
            f"{self.setup_path}/templates/versions.tf",
            f"{self.setup_path}/versions.tf",
        )
        _copy_file(
            f"{self.setup_path}/templates/main.tf",
            f"{self.setup_path}/main.tf",
        )
        _copy_file(
            f"{self.setup_path}/templates/variables.tf",
            f"{self.setup_path}/variables.tf",
        )
        _copy_file(
            f"{self.setup_path}/templates/outputs.tf",
            f"{self.setup_path}/outputs.tf",
        )

        # Configure vulnbox count in variables.tf
        TF_LINE_COUNT = 2
        _replace_line(
            f"{self.setup_path}/variables.tf",
            TF_LINE_COUNT,
            f"  default = {self.config['settings']['vulnboxes']}\n",
        )

        # Add terraform outputs for private and public ip addresses
        with open(
            f"{self.setup_path}/outputs.tf",
            "w",
        ) as outputs_file:
            outputs_file.write(
                f'output "private_ip_addresses" {{\n  value = [for _, nic in azurerm_network_interface.vm_nic : nic.ip_configuration[0].private_ip_address]\n}}\n'
            )
            outputs_file.write(
                f'output "checker_ip" {{\n  value = azurerm_public_ip.vm_pip["checker"]._ip_address\n}}\n'
            )
            outputs_file.write(
                f'output "engine_ip" {{\n  value = azurerm_public_ip.vm_pip["engine"]._ip_address\n}}\n'
            )
            for vulnbox_id in range(1, self.config["settings"]["vulnboxes"] + 1):
                outputs_file.write(
                    f'output "vulnbox{vulnbox_id}_ip" {{\n  value = azurerm_public_ip.vm_pip["vulnbox{vulnbox_id}"]._ip_address\n}}\n'
                )

        # Configure ssh key path in main.tf
        TF_LINE_SSH_KEY_PATH = 67
        _replace_line(
            f"{self.setup_path}/main.tf",
            TF_LINE_SSH_KEY_PATH,
            f"   public_key = file(\"{self.secrets['vm-secrets']['ssh-public-key-path']}\")\n",
        )

    def convert_vm_scripts(self):
        # Copy vm script templates for configuration
        _copy_file(
            f"{self.setup_path}/templates/data/vulnbox.sh",
            f"{self.setup_path}/data/vulnbox.sh",
        )
        _copy_file(
            f"{self.setup_path}/templates/data/checker.sh",
            f"{self.setup_path}/data/checker.sh",
        )
        _copy_file(
            f"{self.setup_path}/templates/data/engine.sh",
            f"{self.setup_path}/data/engine.sh",
        )
        PAT_LINE = 4
        _replace_line(
            f"{self.setup_path}/data/vulnbox.sh",
            PAT_LINE,
            f"pat=\"{self.secrets['vm-secrets']['github-personal-access-token']}\"\n",
        )
        _replace_line(
            f"{self.setup_path}/data/checker.sh",
            PAT_LINE,
            f"pat=\"{self.secrets['vm-secrets']['github-personal-access-token']}\"\n",
        )
        _replace_line(
            f"{self.setup_path}/data/engine.sh",
            PAT_LINE,
            f"pat=\"{self.secrets['vm-secrets']['github-personal-access-token']}\"\n",
        )


# TODO:
# - implement
class LocalTemplateConverter(Converter):
    def __init__(self, config, secrets):
        self.config = config
        self.secrets = secrets
        self.setup_path = f"../test-setup/{config['setup']['location']}"

    def convert_buildscript(self):
        pass

    def convert_deploy_script(self):
        pass

    def convert_tf_files(self):
        pass

    def convert_vm_scripts(self):
        pass


class TemplateConverter:
    def __init__(self, config, secrets):
        self.config = config
        self.secrets = secrets
        self.converters = {
            SetupVariant.AZURE: AzureTemplateConverter(config, secrets),
            SetupVariant.LOCAL: LocalTemplateConverter(config, secrets),
        }

    def convert_templates(self):
        converter = self.converters[
            SetupVariant.from_str(self.config["setup"]["location"])
        ]
        converter.convert_buildscript()
        converter.convert_deploy_script()
        converter.convert_tf_files()
        converter.convert_vm_scripts()
