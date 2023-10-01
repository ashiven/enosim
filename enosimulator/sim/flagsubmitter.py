import socket

import sshtunnel

#### Helpers ####


def _public_ip(setup, team_address):
    for name, ip_address in setup.ips["private_ip_addresses"].items():
        if ip_address == team_address:
            return setup.ips["public_ip_addresses"][name]


#### End Helpers ####


class FlagSubmitter:
    def __init__(self, setup):
        self.setup = setup
    
    # TODO: - figure out why the connection fails
    def submit_flags(self, team_address, flags):
        flag_str = "testtesttesttest"  # "\n".join(flags)

        with sshtunnel.open_tunnel(
            (_public_ip(self.setup, team_address), 22),
            ssh_username="groot",
            ssh_pkey=self.setup.secrets["vm-secrets"]["ssh-private-key-path"],
            remote_bind_address=(
                self.setup.ips["private_ip_addresses"]["engine"],
                1337,
            ),
            local_bind_address=("localhost", 1337),
        ) as tunnel, socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((tunnel.local_bind_host, tunnel.local_bind_port))
            s.sendall(flag_str.encode())
