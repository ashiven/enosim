import json
import os
import pprint
from subprocess import PIPE, STDOUT, CalledProcessError, Popen

from colorama import Fore
from shelp import SetupHelper

####  Helpers ####


def _parse_json(path):
    with open(path, "r") as json_file:
        return json.load(json_file)


def _create_file(path):
    if not os.path.exists(path):
        with open(path, "w") as file:
            file.write("")


def _run_shell_script(script_path, args):
    try:
        cmd = "sh " + script_path + " " + args

        p = Popen(
            cmd,
            stdout=PIPE,
            stderr=STDOUT,
            shell=True,
            encoding="utf-8",
            errors="replace",
        )

        while True:
            line = p.stdout.readline()
            if not line and p.poll() is not None:
                break
            if line:
                print(line.strip(), flush=True)

        p.wait()
        if p.returncode != 0:
            print(Fore.RED + f"[!] Process exited with return code: {p.returncode}")

    except CalledProcessError as e:
        print(e)


def _generate_ctf_json():
    new_ctf_json = {
        "title": "eno-ctf",
        "flagValidityInRounds": 2,
        "checkedRoundsPerRound": 3,
        "roundLengthInSeconds": 60,
        "dnsSuffix": "eno.host",
        "teamSubnetBytesLength": 15,
        "flagSigningKey": "ir7PRm0SzqzA0lmFyBfUv68E6Yb7cjbJDp6dummqwr0Od70Sar7P27HVY6oc8PuW",
        "teams": [],
        "services": [],
    }
    return new_ctf_json


def _generate_team(id):
    team_names = ["Kleinmanzama", "Grossmanzama", "Mittelmanzama"]
    new_team = {
        "id": id,
        "name": team_names[id - 1],
        "teamSubnet": "::ffff:10.0.2.0",
        "address": "<placeholder>",
    }
    return new_team


def _generate_service(id, service, checker_port):
    new_service = {
        "id": id,
        "name": service,
        "flagsPerRoundMultiplier": 1,
        "noisesPerRoundMultiplier": 1,
        "havocsPerRoundMultiplier": 1,
        "weightFactor": 1,
        "checkers": [f"http://<placeholder>:{checker_port}"],
    }
    return new_service


#### End Helpers ####


class Setup:
    def __init__(self, verbose=False):
        self.ips = dict()
        self.teams = dict()
        self.services = dict()
        self.setup_path = ""
        self.setup_helper = None
        self.verbose = verbose

    def info(self):
        p = pprint.PrettyPrinter()
        print(Fore.BLUE + f"\n==================SERVICES==================\n")
        p.pprint(self.services)
        print(Fore.BLUE + f"\n==================TEAMS=====================\n")
        p.pprint(self.teams)
        print(Fore.BLUE + f"\n==================HOSTNAMES=================\n")
        p.pprint(self.ips)
        print("\n")

    def configure(self, config_path, secrets_path):
        config = _parse_json(config_path)
        secrets = _parse_json(secrets_path)
        dir_path = os.path.dirname(os.path.abspath(__file__)).replace("\\", "/")
        self.setup_path = f"{dir_path}/../test-setup/{config['setup']['location']}"
        self.setup_helper = SetupHelper(config, secrets)

        # Create services.txt
        _create_file(f"{self.setup_path}/config/services.txt")
        with open(f"{self.setup_path}/config/services.txt", "r+") as service_file:
            for service in config["settings"]["services"]:
                service_file.write(f"{service}\n")
            if self.verbose:
                print(Fore.GREEN + "[+] Created services.txt")
                service_file.seek(0)
                print(service_file.read())

        # Configure ctf.json from config.json
        ctf_json = _generate_ctf_json()
        for setting, value in config["ctf-json"].items():
            ctf_json[setting] = value

        # Add teams to ctf.json
        ctf_json["teams"].clear()
        for id in range(1, config["settings"]["teams"] + 1):
            new_team = _generate_team(id)
            ctf_json["teams"].append(new_team)
            self.teams[new_team["name"]] = new_team

        # Add services to ctf.json
        ctf_json["services"].clear()
        for id, service in enumerate(config["settings"]["services"]):
            checker_port = config["settings"]["checker-ports"][id]
            new_service = _generate_service(id + 1, service, checker_port)
            ctf_json["services"].append(new_service)
            self.services[service] = new_service

        # Create ctf.json
        _create_file(f"{self.setup_path}/config/ctf.json")
        with open(f"{self.setup_path}/config/ctf.json", "r+") as ctf_file:
            json.dump(ctf_json, ctf_file, indent=4)
            if self.verbose:
                print(Fore.GREEN + "[+] Created ctf.json")
                ctf_file.seek(0)
                print(ctf_file.read())

        # Convert template files (terraform, deploy.sh, build.sh, etc.) according to config
        self.setup_helper.convert_templates()

        self.info()
        print(Fore.GREEN + "[+] Configuration complete")

    def build_infra(self):
        _run_shell_script(f"{self.setup_path}/build.sh", "")

        # Get ip addresses from terraform output
        public_ips, private_ips = self.setup_helper.get_ip_addresses()
        self.ips["public_ip_addresses"] = public_ips
        self.ips["private_ip_addresses"] = private_ips

        # Add ip addresses for checkers to ctf.json
        ctf_json = _parse_json(f"{self.setup_path}/config/ctf.json")
        for service in ctf_json["services"]:
            service["checkers"][0] = service["checkers"][0].replace(
                "<placeholder>", self.ips["public_ip_addresses"]["checker_ip"]
            )
            self.services[service["name"]] = service

        # Add ip addresses for teams to ctf.json
        for team in ctf_json["teams"]:
            # TODO: figure out private ip distribution
            team["address"] = self.ips["private_ip_addresses"][0]
            self.teams[team["name"]] = team

        # Update ctf.json
        with open(f"{self.setup_path}/config/ctf.json", "r+") as ctf_file:
            json.dump(ctf_json, ctf_file, indent=4)
            if self.verbose:
                print(Fore.GREEN + "[+] Updated ctf.json")
                ctf_file.seek(0)
                print(ctf_file.read())

        self.info()
        print(Fore.GREEN + "[+] Infrastructure built successfully")

    def apply_config(self):
        _run_shell_script(f"{self.setup_path}/deploy.sh", "")

    def destroy_infra(self):
        _run_shell_script(f"{self.setup_path}/build.sh", "-d")
