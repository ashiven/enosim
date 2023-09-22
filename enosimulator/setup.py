import json
import os
import pprint
import re
import sys
from subprocess import PIPE, STDOUT, CalledProcessError, Popen


####  Helpers ####
def _parse_json(path):
    with open(path, "r") as json_file:
        return json.load(json_file)


def _create_file(path):
    if not os.path.exists(path):
        with open(path, "w") as file:
            file.write("")


def _copy_file(src, dst):
    if os.path.exists(src):
        with open(src, "r") as src_file:
            with open(dst, "w") as dst_file:
                dst_file.write(src_file.read())


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
            print(f"[!] Process exited with return code: {p.returncode}")

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

    def info(self):
        p = pprint.PrettyPrinter()
        print(f"\n==================SERVICES==================\n")
        p.pprint(self.services)
        print(f"\n==================TEAMS=====================\n")
        p.pprint(self.teams)
        print(f"\n==================HOSTNAMES=================\n")
        p.pprint(self.ips)

    def configure(self, config_path):
        config = _parse_json(config_path)
        self.setup_path = f"../test-setup/{config['setup']['location']}"

        # Create services.txt
        _create_file(f"{self.setup_path}/config/services.txt")
        with open(f"{self.setup_path}/config/services.txt", "r+") as service_file:
            for service in config["settings"]["services"]:
                service_file.write(f"{service}\n")
            if self.verbose:
                print("[+] Created services.txt")
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
            new_service = _generate_service(id + 1, service)
            ctf_json["services"].append(new_service)
            self.services[service] = new_service

        # Create ctf.json
        _create_file(f"{self.setup_path}/config/ctf.json")
        with open(f"{self.setup_path}/config/ctf.json", "r+") as ctf_file:
            json.dump(ctf_json, ctf_file, indent=4)
            if self.verbose:
                print("[+] Created ctf.json")
                ctf_file.seek(0)
                print(ctf_file.read())

        # Copy terraform file templates to configure
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
            lines[2] = f"  default = {config['settings']['vulnboxes']}\n"
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
            for vulnbox_id in range(1, config["settings"]["vulnboxes"] + 1):
                outputs_file.write(
                    f'output "vulnbox{vulnbox_id}_ip" {{\n  value = azurerm_public_ip.vm_pip["vulnbox{vulnbox_id}"]._ip_address\n}}\n'
                )

        # TODO:
        # - we need to modify deploy.sh and build.sh to integrate the config

        print(f"[+] Configuration complete")
        self.info()

    def build_infra(self):
        _run_shell_script(f"{self.setup_path}/build.sh", "")

        # TODO:
        # - parse the ip addresses from ../test-setup/azure/logs/ip_addresses.log
        # - at this point we know the ip addresses and we can add them to self.ips
        # - also we can now expand the ctf.json and add the correct ip addresses
        # - here, we need to equally didive the teams across the vulnboxes: i.e. there are two vulnboxes and 6 teams, so each vulnbox gets 3 teams

        with open(
            f"{self.setup_path}/logs/ip_addresses.log",
            "r",
        ) as ip_file:
            lines = ip_file.readlines()
        pattern = r"(\w+)\s*=\s*(.+)"
        for line in lines:
            m = re.match(pattern, line)
            if m:
                self.ips[m.group(1)] = m.group(2)

    def apply_config(self):
        _run_shell_script(f"{self.setup_path}/deploy.sh", "")

    def destroy_infra(self):
        _run_shell_script(f"{self.setup_path}/build.sh", "-d")
