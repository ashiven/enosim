import json
import os
import sys
from subprocess import CalledProcessError, run
from typing import Dict

import aiofiles
import jsons
from requests import get
from rich.console import Console
from rich.table import Table
from types_ import Config, IpAddresses, Secrets, Service

from .setup_helper import SetupHelper
from .util import create_file, delete_files, execute_command, kebab_to_camel, parse_json


class Setup:
    """
    A class representing the simulation setup.

    Attributes:
        ips: A dictionary containing the public and private ip addresses of the infrastructure components.
        teams: A dictionary containing information about the teams participating in the competition.
        services: A dictionary containing information about the services played in the competition.
        config: A Config object containing the configuration of the simulation and the infrastructure.
        secrets: A Secrets object containing the secrets used for building and configuring the infrastructure.
        setup_path: A string containing the path to the setup directory for the chosen location.
        setup_helper: A SetupHelper object used for generating the infrastructure.
        console: A Console object used for printing to the console.
    """

    def __init__(
        self,
        config: Config,
        secrets: Secrets,
        setup_helper: SetupHelper,
        console: Console,
    ):
        """Initializes the Setup with the given configuration and secrets."""

        self.ips = IpAddresses(dict(), dict())
        self.teams = dict()
        self.services = dict()
        self.config = config
        self.secrets = secrets
        dir_path = os.path.dirname(os.path.abspath(__file__))
        dir_path = dir_path.replace("\\", "/")
        self.setup_path = f"{dir_path}/../../infra/{self.config.setup.location}"
        self.setup_helper = setup_helper
        self.console = console
        if self.config.settings.simulation_type == "basic-stress-test":
            self.config.settings.teams = 1

    async def build(self) -> None:
        """Builds and configures the infrastructure."""

        await self.initialize()
        await self.build_infra()
        self.configure_infra()

    async def initialize(self) -> None:
        """Generates the infrastructure configuration files."""

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

        # Convert template files (terraform, configure.sh, build.sh, etc.) according to config
        await self.setup_helper.convert_templates()

    async def build_infra(self) -> None:
        """Builds the infrastructure."""

        if not self._existing_infra():
            with self.console.status("[bold green]Building infrastructure ..."):
                execute_command(
                    f"{'sh' if sys.platform == 'win32' else 'bash'} {self.setup_path}/build.sh"
                )

        with open(f"{self.setup_path}/logs/ip_addresses.log", "w") as ip_log_file:
            ip_log_file.write(
                "vulnbox_public_ips = {\n"
                + '  "vulnbox1" = "234.123.12.32"\n'
                + '  "vulnbox2" = "234.231.12.32"\n'
                + '  "vulnbox3" = "234.231.12.32"\n'
                + '  "vulnbox4" = "234.231.12.32"\n'
                + '  "vulnbox5" = "234.231.12.32"\n'
                + '  "vulnbox6" = "234.231.12.32"\n'
                + '  "vulnbox7" = "234.231.12.32"\n'
                + '  "vulnbox8" = "234.231.12.32"\n'
                + '  "vulnbox9" = "234.231.12.32"\n'
                + '  "vulnbox10" = "234.231.12.32"\n'
                + '  "vulnbox11" = "234.231.12.32"\n'
                + '  "vulnbox12" = "234.231.12.32"\n'
                + '  "vulnbox13" = "234.231.12.32"\n'
                + '  "vulnbox14" = "234.231.12.32"\n'
                + '  "vulnbox15" = "234.231.12.32"\n'
                + '  "vulnbox16" = "234.231.12.32"\n'
                + '  "vulnbox17" = "234.231.12.32"\n'
                + '  "vulnbox18" = "234.231.12.32"\n'
                + '  "vulnbox19" = "234.231.12.32"\n'
                + '  "vulnbox20" = "234.231.12.32"\n'
                + '  "vulnbox21" = "234.231.12.32"\n'
                + '  "vulnbox22" = "234.231.12.32"\n'
                + '  "vulnbox23" = "234.231.12.32"\n'
                + '  "vulnbox24" = "234.231.12.32"\n'
                + '  "vulnbox25" = "234.231.12.32"\n'
                + '  "vulnbox26" = "234.231.12.32"\n'
                + '  "vulnbox27" = "234.231.12.32"\n'
                + '  "vulnbox28" = "234.231.12.32"\n'
                + '  "vulnbox29" = "234.231.12.32"\n'
                + '  "vulnbox30" = "234.231.12.32"\n'
                + '  "vulnbox31" = "234.231.12.32"\n'
                + '  "vulnbox32" = "234.231.12.32"\n'
                + '  "vulnbox33" = "234.231.12.32"\n'
                + '  "vulnbox34" = "234.231.12.32"\n'
                + '  "vulnbox35" = "234.231.12.32"\n'
                + '  "vulnbox36" = "234.231.12.32"\n'
                + '  "vulnbox37" = "234.231.12.32"\n'
                + '  "vulnbox38" = "234.231.12.32"\n'
                + '  "vulnbox39" = "234.231.12.32"\n'
                + '  "vulnbox40" = "234.231.12.32"\n'
                + '  "vulnbox41" = "234.231.12.32"\n'
                + '  "vulnbox42" = "234.231.12.32"\n'
                + '  "vulnbox43" = "234.231.12.32"\n'
                + '  "vulnbox44" = "234.231.12.32"\n'
                + '  "vulnbox45" = "234.231.12.32"\n'
                + '  "vulnbox46" = "234.231.12.32"\n'
                + '  "vulnbox47" = "234.231.12.32"\n'
                + '  "vulnbox48" = "234.231.12.32"\n'
                + '  "vulnbox49" = "234.231.12.32"\n'
                + '  "vulnbox50" = "234.231.12.32"\n'
                + '  "vulnbox51" = "234.231.12.32"\n'
                + '  "vulnbox52" = "234.231.12.32"\n'
                + '  "vulnbox53" = "234.231.12.32"\n'
                + '  "vulnbox54" = "234.231.12.32"\n'
                + '  "vulnbox55" = "234.231.12.32"\n'
                + '  "vulnbox56" = "234.231.12.32"\n'
                + '  "vulnbox57" = "234.231.12.32"\n'
                + '  "vulnbox58" = "234.231.12.32"\n'
                + '  "vulnbox59" = "234.231.12.32"\n'
                + '  "vulnbox60" = "234.231.12.32"\n'
                + '  "vulnbox61" = "234.231.12.32"\n'
                + '  "vulnbox62" = "234.231.12.32"\n'
                + '  "vulnbox63" = "234.231.12.32"\n'
                + '  "vulnbox64" = "234.231.12.32"\n'
                + '  "vulnbox65" = "234.231.12.32"\n'
                + '  "vulnbox66" = "234.231.12.32"\n'
                + '  "vulnbox67" = "234.231.12.32"\n'
                + '  "vulnbox68" = "234.231.12.32"\n'
                + '  "vulnbox69" = "234.231.12.32"\n'
                + '  "vulnbox70" = "234.231.12.32"\n'
                + '  "vulnbox71" = "234.231.12.32"\n'
                + '  "vulnbox72" = "234.231.12.32"\n'
                + '  "vulnbox73" = "234.231.12.32"\n'
                + '  "vulnbox74" = "234.231.12.32"\n'
                + '  "vulnbox75" = "234.231.12.32"\n'
                + '  "vulnbox76" = "234.231.12.32"\n'
                + '  "vulnbox77" = "234.231.12.32"\n'
                + '  "vulnbox78" = "234.231.12.32"\n'
                + '  "vulnbox79" = "234.231.12.32"\n'
                + '  "vulnbox80" = "234.231.12.32"\n'
                + '  "vulnbox81" = "234.231.12.32"\n'
                + '  "vulnbox82" = "234.231.12.32"\n'
                + '  "vulnbox83" = "234.231.12.32"\n'
                + '  "vulnbox84" = "234.231.12.32"\n'
                + '  "vulnbox85" = "234.231.12.32"\n'
                + '  "vulnbox86" = "234.231.12.32"\n'
                + '  "vulnbox87" = "234.231.12.32"\n'
                + '  "vulnbox88" = "234.231.12.32"\n'
                + '  "vulnbox89" = "234.231.12.32"\n'
                + '  "vulnbox90" = "234.231.12.32"\n'
                + '  "vulnbox91" = "234.231.12.32"\n'
                + '  "vulnbox92" = "234.231.12.32"\n'
                + '  "vulnbox93" = "234.231.12.32"\n'
                + '  "vulnbox94" = "234.231.12.32"\n'
                + '  "vulnbox95" = "234.231.12.32"\n'
                + '  "vulnbox96" = "234.231.12.32"\n'
                + '  "vulnbox97" = "234.231.12.32"\n'
                + '  "vulnbox98" = "234.231.12.32"\n'
                + '  "vulnbox99" = "234.231.12.32"\n'
                + '  "vulnbox100" = "234.123.32.12"\n}\n'
                + 'checker = "123.32.32.21"\n'
                + 'engine = "123.32.23.21"\n',
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

        # self.info()

    def configure_infra(self) -> None:
        """
        Uses the configuration files generated in the initialize step to configure the
        infrastructure.

        This includes configuring the known hosts and setting the appropriate private
        key permissions.
        """

        if not self._existing_config():
            with self.console.status("[bold green]Configuring infrastructure ..."):
                self.console.print(
                    "\n[green][+] Configuring known hosts and private key permissions..."
                )
                for public_ip in self.ips.public_ip_addresses.values():
                    execute_command(f"ssh-keygen -R {public_ip}")

                if sys.platform == "win32":
                    execute_command(
                        f"icacls {self.secrets.vm_secrets.ssh_private_key_path} /reset"
                    )
                    execute_command(
                        f"icacls {self.secrets.vm_secrets.ssh_private_key_path} /grant %username%:rw"
                    )
                    execute_command(
                        f"icacls {self.secrets.vm_secrets.ssh_private_key_path} /inheritance:d"
                    )
                    execute_command(
                        f"icacls {self.secrets.vm_secrets.ssh_private_key_path} /remove *S-1-5-11 *S-1-5-18 *S-1-5-32-544 *S-1-5-32-545"
                    )
                else:
                    execute_command(
                        f"chmod 600 {self.secrets.vm_secrets.ssh_private_key_path}"
                    )

                execute_command(
                    f"{'sh' if sys.platform == 'win32' else 'bash'} {self.setup_path}/configure.sh"
                )

    def destroy(self) -> None:
        """Destroys the infrastructure and deletes all files created for this setup."""

        try:
            # with self.console.status("[bold red]Destroying infrastructure ..."):
            #     execute_command(
            #         f"{'sh' if sys.platform == 'win32' else 'bash'} {self.setup_path}/build.sh -d"
            #     )

            # Delete all files created for this setup
            delete_files(f"{self.setup_path}")
            delete_files(f"{self.setup_path}/config")
            delete_files(f"{self.setup_path}/data")
            delete_files(f"{self.setup_path}/logs")

        except Exception:
            # Delete all files created for this setup
            delete_files(f"{self.setup_path}")
            delete_files(f"{self.setup_path}/config")
            delete_files(f"{self.setup_path}/data")
            delete_files(f"{self.setup_path}/logs")

    def info(self) -> None:
        """
        Prints information about the setup to the console.

        This includes the teams, services, and ip addresses.
        """

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
        """
        Checks whether the infrastructure has already been built.

        This is done by checking whether the terraform state file exists and whether the
        ip_addresses.log file exists.

        If an infrastructure has already been built the build step is skipped.
        """

        return True

        try:
            ip_logs_available = os.path.exists(
                f"{self.setup_path}/logs/ip_addresses.log"
            )

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
                return True and ip_logs_available

        except CalledProcessError:
            return False

    def _existing_config(self) -> bool:
        """
        Checks whether the infrastructure has already been configured.

        This is done by checking whether the infrastructure is reachable and whether the
        attack.json file exists.

        If an infrastructure has already been configured the configure step is skipped.
        """

        return True

        try:
            r = get(
                f"http://{self.ips.public_ip_addresses['engine']}:5001/scoreboard/attack.json"
            )
            if r.status_code != 200:
                raise Exception("Infrastructure is not configured!")

            attack_info = jsons.loads(r.content)
            if not attack_info["services"]:
                raise Exception("Infrastructure is not configured!")

            return True

        except Exception:
            return False

    def _generate_ctf_json(self) -> Dict:
        """Generates a ctf.json file template in the form of a dictionary from the
        config.json file.
        """

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
        """Generates a service in the form of a dictionary from the config.json file."""

        new_service = {
            "id": id,
            "name": service,
            "flagsPerRoundMultiplier": 30
            if simulation_type == "basic-stress-test"
            else 10
            if simulation_type == "intensive-stress-test"
            else 1,
            "noisesPerRoundMultiplier": 30
            if simulation_type == "basic-stress-test"
            else 10
            if simulation_type == "intensive-stress-test"
            else 1,
            "havocsPerRoundMultiplier": 1,
            "weightFactor": 1,
            "checkers": [str(checker_port)],
        }
        return new_service
