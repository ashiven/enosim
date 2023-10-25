import json
import os
import sys
from subprocess import CalledProcessError, run
from typing import Dict

import aiofiles
from rich.console import Console
from rich.table import Table
from types_ import Config, IpAddresses, Secrets, Service
from util import *

from .setup_helper.setup_helper import SetupHelper


class Setup:
    def __init__(
        self,
        config: Config,
        secrets: Secrets,
        setup_path: str,
        setup_helper: SetupHelper,
    ):
        self.ips = IpAddresses(dict(), dict())
        self.teams = dict()
        self.services = dict()
        self.config = config
        self.secrets = secrets
        self.setup_path = setup_path
        self.setup_helper = setup_helper
        self.skip_infra = self._existing_infra()
        self.console = Console()

    @classmethod
    async def new(
        cls,
        config_path: str,
        secrets_path: str,
    ):
        config_json = await parse_json(config_path)
        config = Config.from_(config_json)
        secrets_json = await parse_json(secrets_path)
        secrets = Secrets.from_(secrets_json)
        dir_path = os.path.dirname(os.path.abspath(__file__))
        dir_path = dir_path.replace("\\", "/")
        setup_path = f"{dir_path}/../../test-setup/{config.setup.location}"
        setup_helper = SetupHelper(config, secrets)
        return cls(config, secrets, setup_path, setup_helper)

    async def build(self) -> None:
        await self.configure()
        await self.build_infra()
        self.deploy()

    async def configure(self) -> None:
        # Create services.txt
        await create_file(f"{self.setup_path}/config/services.txt")
        async with aiofiles.open(
            f"{self.setup_path}/config/services.txt", "r+"
        ) as service_file:
            for service in self.config.settings.services:
                await service_file.write(f"{service}\n")

        # Configure ctf.json from config.json
        ctf_json = self._generate_ctf_json()
        for setting, value in vars(self.config.ctf_json).items():
            ctf_json[kebab_to_camel(setting)] = value

        # Add teams to ctf.json
        ctf_json["teams"].clear()
        ctf_json_teams, setup_teams = self.setup_helper.generate_teams()
        ctf_json["teams"] = ctf_json_teams
        self.teams = setup_teams

        # Add services to ctf.json
        ctf_json["services"].clear()
        for service_id, service in enumerate(self.config.settings.services):
            checker_port = self.config.settings.checker_ports[service_id]
            new_service = self._generate_service(
                service_id + 1,
                service,
                checker_port,
                self.config.settings.simulation_type,
            )
            ctf_json["services"].append(new_service)
            self.services[service] = Service.from_(new_service)

        # Create ctf.json
        await create_file(f"{self.setup_path}/config/ctf.json")
        async with aiofiles.open(
            f"{self.setup_path}/config/ctf.json", "r+"
        ) as ctf_file:
            await ctf_file.write(json.dumps(ctf_json, indent=4))

        # Convert template files (terraform, deploy.sh, build.sh, etc.) according to config
        await self.setup_helper.convert_templates()

    async def build_infra(self) -> None:
        if not self.skip_infra:
            with self.console.status("[bold green]Building infrastructure ..."):
                execute_command(
                    f"{'sh' if sys.platform == 'win32' else 'bash'} {self.setup_path}/build.sh"
                )

        # Get ip addresses from terraform output
        public_ips, private_ips = await self.setup_helper.get_ip_addresses()
        self.ips.public_ip_addresses = public_ips
        self.ips.private_ip_addresses = private_ips

        # Add ip addresses for checkers to ctf.json
        ctf_json = await parse_json(f"{self.setup_path}/config/ctf.json")
        for service in ctf_json["services"]:
            checker_port = service["checkers"].pop()
            for name, ip_address in self.ips.public_ip_addresses.items():
                if name.startswith("checker"):
                    service["checkers"].append(f"http://{ip_address}:{checker_port}")
            self.services[service["name"]] = Service.from_(service)

        # Add ip addresses for teams to ctf.json and self.teams
        for id, team in enumerate(ctf_json["teams"]):
            vulnboxes = self.config.settings.teams
            vulnbox_id = (id % vulnboxes) + 1
            team["address"] = self.ips.private_ip_addresses[f"vulnbox{vulnbox_id}"]
            team["teamSubnet"] = (
                team["teamSubnet"].replace("<placeholder>", team["address"])[:-1] + "0"
            )
            self.teams[team["name"]].address = team["address"]
            self.teams[team["name"]].team_subnet = team["teamSubnet"]

        # Update ctf.json
        await create_file(f"{self.setup_path}/config/ctf.json")
        async with aiofiles.open(
            f"{self.setup_path}/config/ctf.json", "r+"
        ) as ctf_file:
            await ctf_file.write(json.dumps(ctf_json, indent=4))

        self.info()

    def deploy(self) -> None:
        if not self.skip_infra:
            with self.console.status("[bold green]Configuring infrastructure ..."):
                self.console.print("\n[green][+] Configuring known hosts ...")
                for public_ip in self.ips.public_ip_addresses.values():
                    execute_command(f"ssh-keygen -R {public_ip}")
                execute_command(
                    f"chmod 600 {self.secrets.vm_secrets.ssh_private_key_path}"
                )
                execute_command(
                    f"{'sh' if sys.platform == 'win32' else 'bash'} {self.setup_path}/deploy.sh"
                )

    def destroy(self) -> None:
        try:
            with self.console.status("[bold red]Destroying infrastructure ..."):
                execute_command(
                    f"{'sh' if sys.platform == 'win32' else 'bash'} {self.setup_path}/build.sh -d"
                )

            # Delete all files created for this setup
            delete_files(f"{self.setup_path}")
            delete_files(f"{self.setup_path}/config")
            delete_files(f"{self.setup_path}/data")
            delete_files(f"{self.setup_path}/logs")

        except:
            # Delete all files created for this setup
            delete_files(f"{self.setup_path}")
            delete_files(f"{self.setup_path}/config")
            delete_files(f"{self.setup_path}/data")
            delete_files(f"{self.setup_path}/logs")

    def info(self) -> None:
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
        public_ips = vars(self.ips).get("public_ip_addresses", dict())
        for name, ip_address in public_ips.items():
            table.add_row(name, ip_address)
        self.console.print(table)

        table = Table(title="Private IP Addresses")
        table.add_column("Name", justify="center", style="magenta")
        table.add_column("IP Address", justify="center", style="magenta")
        private_ips = vars(self.ips).get("private_ip_addresses", dict())
        for name, ip_address in private_ips.items():
            table.add_row(name, ip_address)
        self.console.print(table)

    def _existing_infra(self) -> bool:
        try:
            stdout = run(
                ["terraform", "show"],
                check=True,
                cwd=self.setup_path,
                capture_output=True,
                text=True,
            ).stdout

            if "No state." in stdout:
                return False
            else:
                return True

        except CalledProcessError:
            return False

    def _generate_ctf_json(self) -> Dict:
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

    def _generate_service(
        self, id: int, service: str, checker_port: int, simulation_type: str
    ) -> Dict:
        new_service = {
            "id": id,
            "name": service,
            "flagsPerRoundMultiplier": 30
            if simulation_type == "basic-stress-test"
            else 1,
            "noisesPerRoundMultiplier": 30
            if simulation_type == "basic-stress-test"
            else 1,
            "havocsPerRoundMultiplier": 1,
            "weightFactor": 1,
            "checkers": [str(checker_port)],
        }
        return new_service
