from concurrent.futures import ThreadPoolExecutor
from typing import Dict

import paramiko
from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from setup.types import Config, Secrets, SetupVariant


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

    # TODO:
    # - sends vm data in every round for every vm
    def system_analytics():
        pass

    def _container_stats(self, ip_address: str, beautify: bool = True):
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

        if beautify:
            return self._beautify_container_stats(container_stats_blank)
        else:
            return container_stats_blank

    def _beautify_container_stats(self, container_stats_blank: str):
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

        container_stats = []
        for line_number, line in enumerate(container_stats_blank.splitlines()):
            if line_number == 0:
                container_stats.append(f"[b]{line}[/b]")
            else:
                line = _beautify_line(line)
                container_stats.append(line)

        return Panel("\n".join(container_stats), expand=True)

    def _system_stats(self, ip_address: str, beautify: bool = True):
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
                "free -m | grep Mem | awk '{print ($3/$2)*100}' &&"
                + "free -m | grep Mem | awk '{print $2}' &&"
                + "free -m | grep Mem | awk '{print $3}' &&"
                + "sar 1 1 | grep 'Average' | sed 's/^.* //' | awk '{print 100 - $1}' &&"
                + "nproc &&"
                + "df -h / | awk 'NR == 2 {print $2}'"
            )
            system_stats = stdout.read().decode("utf-8")
            _, stdout, _ = client.exec_command(
                "sar -n DEV 1 1 | grep 'Average' | grep 'eth0' | awk '{print $5, $6}'"
            )
            network_usage = stdout.read().decode("utf-8")

        if system_stats:
            [
                ram_percent,
                ram_total,
                ram_used,
                cpu_usage,
                cpu_cores,
                disk_size,
            ] = system_stats.splitlines()
        else:
            ram_percent, ram_total, ram_used, cpu_usage, cpu_cores, disk_size = (
                None,
                None,
                None,
                None,
                None,
                None,
            )

        if network_usage:
            [network_rx, network_tx] = network_usage.splitlines()[-1].split(" ")
        else:
            network_rx, network_tx = None, None

        if beautify:
            return self._beautify_system_stats(
                ram_percent,
                ram_total,
                ram_used,
                cpu_usage,
                cpu_cores,
                network_rx,
                network_tx,
            )
        else:
            return [
                ram_percent,
                ram_total,
                cpu_usage,
                cpu_cores,
                network_rx,
                network_tx,
                disk_size,
            ]

    def _beautify_system_stats(
        self,
        ram_percent: str,
        ram_total: str,
        ram_used: str,
        cpu_usage: str,
        cpu_cores: str,
        network_rx: str,
        network_tx: str,
    ):
        ram_panel = (
            Panel(
                f"[b]RAM Stats[/b]\n"
                + f"[yellow]RAM usage:[/yellow] {float(ram_percent.strip()):.2f}%\n"
                + f"[yellow]RAM total:[/yellow] {(float(ram_total.strip())/1024):.2f} GB\n"
                + f"[yellow]RAM used:[/yellow] {(float(ram_used.strip())/1024):.2f} GB",
                expand=True,
            )
            if ram_total and ram_used and ram_percent
            else ""
        )
        cpu_panel = (
            Panel(
                f"[b]CPU Stats[/b]\n"
                + f"[yellow]CPU usage:[/yellow] {float(cpu_usage.strip()):.2f}%\n"
                + f"[yellow]CPU cores:[/yellow] {cpu_cores.strip()}",
                expand=True,
            )
            if cpu_usage and cpu_cores
            else ""
        )
        network_panel = (
            Panel(
                f"[b]Network Stats[/b]\n"
                + f"[yellow]Network RX:[/yellow] {network_rx.strip()} kB/s\n"
                + f"[yellow]Network TX:[/yellow] {network_tx.strip()} kB/s",
                expand=True,
            )
            if network_rx and network_tx
            else ""
        )

        return [ram_panel, cpu_panel, network_panel]
