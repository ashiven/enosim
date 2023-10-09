from concurrent.futures import ThreadPoolExecutor, as_completed

import docker
import paramiko
from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from setup.types import SetupVariant


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
        SSH_PORT = 22
        SSH_USER = self.usernames[SetupVariant.from_str(self.config.setup.location)]
        client = docker.DockerClient(
            base_url=f"ssh://{SSH_USER}@{ip_address}:{SSH_PORT}"
        )
        containers = client.containers.list()
        futures = []
        with ThreadPoolExecutor(max_workers=20) as executor:
            for container in containers:
                future = executor.submit(self._container_stats, container)
                futures.append(future)

        panels = []
        for future in as_completed(futures):
            stat = future.result()
            panel = Panel(stat, expand=True)
            panels.append(panel)

        self.console.print(Columns(panels))

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

    def _container_stats(self, container):
        stats = container.stats(stream=False)
        cpu_usage = stats["cpu_stats"]["cpu_usage"]["total_usage"]
        cpu_system = stats["cpu_stats"]["system_cpu_usage"]
        cpu_percent = (
            (cpu_usage / cpu_system)
            * len(stats["cpu_stats"]["cpu_usage"]["percpu_usage"])
            * 100.0
        )
        mem_usage = stats["memory_stats"]["usage"]
        mem_limit = stats["memory_stats"]["limit"]
        net_rx_bytes = stats["networks"]["eth0"]["rx_bytes"]
        net_tx_bytes = stats["networks"]["eth0"]["tx_bytes"]

        stat_result = (
            f"[b]Container: {container.name}[/b]\n"
            + f"[yellow]CPU Usage:[/yellow] {cpu_percent:.2f}%\n"
            + f"[yellow]Memory Usage:[/yellow] {mem_usage / 1024 / 1024:.2f} MB / {mem_limit / 1024 / 1024:.2f} MB\n"
            + f"[yellow]Network Usage:[/yellow] RX {net_rx_bytes / 1024 / 1024:.2f} MB / TX {net_tx_bytes / 1024 / 1024:.2f} MB\n"
        )
        return stat_result

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
