import json
import os
from subprocess import PIPE, STDOUT, CalledProcessError, Popen

import aiofiles
from rich.console import Console
from rich.table import Table
from setup.setuphelper import SetupHelper
from setup.types import Service

####  Helpers ####


def _kebab_to_camel(s):
    words = s.split("-")
    return words[0] + "".join(w.title() for w in words[1:])


async def _parse_json(path):
    async with aiofiles.open(path, "r") as json_file:
        content = await json_file.read()
        return json.loads(content)


async def _create_file(path):
    if os.path.exists(path):
        os.remove(path)
    async with aiofiles.open(path, "w") as file:
        await file.write("")


def _delete_files(path):
    for file in os.listdir(path):
        if file == ".gitkeep":
            continue
        file_path = os.path.join(path, file)
        if os.path.isfile(file_path):
            os.remove(file_path)


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
            c = Console()
            c.print(
                f"\n[bold red][!] Process exited with return code: {p.returncode}\n"
            )

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


def _generate_service(id, service, checker_port, simulation_type):
    new_service = {
        "id": id,
        "name": service,
        "flagsPerRoundMultiplier": 1,
        "noisesPerRoundMultiplier": 1,
        "havocsPerRoundMultiplier": 1,
        "weightFactor": 1,
        "checkers": [str(checker_port)],
    }
    if simulation_type == "stress-test":
        new_service["flagsPerRoundMultiplier"] = 10
        new_service["noisesPerRoundMultiplier"] = 10
        new_service["havocsPerRoundMultiplier"] = 10
        new_service["weightFactor"] = 1
    return new_service


def _to_service_data(service):
    new_service = Service(
        id=service["id"],
        name=service["name"],
        flags_per_round_multiplier=service["flagsPerRoundMultiplier"],
        noises_per_round_multiplier=service["noisesPerRoundMultiplier"],
        havocs_per_round_multiplier=service["havocsPerRoundMultiplier"],
        weight_factor=service["weightFactor"],
        checkers=service["checkers"],
    )
    return new_service


#### End Helpers ####


