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


def _append_lines(path, append_lines):
    with open(path, "ab") as file:
        for line in append_lines:
            file.write(line.encode("utf-8"))


def _delete_lines(path, delete_lines):
    new_lines = []
    with open(path, "rb") as file:
        lines = file.readlines()
        for index, line in enumerate(lines):
            if index not in delete_lines:
                new_lines.append(line)
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
        dir_path = os.path.dirname(os.path.abspath(__file__)).replace("\\", "/")
        self.setup_path = f"{dir_path}/../test-setup/{config['setup']['location']}"
        self.use_vm_images = False

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
                f'vulnbox{vulnbox_id}_ip=$(grep -oP "vulnbox{vulnbox_id}\s*=\s*\K[^\s]+" ./logs/ip_addresses.log)\n'
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

        # Configure vulnbox deployments
        lines = []
        for vulnbox_id in range(1, self.config["settings"]["vulnboxes"] + 1):
            lines.append(
                f'\necho -e "\\033[32m[+] Configuring vulnbox{vulnbox_id} ...\\033[0m"\n'
            )
            lines.append(
                f"retry scp -F ${{ssh_config}} ./data/vulnbox.sh vulnbox{vulnbox_id}:/home/groot/vulnbox.sh\n"
            )
            lines.append(
                f"retry scp -F ${{ssh_config}} ./data/services.txt vulnbox{vulnbox_id}:/home/groot/services.txt\n"
            )
            lines.append(
                f'echo -e "\\033[31m[!] This will take a few minutes. Please be patient.\\033[0m"\n'
            )
            lines.append(
                f'retry ssh -F ${{ssh_config}} vulnbox{vulnbox_id} "chmod +x vulnbox.sh && ./vulnbox.sh" | tee ./logs/vulnbox{vulnbox_id}_config.log 2>&1\n'
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

        # Add service principal credentials to versions.tf
        TF_SUBSCRIPTION_ID_LINE = 11
        TF_CLIENT_ID_LINE = 12
        TF_CLIENT_SECRET_LINE = 13
        TF_TENANT_ID_LINE = 14
        _replace_line(
            f"{self.setup_path}/versions.tf",
            TF_SUBSCRIPTION_ID_LINE,
            f"  subscription_id = \"{self.secrets['cloud-secrets']['azure-service-principal']['subscription-id']}\"\n",
        )
        _replace_line(
            f"{self.setup_path}/versions.tf",
            TF_CLIENT_ID_LINE,
            f"  client_id       = \"{self.secrets['cloud-secrets']['azure-service-principal']['client-id']}\"\n",
        )
        _replace_line(
            f"{self.setup_path}/versions.tf",
            TF_CLIENT_SECRET_LINE,
            f"  client_secret   = \"{self.secrets['cloud-secrets']['azure-service-principal']['client-secret']}\"\n",
        )
        _replace_line(
            f"{self.setup_path}/versions.tf",
            TF_TENANT_ID_LINE,
            f"  tenant_id       = \"{self.secrets['cloud-secrets']['azure-service-principal']['tenant-id']}\"\n",
        )

        # Configure ssh key path in main.tf
        TF_LINE_SSH_KEY_PATH = 61
        _replace_line(
            f"{self.setup_path}/main.tf",
            TF_LINE_SSH_KEY_PATH,
            f"    public_key = file(\"{self.secrets['vm-secrets']['ssh-public-key-path']}\")\n",
        )

        # Configure vm image references in main.tf
        TF_LINE_SOURCE_IMAGE = 69
        if any(
            ref != "<optional>"
            for ref in self.config["setup"]["vm-image-references"].values()
        ):
            self.use_vm_images = True
            _replace_line(
                f"{self.setup_path}/main.tf",
                TF_LINE_SOURCE_IMAGE,
                "  source_image_id = each.value.source_image_id\n",
            )
            _delete_lines(
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
        _replace_line(
            f"{self.setup_path}/variables.tf",
            TF_LINE_COUNT,
            f"  default = {self.config['settings']['vulnboxes']}\n",
        )

        # Configure vm image references in variables.tf
        if self.use_vm_images:
            sub_id = self.secrets["cloud-secrets"]["azure-service-principal"][
                "subscription-id"
            ]
            _insert_after(
                f"{self.setup_path}/variables.tf",
                "    name = string",
                f"    source_image_id = string\n",
            )
            _insert_after(
                f"{self.setup_path}/variables.tf",
                '      name = "engine"',
                f'      source_image_id = "{self.config["setup"]["vm-image-references"]["engine"].replace("<sub-id>", sub_id)}"\n',
            )
            _insert_after(
                f"{self.setup_path}/variables.tf",
                '      name = "checker"',
                f'      source_image_id = "{self.config["setup"]["vm-image-references"]["checker"].replace("<sub-id>", sub_id)}"\n',
            )
            _insert_after(
                f"{self.setup_path}/variables.tf",
                '        name = "vulnbox${vulnbox_id}"',
                f'        source_image_id = "{self.config["setup"]["vm-image-references"]["vulnbox"].replace("<sub-id>", sub_id)}"\n',
            )

        # Add terraform outputs for private and public ip addresses
        lines = []
        for vulnbox_id in range(1, self.config["settings"]["vulnboxes"] + 1):
            lines.append(
                f'output "vulnbox{vulnbox_id}" {{\n  value = azurerm_public_ip.vm_pip["vulnbox{vulnbox_id}"].ip_address\n}}\n'
            )
        _append_lines(f"{self.setup_path}/outputs.tf", lines)

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

        # Configure github personal access token
        PAT_LINE = 22
        PAT_LINE_ENGINE = 28
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
            PAT_LINE_ENGINE,
            f"pat=\"{self.secrets['vm-secrets']['github-personal-access-token']}\"\n",
        )

        # Omit configuration when using vm images
        VULNBOX_CHECKER_CONFIG_LINES_START = 4
        VULNBOX_CHECKER_CONFIG_LINES_END = 21
        ENGINE_CONFIG_LINES_START = 4
        ENGINE_CONFIG_LINES_END = 27
        if self.use_vm_images:
            _delete_lines(
                f"{self.setup_path}/data/vulnbox.sh",
                [
                    line
                    for line in range(
                        VULNBOX_CHECKER_CONFIG_LINES_START,
                        VULNBOX_CHECKER_CONFIG_LINES_END + 1,
                    )
                ],
            )
            _delete_lines(
                f"{self.setup_path}/data/checker.sh",
                [
                    line
                    for line in range(
                        VULNBOX_CHECKER_CONFIG_LINES_START,
                        VULNBOX_CHECKER_CONFIG_LINES_END + 1,
                    )
                ],
            )
            _delete_lines(
                f"{self.setup_path}/data/engine.sh",
                [
                    line
                    for line in range(
                        ENGINE_CONFIG_LINES_START, ENGINE_CONFIG_LINES_END + 1
                    )
                ],
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
                        while "}" not in value:
                            line = lines.pop(index + 1)
                            value += line.strip().replace("=", ":") + ", "
                        value = value[:-2]
                        private_ip_addresses = eval(value)
                    else:
                        ip_addresses[key] = value
        return ip_addresses, private_ip_addresses


# TODO:
# - implement
class LocalSetupHelper(Helper):
    def __init__(self, config, secrets):
        self.config = config
        self.secrets = secrets
        dir_path = os.path.dirname(os.path.abspath(__file__)).replace("\\", "/")
        self.setup_path = f"{dir_path}/../test-setup/{config['setup']['location']}"

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
