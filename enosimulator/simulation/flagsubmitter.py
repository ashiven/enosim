from typing import List, Tuple

import paramiko
from rich.console import Console
from setup import Setup
from types_ import SetupVariant, VMType


class FlagSubmitter:
    """
    A Class for submitting flags to the submission endpoint running on the engine.

    Connects to the engine by creating an SSH tunnel through the VM.
    After connecting, the flags are submitted to the submission endpoint.

    Attributes:
        config: The configuration file supplied by the user.
        secrets: The secrets file supplied by the user.
        ip_addresses: The IP addresses of the VMs in the simulation.
        verbose: Whether to print verbose output.
        debug: Whether to print debug output.
        console: The console used for printing.
        usernames: The SSH usernames according to the chosen setup location.
    """

    def __init__(
        self,
        setup: Setup,
        console: Console,
        verbose: bool = False,
        debug: bool = False,
    ):
        """Initialize the FlagSubmitter class."""

        self.config = setup.config
        self.secrets = setup.secrets
        self.ip_addresses = setup.ips
        self.verbose = verbose
        self.debug = debug
        self.console = console
        self.usernames = {
            SetupVariant.AZURE: "groot",
            SetupVariant.HETZNER: "root",
            SetupVariant.LOCAL: "root",
        }

    def submit_flags(self, team_address: str, flags: List[str]) -> None:
        """
        Submit the flags for a team to the submission endpoint.

        This works by creating an SSH tunnel through the team's VM to the submission endpoint.
        After connecting, the flags are submitted to the submission endpoint.

        Args:
            team_address (str): The IP address of the team's VM.
            flags (List[str]): The flags to submit.
        """

        SUBMISSION_ENDPOINT_PORT = 1337
        flag_str = "\n".join(flags) + "\n"

        with paramiko.SSHClient() as client:
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            vm_name, team_address = self._private_to_public_ip(team_address)
            client.connect(
                hostname=team_address,
                username=self.usernames[
                    SetupVariant.from_str(self.config.setup.location)
                ],
                pkey=paramiko.RSAKey.from_private_key_file(
                    self.secrets.vm_secrets.ssh_private_key_path
                ),
            )
            transport = client.get_transport()
            with transport.open_channel(
                "direct-tcpip",
                (
                    self.ip_addresses.private_ip_addresses[VMType.ENGINE.value],
                    SUBMISSION_ENDPOINT_PORT,
                ),
                ("localhost", 0),
            ) as channel:
                channel.send(flag_str.encode())
                if self.debug:
                    self.console.log(f"[bold blue]Submitted {flag_str}for {vm_name}\n")

    def _private_to_public_ip(self, team_address: str) -> Tuple[str, str]:
        """Convert a private IP address to a public IP address."""

        for name, ip_address in self.ip_addresses.private_ip_addresses.items():
            if ip_address == team_address:
                return name, self.ip_addresses.public_ip_addresses[name]
