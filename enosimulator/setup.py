import json


def _parse_config(config_path):
    with open(config_path, "r") as json_config:
        data = json_config.read()
    return json.loads(data)


class Setup:
    def __init__(self):
        self.ips = dict()
        self.teams = dict()
        self.services = dict()
        self.setup_path = ""

    def configure(self, config_path):
        config = _parse_config(config_path)
        self.setup_path = f"../test-setup/{config['settings']['location']}"

        with open(f"{self.setup_path}/config/services.txt", "w") as service_file:
            for service in config["services"]:
                service_file.write(f"{service}\n")

    def build(self):
        pass

    def destroy(self):
        pass
