import os

from types_ import Config, Secrets

from .abstract import Helper


# TODO:
# - implement
class LocalSetupHelper(Helper):
    def __init__(self, config: Config, secrets: Secrets):
        self.config = config
        self.secrets = secrets
        dir_path = os.path.dirname(os.path.abspath(__file__))
        dir_path = dir_path.replace("\\", "/")
        self.setup_path = f"{dir_path}/../../../test-setup/{config.setup.location}"
        self.use_vm_images = any(
            ref != "" for ref in self.config.setup.vm_image_references.values()
        )

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
