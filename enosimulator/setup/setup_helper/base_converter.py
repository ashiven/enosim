from abc import ABC, abstractmethod
from typing import Dict, Tuple


class TemplateConverter(ABC):
    """Abstract base class for template converters."""

    @abstractmethod
    async def convert_buildscript(self) -> None:
        """A method to convert the build script template."""

        pass

    @abstractmethod
    async def convert_configure_script(self) -> None:
        """A method to convert the configure script template."""

        pass

    @abstractmethod
    async def convert_tf_files(self) -> None:
        """A method to convert the terraform files."""

        pass

    @abstractmethod
    async def convert_vm_scripts(self) -> None:
        """A method to convert the vm configuration scripts."""

        pass

    @abstractmethod
    async def get_ip_addresses(self) -> Tuple[Dict, Dict]:
        """A method to get the ip addresses of the VMs."""

        pass
