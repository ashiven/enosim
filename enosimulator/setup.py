import json


####  Helpers ####
def _parse_json(path):
    with open(path, "r") as json_file:
        return json.load(json_file)


#### End Helpers ####


class Setup:
    def __init__(self):
        self.ips = dict()
        self.teams = dict()
        self.services = dict()
        self.setup_path = ""

    def configure(self, config_path):
        config = _parse_json(config_path)
        self.setup_path = f"../test-setup/{config['settings']['location']}"

        with open(f"{self.setup_path}/config/services.txt", "w") as service_file:
            for service in config["settings"]["services"]:
                service_file.write(f"{service}\n")

        ctf_json = _parse_json(f"{self.setup_path}/config/ctf.json")
        for setting, value in config["ctf-json"].items():
            ctf_json[setting] = value

        with open(f"{self.setup_path}/config/ctf.json", "w") as ctf_file:
            json.dump(ctf_json, ctf_file, indent=4)

    def build(self):
        pass

    def destroy(self):
        pass
