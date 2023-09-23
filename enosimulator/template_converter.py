import os
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
    def __init__(self, config):
        self.config = config
        self.setup_path = f"../test-setup/{config['setup']['location']}"

    def convert_buildscript(self):
        # Copy deploy.sh template for configuration
        _copy_file(
            f"{self.setup_path}/templates/build.sh",
            f"{self.setup_path}/build.sh",
        )
        # TODO:
        # - implement

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
        with open(f"{self.setup_path}/variables.tf", "r+") as variables_file:
            lines = variables_file.readlines()
            lines[2] = f"  default = {self.config['settings']['vulnboxes']}\n"
            variables_file.seek(0)
            variables_file.writelines(lines)
            variables_file.truncate()

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

        # TODO:
        # - we can also put the ssh public key path from secrets.json into main.tf

    def _convert_vm_scripts():
        pass
        # TODO:
        # - we can put the PAT from secrets.json into a working copy of checker.sh, engine.sh, vulnbox.sh


# TODO:
# - implement
class LocalTemplateConverter(Converter):
    def __init__(self, setup_path):
        self.setup_path = setup_path

    def convert_buildscript(self):
        pass

    def convert_deploy_script(self):
        pass

    def convert_tf_files(self):
        pass


class TemplateConverter:
    def __init__(self, config):
        self.config = config
        self.converters = {
            SetupVariant.AZURE: AzureTemplateConverter(config),
            SetupVariant.LOCAL: LocalTemplateConverter(config),
        }

    def convert_templates(self, setup_variant):
        converter = self.converters[
            SetupVariant.from_str(self.config["setup"]["location"])
        ]
        converter.convert_buildscript()
        converter.convert_deploy_script()
        converter.convert_tf_files()
