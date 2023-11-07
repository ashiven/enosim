from abc import ABC, abstractmethod
from typing import Dict, Tuple


class TemplateConverter(ABC):
    @abstractmethod
    async def convert_buildscript(self) -> None:
        pass

    @abstractmethod
    async def convert_configure_script(self) -> None:
        pass

    @abstractmethod
    async def convert_tf_files(self) -> None:
        pass

    @abstractmethod
    async def convert_vm_scripts(self) -> None:
        pass

    @abstractmethod
    async def get_ip_addresses(self) -> Tuple[Dict, Dict]:
        pass