class Setup:
    def __init__(self, config, secrets, skip_infra, setup_path, setup_helper, verbose):
        self.ips = dict()
        self.teams = dict()
        self.services = dict()
        self.verbose = verbose
        self.config = config
        self.secrets = secrets
        self.skip_infra = skip_infra
        self.setup_path = setup_path
        self.setup_helper = setup_helper
        self.console = Console()

    @classmethod
    async def new(cls, config_path, secrets_path, skip_infra, verbose=False):
        config = await _parse_json(config_path)
        secrets = await _parse_json(secrets_path)
        dir_path = os.path.dirname(os.path.abspath(__file__))
        dir_path = dir_path.replace("\\", "/")
        setup_path = f"{dir_path}/../../test-setup/{config['setup']['location']}"
        setup_helper = SetupHelper(config, secrets)
        return cls(config, secrets, skip_infra, setup_path, setup_helper, verbose)

    def info(self):
        table = Table(title="Teams")
        table.add_column("ID", justify="center", style="magenta")
        table.add_column("Name", justify="center", style="magenta")
        table.add_column("Subnet", justify="center", style="magenta")
        table.add_column("Address", justify="center", style="magenta")
        table.add_column("Experience", justify="center", style="magenta")
        for team_name, team in self.teams.items():
            table.add_row(
                str(team.id),
                team_name,
                team.team_subnet,
                team.address,
                str(team.experience),
            )
        self.console.print(table)

        table = Table(title="Services")
        table.add_column("ID", justify="center", style="magenta")
        table.add_column("Name", justify="center", style="magenta")
        table.add_column("Checkers", justify="center", style="magenta")
        for service_name, service in self.services.items():
            table.add_row(
                str(service.id),
                service_name,
                str(service.checkers),
            )
        self.console.print(table)

        table = Table(title="Public IP Addresses")
        table.add_column("Name", justify="center", style="magenta")
        table.add_column("IP Address", justify="center", style="magenta")
        public_ips = self.ips.get("public_ip_addresses", dict())
        for name, ip_address in public_ips.items():
            table.add_row(name, ip_address)
        self.console.print(table)

        table = Table(title="Private IP Addresses")
        table.add_column("Name", justify="center", style="magenta")
        table.add_column("IP Address", justify="center", style="magenta")
        private_ips = self.ips.get("private_ip_addresses", dict())
        for name, ip_address in private_ips.items():
            table.add_row(name, ip_address)
        self.console.print(table)

    async def build(self):
        await self.configure()
        await self.build_infra()
        self.deploy()

    async def configure(self):
        # Create services.txt
        await _create_file(f"{self.setup_path}/config/services.txt")
        async with aiofiles.open(
            f"{self.setup_path}/config/services.txt", "r+"
        ) as service_file:
            for service in self.config["settings"]["services"]:
                await service_file.write(f"{service}\n")
            if self.verbose:
                self.console.print("\n[bold cyan][+] Created services.txt\n")
                await service_file.seek(0)
                content = await service_file.read()
                self.console.print(content)

        # Configure ctf.json from config.json
        ctf_json = _generate_ctf_json()
        for setting, value in self.config["ctf-json"].items():
            ctf_json[_kebab_to_camel(setting)] = value

        # Add teams to ctf.json
        ctf_json["teams"].clear()
        ctf_json_teams, setup_teams = self.setup_helper.generate_teams()
        ctf_json["teams"] = ctf_json_teams
        self.teams = setup_teams

        # Add services to ctf.json
        ctf_json["services"].clear()
        for id, service in enumerate(self.config["settings"]["services"]):
            checker_port = self.config["settings"]["checker-ports"][id]
            new_service = _generate_service(
                id + 1,
                service,
                checker_port,
                self.config["settings"]["simulation-type"],
            )
            ctf_json["services"].append(new_service)
            self.services[service] = _to_service_data(new_service)

        # Create ctf.json
        await _create_file(f"{self.setup_path}/config/ctf.json")
        async with aiofiles.open(
            f"{self.setup_path}/config/ctf.json", "r+"
        ) as ctf_file:
            await ctf_file.write(json.dumps(ctf_json, indent=4))
            if self.verbose:
                self.console.print("\n[bold cyan] [+] Created ctf.json\n")
                await ctf_file.seek(0)
                content = await ctf_file.read()
                self.console.print(content)

        # Convert template files (terraform, deploy.sh, build.sh, etc.) according to config
        await self.setup_helper.convert_templates()

    async def build_infra(self):
        if not self.skip_infra:
            with self.console.status("[bold green]Building infrastructure ..."):
                _run_shell_script(f"{self.setup_path}/build.sh", "")

        # Get ip addresses from terraform output
        public_ips, private_ips = await self.setup_helper.get_ip_addresses()
        self.ips["public_ip_addresses"] = public_ips
        self.ips["private_ip_addresses"] = private_ips

        # Add ip addresses for checkers to ctf.json
        ctf_json = await _parse_json(f"{self.setup_path}/config/ctf.json")
        for service in ctf_json["services"]:
            checker_port = service["checkers"].pop()
            for name, ip_address in self.ips["public_ip_addresses"].items():
                if name.startswith("checker"):
                    service["checkers"].append(f"http://{ip_address}:{checker_port}")
            self.services[service["name"]] = _to_service_data(service)

        # Add ip addresses for teams to ctf.json and self.teams
        for id, team in enumerate(ctf_json["teams"]):
            vulnboxes = self.config["settings"]["vulnboxes"]
            vulnbox_id = (id % vulnboxes) + 1
            team["address"] = self.ips["private_ip_addresses"][f"vulnbox{vulnbox_id}"]
            team["teamSubnet"] = (
                team["teamSubnet"].replace("<placeholder>", team["address"])[:-1] + "0"
            )
            self.teams[team["name"]].address = team["address"]
            self.teams[team["name"]].team_subnet = team["teamSubnet"]

        # Update ctf.json
        await _create_file(f"{self.setup_path}/config/ctf.json")
        async with aiofiles.open(
            f"{self.setup_path}/config/ctf.json", "r+"
        ) as ctf_file:
            await ctf_file.write(json.dumps(ctf_json, indent=4))
            if self.verbose:
                self.console.print("\n[bold cyan][+] Updated ctf.json\n")
                await ctf_file.seek(0)
                content = await ctf_file.read()
                self.console.print(content)

        self.info()

    def deploy(self):
        if not self.skip_infra:
            with self.console.status("[bold green]Configuring infrastructure ..."):
                _run_shell_script(f"{self.setup_path}/deploy.sh", "")

    def destroy(self):
        with self.console.status("[bold red]Destroying infrastructure ..."):
            _run_shell_script(f"{self.setup_path}/build.sh", "-d")

        # Delete all files created for this setup
        _delete_files(f"{self.setup_path}")
        _delete_files(f"{self.setup_path}/config")
        _delete_files(f"{self.setup_path}/data")
        _delete_files(f"{self.setup_path}/logs")
