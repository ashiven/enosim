from abc import ABC, abstractmethod


class Helper(ABC):
    @abstractmethod
    async def convert_buildscript(self):
        pass

    @abstractmethod
    async def convert_deploy_script(self):
        pass

    @abstractmethod
    async def convert_tf_files(self):
        pass

    @abstractmethod
    async def convert_vm_scripts(self):
        pass

    @abstractmethod
    async def get_ip_addresses(self):
        pass
