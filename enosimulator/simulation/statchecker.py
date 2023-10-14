from concurrent.futures import ThreadPoolExecutor
from typing import Dict

import paramiko
from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from setup.types import Config, Secrets, SetupVariant

#### Helpers ####


def _beautify_line(line: str):
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
    def __init__(self, config: Config, secrets: Secrets):
        self.config = config
        self.secrets = secrets
        self.usernames = {
            SetupVariant.AZURE: "groot",
            SetupVariant.HETZNER: "root",
            SetupVariant.LOCAL: "root",
        }
        self.console = Console()

    def check_containers(self, ip_addresses: Dict[str, str]):
        futures = dict()
        with ThreadPoolExecutor(max_workers=20) as executor:
            for name, ip_address in ip_addresses.items():
                future = executor.submit(self._container_stats, ip_address)
                futures[name] = future

        container_stat_panels = {
            name: future.result() for name, future in futures.items()
        }

        for name, container_stat_panel in container_stat_panels.items():
            self.console.print(f"\n[bold red]Docker stats for {name}:")
            self.console.print(container_stat_panel)

    # TODO:
    # - update this method so it sends vm data to the backend at the start of every round for every vm
    # - maybe i could also create a separate method for this
    def check_system(self, ip_addresses: Dict[str, str]):
        futures = dict()
        with ThreadPoolExecutor(max_workers=20) as executor:
            for name, ip_address in ip_addresses.items():
                future = executor.submit(self._system_stats, ip_address)
                futures[name] = future

        system_stat_panels = {name: future.result() for name, future in futures.items()}

        for name, system_stat_panel in system_stat_panels.items():
            self.console.print(f"\n[bold red]System stats for {name}:")
            self.console.print(Columns(system_stat_panel))

    def _container_stats(self, ip_address: str):
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
            container_stats_blank = stdout.read().decode("utf-8")

        container_stats = []
        for line_number, line in enumerate(container_stats_blank.splitlines()):
            if line_number == 0:
                container_stats.append(f"[b]{line}[/b]")
            else:
                line = _beautify_line(line)
                container_stats.append(line)

        return Panel("\n".join(container_stats), expand=True)

    def _system_stats(self, ip_address: str):
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
            _, stdout, _ = client.exec_command(
                "sar -n DEV 1 1 | grep 'Average' | grep 'eth0' | awk '{print $5, $6}'"
            )
            network_usage = stdout.read().decode("utf-8")

        [ram_percent, ram_total, ram_used] = ram_usage.splitlines()
        [network_rx, network_tx] = network_usage.split(" ")

        ram_panel = (
            Panel(
                f"[b]RAM Stats[/b]\n"
                + f"[yellow]RAM usage:[/yellow] {float(ram_percent.strip()):.2f}%\n"
                + f"[yellow]RAM total:[/yellow] {(float(ram_total.strip())/1024):.2f} GB\n"
                + f"[yellow]RAM used:[/yellow] {(float(ram_used.strip())/1024):.2f} GB",
                expand=True,
            )
            if ram_usage
            else ""
        )
        cpu_panel = (
            Panel(
                f"[b]CPU Stats[/b]\n"
                + f"[yellow]CPU usage:[/yellow] {float(cpu_usage.strip()):.2f}%",
                expand=True,
            )
            if cpu_usage
            else ""
        )
        network_panel = (
            Panel(
                f"[b]Network Stats[/b]\n"
                + f"[yellow]Network RX:[/yellow] {network_rx.strip()} kB/s\n"
                + f"[yellow]Network TX:[/yellow] {network_tx.strip()} kB/s",
                expand=True,
            )
            if network_usage
            else ""
        )

        return [ram_panel, cpu_panel, network_panel]
