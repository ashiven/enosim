import os
from typing import Dict, Tuple

from types_ import Config, Secrets

from .base_converter import TemplateConverter


# TODO:
# - implement
class LocalConverter(TemplateConverter):
    """
    A class that converts configuration template files for a local setup.

    This includes terraform files for provisioning an infrastructure,
    a build script that is used to invoke the build process and generate an SSH config file,
    and configuration scripts that are used to configure the VMs.

    Attributes:
        config (Config): The configuration file provided by the user.
        secrets (Secrets): The secrets file provided by the user.
        setup_path (str): The path to the azure setup directory.
        use_vm_images (bool): Whether to use preconfigured VM images in the deployment.
    """ """"""

    def __init__(self, config: Config, secrets: Secrets):
        """Initialize the LocalConverter class."""

        self.config = config
        self.secrets = secrets
        dir_path = os.path.dirname(os.path.abspath(__file__))
        dir_path = dir_path.replace("\\", "/")
        self.setup_path = f"{dir_path}/../../infra/{config.setup.location}"
        self.use_vm_images = any(
            ref != "" for ref in self.config.setup.vm_image_references.values()
        )

    def convert_buildscript(self) -> None:
        """Convert the template build script according to the configuration file."""

        pass

    def convert_configure_script(self) -> None:
        """Convert the configure script according to the configuration file."""

        pass

    def convert_tf_files(self) -> None:
        """Convert the terraform files according to the configuration file."""

        pass

    def convert_vm_scripts(self) -> None:
        """Convert the vm configuration scripts according to the configuration file."""

        pass

    def get_ip_addresses(self) -> Tuple[Dict, Dict]:
        """
        Parse ip addresses from ip_addresses.log after the infrastructure has been
        provisioned.

        Returns:
            ip_addresses (Dict): A dictionary containing all public ip addresses in the infrastructure.
            private_ip_addresses (Dict): A dictionary containing all private ip addresses in the infrastructure.
        """

        pass
