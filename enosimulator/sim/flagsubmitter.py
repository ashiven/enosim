import paramiko

#### Helpers ####


def _private_to_public_ip(setup, team_address):
    for name, ip_address in setup.ips["private_ip_addresses"].items():
        if ip_address == team_address:
            return setup.ips["public_ip_addresses"][name]


#### End Helpers ####


class FlagSubmitter:
    def __init__(self, setup):
        self.setup = setup

    def submit_flags(self, team_address, flags):
        flag_str = "\n".join(flags)

        with paramiko.SSHClient() as client:
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(
                hostname=_private_to_public_ip(team_address),
                username="groot",
                pkey=paramiko.RSAKey.from_private_key_file(
                    self.setup.secrets["vm-secrets"]["ssh-private-key-path"]
                ),
            )
            transport = client.get_transport()
            with transport.open_channel(
                "direct-tcpip",
                (self.setup.ips["private_ip_addresses"]["engine"], 1337),
                ("localhost", 0),
            ) as channel:
                channel.send(flag_str.encode())
