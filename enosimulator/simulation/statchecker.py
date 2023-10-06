import docker
from rich.console import Console


class StatChecker:
    def __init__(self, setup):
        self.setup = setup
        self.console = Console()

    def check(self, ip_address, port):
        client = docker.DockerClient(base_url=f"tcp://{ip_address}:{port}")
        containers = client.containers.list()
        for container in containers:
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
            self.console.print(f"Container: {container.name}")
            self.console.print(f"CPU Usage: {cpu_percent:.2f}%")
            self.console.print(
                f"Memory Usage: {mem_usage / 1024 / 1024:.2f} MB / {mem_limit / 1024 / 1024:.2f} MB"
            )
            self.console.print(
                f"Network Usage: RX {net_rx_bytes / 1024 / 1024:.2f} MB / TX {net_tx_bytes / 1024 / 1024:.2f} MB"
            )
