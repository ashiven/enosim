import paramiko
from rich.console import Console

from ..setup import SetupVariant

#### Helpers ####


def _private_to_public_ip(setup, team_address):
    for name, ip_address in setup.ips.private_ip_addresses.items():
        if ip_address == team_address:
            return name, setup.ips.public_ip_addresses[name]


#### End Helpers ####


class FlagSubmitter:
    def __init__(self, setup, verbose=False):
        self.setup = setup
        self.verbose = verbose
        self.usernames = {
            SetupVariant.AZURE: "groot",
            SetupVariant.HETZNER: "root",
            SetupVariant.LOCAL: "root",
        }
        self.console = Console()

    def submit_flags(self, team_address, flags):
        flag_str = "\n".join(flags) + "\n"

        with paramiko.SSHClient() as client:
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            vm_name, team_address = _private_to_public_ip(self.setup, team_address)
            client.connect(
                hostname=team_address,
                username=self.usernames[
                    SetupVariant.from_str(self.setup.config.setup.location)
                ],
                pkey=paramiko.RSAKey.from_private_key_file(
                    self.setup.secrets.vm_secrets.ssh_private_key_path
                ),
            )
            transport = client.get_transport()
            with transport.open_channel(
                "direct-tcpip",
                (self.setup.ips.private_ip_addresses["engine"], 1337),
                ("localhost", 0),
            ) as channel:
                channel.send(flag_str.encode())
                if self.verbose:
                    self.console.log(f"[bold blue]Submitted {flag_str}for {vm_name}\n")
