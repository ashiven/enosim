from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Tuple

import paramiko
from httpx import AsyncClient
from rich.console import Console
from rich.panel import Panel
from types_ import Config, Secrets, SetupVariant


class StatChecker:
    def __init__(
        self,
        config: Config,
        secrets: Secrets,
        client: AsyncClient,
        console: Console,
        verbose: bool = False,
    ):
        self.config = config
        self.secrets = secrets
        self.verbose = verbose
        self.vm_count = config.settings.teams + 2
        self.vm_stats = dict()
        self.container_stats = dict()
        self.client = client
        self.console = console
        self.usernames = {
            SetupVariant.AZURE: "groot",
            SetupVariant.HETZNER: "root",
            SetupVariant.LOCAL: "root",
        }

    def check_containers(self, ip_addresses: Dict[str, str]) -> Dict[str, Panel]:
        futures = dict()
        with ThreadPoolExecutor(max_workers=self.vm_count) as executor:
            for name, ip_address in ip_addresses.items():
                future = executor.submit(self._container_stats, name, ip_address)
                futures[name] = future

        container_stat_panels = {
            name: future.result() for name, future in futures.items()
        }

        return container_stat_panels

    def check_system(self, ip_addresses: Dict[str, str]) -> Dict[str, List[Panel]]:
        futures = dict()
        with ThreadPoolExecutor(max_workers=self.vm_count) as executor:
            for name, ip_address in ip_addresses.items():
                future = executor.submit(self._system_stats, name, ip_address)
                futures[name] = future

        system_stat_panels = {name: future.result() for name, future in futures.items()}

        return system_stat_panels

    async def system_analytics(self) -> None:
        FLASK_PORT = 5000
        for stats in self.vm_stats.values():
            if any(stat is None for stat in stats.values()):
                stats["status"] = "offline"
                stats["uptime"] = 0
            await self.client.post(f"http://localhost:{FLASK_PORT}/vminfo", json=stats)

        # We currently only want to collect analytics on the containers of vulnbox1 since it has all the service containers
        container_stats = self.container_stats["vulnbox1"]
        for stats in container_stats.values():
            await self.client.post(
                f"http://localhost:{FLASK_PORT}/containerinfo", json=stats
            )

    def _container_stats(self, vm_name: str, ip_address: str) -> Panel:
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

            self._save_container_stats(vm_name, container_stats_blank)

        return self._beautify_container_stats(container_stats_blank)

    def _save_container_stats(self, vm_name: str, container_stats: str) -> None:
        stats = dict()
        lines = container_stats.splitlines()
        for i, line in enumerate(lines):
            if i == 0:
                continue
            parts = line.split()
            name = parts[1]
            cpu_usage = parts[2]
            cpu_usage = round(float(cpu_usage[:-1]), 2)
            ram_usage = parts[6]
            ram_usage = round(float(ram_usage[:-1]), 2)
            network_rx = "".join((c if c in "0123456789." else "") for c in parts[7])
            network_rx = round(float(network_rx) * (1024 if "MB" in parts[7] else 1), 2)
            network_tx = "".join((c if c in "0123456789." else "") for c in parts[9])
            network_tx = round(float(network_tx) * (1024 if "MB" in parts[9] else 1), 2)

            stats[name] = {
                "name": name,
                "cpuusage": cpu_usage,
                "ramusage": ram_usage,
                "netrx": network_rx,
                "nettx": network_tx,
            }

        self.container_stats[vm_name] = stats

    def _beautify_container_stats(self, container_stats_blank: str) -> Panel:
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

    def _system_stats(self, vm_name: str, ip_address: str) -> List[Panel]:
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
                + "sar 1 2 | grep 'Average' | sed 's/^.* //' | awk '{print 100 - $1}' &&"
                + "nproc &&"
                + "df -h / | awk 'NR == 2 {print $2}'"
            )
            system_stats = stdout.read().decode("utf-8")
            _, stdout, _ = client.exec_command(
                "sar -n DEV 1 1 | grep 'Average' | grep 'eth0' | awk '{print $5, $6}'"
            )
            network_usage = stdout.read().decode("utf-8")

        (
            ram_percent,
            ram_total,
            ram_used,
            cpu_usage,
            cpu_cores,
            disk_size,
            network_rx,
            network_tx,
        ) = self._parse_system_stats(system_stats, network_usage)

        self._save_system_stats(
            vm_name,
            ip_address,
            ram_percent,
            ram_total,
            cpu_usage,
            cpu_cores,
            disk_size,
            network_rx,
            network_tx,
        )

        return self._beautify_system_stats(
            ram_percent,
            ram_total,
            ram_used,
            cpu_usage,
            cpu_cores,
            network_rx,
            network_tx,
        )

    def _parse_system_stats(self, system_stats: str, network_usage: str) -> Tuple:
        if system_stats:
            [
                ram_percent,
                ram_total,
                ram_used,
                cpu_usage,
                cpu_cores,
                disk_size,
            ] = system_stats.splitlines()
            ram_percent = round(float(ram_percent.strip()), 2)
            ram_total = round(float(ram_total.strip()) / 1024, 2)
            ram_used = round(float(ram_used.strip()) / 1024, 2)
            cpu_usage = round(float(cpu_usage.strip()), 2)
            cpu_cores = int(cpu_cores.strip())
            disk_size = float(disk_size.strip()[:-1])

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
            network_rx = float(network_rx.strip())
            network_tx = float(network_tx.strip())
        else:
            network_rx, network_tx = None, None

        return (
            ram_percent,
            ram_total,
            ram_used,
            cpu_usage,
            cpu_cores,
            disk_size,
            network_rx,
            network_tx,
        )

    def _save_system_stats(
        self,
        vm_name: str,
        ip_address: str,
        ram_percent: float,
        ram_total: float,
        cpu_usage: float,
        cpu_cores: int,
        disk_size: float,
        network_rx: float,
        network_tx: float,
    ) -> None:
        prev_uptime = (
            self.vm_stats[vm_name]["uptime"] if vm_name in self.vm_stats else 0
        )
        self.vm_stats[vm_name] = {
            "name": vm_name,
            "ip": ip_address,
            "cpu": cpu_cores,
            "ram": ram_total,
            "disk": disk_size,
            "status": "online",
            "uptime": 0,
            "cpuusage": cpu_usage,
            "ramusage": ram_percent,
            "netrx": network_rx,
            "nettx": network_tx,
        }
        self.vm_stats[vm_name]["uptime"] = prev_uptime + 1

    def _beautify_system_stats(
        self,
        ram_percent: float,
        ram_total: float,
        ram_used: float,
        cpu_usage: float,
        cpu_cores: int,
        network_rx: float,
        network_tx: float,
    ) -> List[Panel]:
        ram_panel = (
            Panel(
                f"[b]RAM Stats[/b]\n"
                + f"[yellow]RAM usage:[/yellow] {ram_percent:.2f}%\n"
                + f"[yellow]RAM total:[/yellow] {ram_total:.2f} GB\n"
                + f"[yellow]RAM used:[/yellow] {ram_used:.2f} GB",
                expand=True,
            )
            if ram_total and ram_used and ram_percent
            else ""
        )
        cpu_panel = (
            Panel(
                f"[b]CPU Stats[/b]\n"
                + f"[yellow]CPU usage:[/yellow] {cpu_usage:.2f}%\n"
                + f"[yellow]CPU cores:[/yellow] {cpu_cores}",
                expand=True,
            )
            if cpu_usage and cpu_cores
            else ""
        )
        network_panel = (
            Panel(
                f"[b]Network Stats[/b]\n"
                + f"[yellow]Network RX:[/yellow] {network_rx:.2f} kB/s\n"
                + f"[yellow]Network TX:[/yellow] {network_tx:.2f} kB/s",
                expand=True,
            )
            if network_rx and network_tx
            else ""
        )

        return [ram_panel, cpu_panel, network_panel]
