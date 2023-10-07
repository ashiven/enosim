from concurrent.futures import ThreadPoolExecutor, as_completed

import docker
from rich.console import Console


class StatChecker:
    def __init__(self):
        self.console = Console()

    def check(self, ip_address, port):
        client = docker.DockerClient(base_url=f"tcp://{ip_address}:{port}")
        containers = client.containers.list()
        futures = []
        with ThreadPoolExecutor(max_workers=20) as executor:
            for container in containers:
                future = executor.submit(self._container_stats, container)
                futures.append(future)

        for future in as_completed(futures):
            self.console.print(future.result())

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
            f"Container: {container.name}\n"
            + f"CPU Usage: {cpu_percent:.2f}%\n"
            + f"Memory Usage: {mem_usage / 1024 / 1024:.2f} MB / {mem_limit / 1024 / 1024:.2f} MB\n"
            + f"Network Usage: RX {net_rx_bytes / 1024 / 1024:.2f} MB / TX {net_tx_bytes / 1024 / 1024:.2f} MB\n"
        )
        return stat_result
