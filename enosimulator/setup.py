import json
import subprocess
import sys


####  Helpers ####
def _parse_json(path):
    with open(path, "r") as json_file:
        return json.load(json_file)


def _run_bash_script(script_path, args):
    try:
        p_args = ["bash", script_path] + args

        p = subprocess.Popen(
            p_args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        for line in p.stdout:
            print(line)
            sys.stdout.flush()

        p.wait()
        if p.returncode != 0:
            print(f"process exited with return code: {p.returncode}")

    except subprocess.CalledProcessError as e:
        print(e)


def _generate_team(id):
    team_names = ["Kleinmanzama", "Grossmanzama", "Mittelmanzama"]
    new_team = {
        "id": id,
        "name": team_names[id - 1],
        "teamSubnet": "::ffff:10.0.2.0",
        "address": "<placeholder>",
    }
    return new_team


def _generate_service(id, service):
    new_service = {
        "id": id,
        "name": service,
        "flagsPerRoundMultiplier": 1,
        "noisesPerRoundMultiplier": 1,
        "havocsPerRoundMultiplier": 1,
        "weightFactor": 1,
        "checkers": [],
    }
    return new_service


#### End Helpers ####


class Setup:
    def __init__(self, verbose=False):
        self.ips = dict()
        self.teams = dict()
        self.services = dict()
        self.setup_path = ""
        self.verbose = verbose

    def configure(self, config_path):
        config = _parse_json(config_path)
        self.setup_path = f"../test-setup/{config['settings']['location']}"

        # Create services.txt from config.json
        with open(f"{self.setup_path}/config/services.txt", "r+") as service_file:
            for service in config["settings"]["services"]:
                service_file.write(f"{service}\n")
            if self.verbose:
                print("[+] Created services.txt")
                service_file.seek(0)
                print(service_file.read())

        # Configure ctf.json from config.json
        ctf_json = _parse_json(f"{self.setup_path}/config/ctf.json")
        for setting, value in config["ctf-json"].items():
            ctf_json[setting] = value

        # Add teams to ctf.json
        ctf_json["teams"].clear()
        for id in range(1, config["settings"]["teams"] + 1):
            ctf_json["teams"].append(_generate_team(id))

        # Add services to ctf.json
        ctf_json["services"].clear()
        for id, service in enumerate(config["settings"]["services"]):
            ctf_json["services"].append(_generate_service(id + 1, service))

        # Create ctf.json
        with open(f"{self.setup_path}/config/ctf.json", "r+") as ctf_file:
            json.dump(ctf_json, ctf_file, indent=4)
            if self.verbose:
                print("[+] Created ctf.json")
                ctf_file.seek(0)
                print(ctf_file.read())

    def build(self):
        # Step 1: run the build.sh script to create CTF infrastructure
        _run_bash_script(f"{self.setup_path}/build.sh", [])

        # TODO:
        # at this point we know the ip addresses and we can add them to self.ips
        # also we can now expand the ctf.json and add the correct ip addresses

        # Step 2: run the deploy.sh script to deploy configuration to the infrastructure
        _run_bash_script(f"{self.setup_path}/deploy.sh", [])

    def destroy(self):
        _run_bash_script(f"{self.setup_path}/build.sh", ["-d"])
