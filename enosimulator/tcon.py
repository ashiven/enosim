import os
import re
from abc import ABC, abstractmethod
from enum import Enum


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
        lines[line_number] = new_line.replace("\\", "/").encode("utf-8")
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


class Helper(ABC):
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

    @abstractmethod
    def get_ip_addresses(self):
        pass


class AzureSetupHelper(Helper):
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

        # Configure setup_path, ssh_config_path
        ABSOLUTE_SETUP_PATH_LINE = 4
        SSH_CONFIG_PATH_LINE = 5
        _replace_line(
            f"{self.setup_path}/deploy.sh",
            ABSOLUTE_SETUP_PATH_LINE,
            f'setup_path="{os.path.abspath(self.setup_path)}"\n',
        )
        _replace_line(
            f"{self.setup_path}/deploy.sh",
            SSH_CONFIG_PATH_LINE,
            f"ssh_config=\"{self.config['setup']['ssh-config-path']}\"\n",
        )

        # Configure ip vulnbox deployments
        lines = []
        for vulnbox_id in range(1, self.config["settings"]["vulnboxes"] + 1):
            lines.append(f'\necho "[+] Configuring vulnbox{vulnbox_id} ..."\n')
            lines.append(
                f"retry scp -F ${{ssh_config}} ./data/vulnbox.sh vulnbox{vulnbox_id}:/home/groot/vulnbox.sh\n"
            )
            lines.append(
                f"retry scp -F ${{ssh_config}} ./data/services.txt vulnbox{vulnbox_id}:/home/groot/services.txt\n"
            )
            lines.append(
                f'echo "[!] This will take a few minutes. Please be patient."\n'
            )
            lines.append(
                f'retry ssh -F ${{ssh_config}} vulnbox{vulnbox_id} "chmod +x vulnbox.sh && ./vulnbox.sh" >./logs/vulnbox{vulnbox_id}_config.log 2>&1\n'
            )
        _insert_after(
            f"{self.setup_path}/deploy.sh", "retry ssh -F ${ssh_config} checker", lines
        )

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

    def get_ip_addresses(self):
        # Parse ip addresses from ip_addresses.log
        ip_addresses = dict()
        with open(
            f"{self.setup_path}/logs/ip_addresses.log",
            "r",
        ) as ip_file:
            lines = ip_file.readlines()
            pattern = r"(\w+)\s*=\s*(.+)"
            for index, line in enumerate(lines):
                m = re.match(pattern, line)
                if m:
                    key = m.group(1)
                    value = m.group(2).strip().replace('"', "")
                    if key == "private_ip_addresses":
                        while "]" not in value:
                            line = lines.pop(index + 1)
                            value += line.strip()
                        private_ip_addresses = eval(value)
                        ip_addresses["private_ip_addresses"] = private_ip_addresses
                    else:
                        ip_addresses[key] = value
        return ip_addresses


# TODO:
# - implement
class LocalSetupHelper(Helper):
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

    def get_ip_addresses(self):
        pass


class SetupHelper:
    def __init__(self, config, secrets):
        self.config = config
        self.secrets = secrets
        self.helpers = {
            SetupVariant.AZURE: AzureSetupHelper(config, secrets),
            SetupVariant.LOCAL: LocalSetupHelper(config, secrets),
        }

    def convert_templates(self):
        helper = self.helpers[SetupVariant.from_str(self.config["setup"]["location"])]
        helper.convert_buildscript()
        helper.convert_deploy_script()
        helper.convert_tf_files()
        helper.convert_vm_scripts()

    def get_ip_addresses(self):
        helper = self.helpers[SetupVariant.from_str(self.config["setup"]["location"])]
        return helper.get_ip_addresses()
