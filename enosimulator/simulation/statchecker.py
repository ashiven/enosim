import paramiko
from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel

from ..types import SetupVariant

#### Helpers ####


def _beautify_line(line):
    word_index = 0
    words = line.split(" ")
    for i, word in enumerate(words):
        if word and word_index == 0:
            word = "[yellow]" + word
            words[i] = word
            word_index += 1
        elif word and word_index == 1:
            word = word + "[/yellow]"
            words[i] = word
            break

    return " ".join(words)


#### End Helpers ####


class StatChecker:
    def __init__(self, config, secrets):
        self.config = config
        self.secrets = secrets
        self.usernames = {
            SetupVariant.AZURE: "groot",
            SetupVariant.HETZNER: "root",
            SetupVariant.LOCAL: "root",
        }
        self.console = Console()

    def check_containers(self, ip_address):
        container_stats_blank = self._container_stats(ip_address)

        container_stats = []
        for line_number, line in enumerate(container_stats_blank.splitlines()):
            if line_number == 0:
                container_stats.append(f"[b]{line}[/b]")
            else:
                line = _beautify_line(line)
                container_stats.append(line)

        self.console.print(Panel("\n".join(container_stats), expand=True))

    def check_system(self, ip_address):
        ram_usage, cpu_usage = self._system_stats(ip_address)

        [ram_percent, ram_total, ram_used] = ram_usage.splitlines()
        ram_panel = (
            Panel(
                f"[b]RAM Stats[/b]\n"
                + f"[yellow]RAM usage:[/yellow] {float(ram_percent.strip()):.2f}%\n"
                + f"[yellow]RAM total:[/yellow] {(float(ram_total.strip())/1024):.2f} GB\n"
                + f"[yellow]RAM used:[/yellow] {(float(ram_used.strip())/1024):.2f} GB\n",
                expand=True,
            )
            if ram_usage
            else ""
        )
        cpu_panel = (
            Panel(
                f"[b]CPU Stats[/b]\n[yellow]CPU usage:[/yellow] {float(cpu_usage.strip()):.2f}%",
                expand=True,
            )
            if cpu_usage
            else ""
        )
        self.console.print(Columns([ram_panel, cpu_panel]))

    def _container_stats(self, ip_address):
        with paramiko.SSHClient() as client:
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(
                hostname=ip_address,
                username=self.usernames[
                    SetupVariant.from_str(self.config.setup.location)
                ],
                pkey=paramiko.RSAKey.from_private_key_file(
                    self.secrets.vm_secrets.ssh_private_key_path
                ),
            )
            _, stdout, _ = client.exec_command("docker stats --no-stream")
            container_stats = stdout.read().decode("utf-8")

        return container_stats

    def _system_stats(self, ip_address):
        with paramiko.SSHClient() as client:
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(
                hostname=ip_address,
                username=self.usernames[
                    SetupVariant.from_str(self.config.setup.location)
                ],
                pkey=paramiko.RSAKey.from_private_key_file(
                    self.secrets.vm_secrets.ssh_private_key_path
                ),
            )
            _, stdout, _ = client.exec_command(
                "free -m | grep Mem | awk '{print ($3/$2)*100}' && free -m | grep Mem | awk '{print $2}' && free -m | grep Mem | awk '{print $3}'"
            )
            ram_usage = stdout.read().decode("utf-8")
            _, stdout, _ = client.exec_command(
                "sar 1 1 | grep 'Average' | sed 's/^.* //' | awk '{print 100 - $1}'"
            )
            cpu_usage = stdout.read().decode("utf-8")

        return ram_usage, cpu_usage
