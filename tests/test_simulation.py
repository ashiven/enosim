from io import BytesIO
from unittest.mock import Mock, patch

import jsons
import pytest
from enochecker_core import CheckerInfoMessage
from httpx import AsyncClient
from paramiko import RSAKey, SSHClient
from rich.console import Console
from rich.panel import Panel

from enosimulator.types_ import Experience, Team


def test_flag_submitter(simulation_container):
    flag_submitter = simulation_container.flag_submitter()

    flags = ["ENO123123123123", "ENO321321321321", "ENO231231231231231"]

    with patch.object(RSAKey, "from_private_key_file"):
        with patch.object(SSHClient, "connect") as mock_connect:
            with patch.object(SSHClient, "get_transport") as mock_get_transport:
                flag_submitter.submit_flags("10.1.1.1", flags)

        mock_connect.assert_called_once_with(
            hostname="234.123.12.32",
            username="root",
            pkey=RSAKey.from_private_key_file("/path/to/your/private_key"),
        )

    mock_get_transport.assert_called_once()

    mock_get_transport.return_value.open_channel.assert_called_once_with(
        "direct-tcpip", ("10.1.5.1", 1337), ("localhost", 0)
    )

    # TODO: - fix test
    # mock_get_transport.return_value.open_channel.return_value.send.assert_called_once_with(
    #     b"ENO123123123123\nENO321321321321\nENO231231231231231\n"
    # )


def test_stat_checker_container_stats(simulation_container):
    simulation_container.reset_singletons()
    stat_checker = simulation_container.stat_checker()

    with patch.object(RSAKey, "from_private_key_file"):
        with patch.object(SSHClient, "connect") as mock_connect:
            with patch.object(SSHClient, "exec_command") as mock_exec_command:
                mock_exec_command.return_value = (
                    None,
                    BytesIO(
                        b"CONTAINER ID        NAME                CPU %               MEM USAGE / LIMIT     MEM %               NET I/O             BLOCK I/O           PIDS\n"
                        + b"a1b2c3d4e5f6        my_container1       0.07%               4.883MiB / 1.952GiB   0.24%               648B / 0B           12.3MB / 0B         2\n"
                        + b"b2c3d4e5f6a7        my_container2       0.10%               2.211MiB / 1.952GiB   0.11%               648B / 0B           4.987MB / 0B        2\n"
                    ),
                    None,
                )

                stat_panel = stat_checker._container_stats("engine", "123.32.123.21")

        mock_connect.assert_called_once_with(
            hostname="123.32.123.21",
            username="root",
            pkey=RSAKey.from_private_key_file("/path/to/your/private_key"),
        )

    assert stat_checker.container_stats["engine"]["my_container1"] == {
        "name": "my_container1",
        "cpuusage": 0.07,
        "ramusage": 0.24,
        "netrx": 648,
        "nettx": 0,
    }
    assert stat_checker.container_stats["engine"]["my_container2"] == {
        "name": "my_container2",
        "cpuusage": 0.1,
        "ramusage": 0.11,
        "netrx": 648,
        "nettx": 0,
    }

    assert isinstance(stat_panel, Panel)


def test_stat_checker_system_stats(simulation_container):
    simulation_container.reset_singletons()
    stat_checker = simulation_container.stat_checker()

    with patch.object(RSAKey, "from_private_key_file"):
        with patch.object(SSHClient, "connect") as mock_connect:
            with patch.object(SSHClient, "exec_command") as mock_exec_command:

                def return_value(param):
                    if (
                        param
                        == "sar -n DEV 1 1 | grep 'Average' | grep 'eth0' | awk '{print $5, $6}'"
                    ):
                        return (
                            None,
                            BytesIO(b"0.07 0.24"),
                            None,
                        )
                    else:
                        return (
                            None,
                            BytesIO(b"23.45\n7982\n1873\n2.34\n8\n49G"),
                            None,
                        )

                mock_exec_command.side_effect = return_value

                stat_panels = stat_checker._system_stats("engine", "123.32.123.21")

        mock_connect.assert_called_once_with(
            hostname="123.32.123.21",
            username="root",
            pkey=RSAKey.from_private_key_file("/path/to/your/private_key"),
        )

    assert stat_checker.vm_stats["engine"] == {
        "name": "engine",
        "ip": "123.32.123.21",
        "cpu": 8,
        "ram": 7.79,
        "disk": 49,
        "status": "online",
        "uptime": 1,
        "cpuusage": 2.34,
        "ramusage": 23.45,
        "netrx": 0.07,
        "nettx": 0.24,
    }

    assert isinstance(stat_panels, list)
    assert isinstance(stat_panels[0], Panel)
    assert isinstance(stat_panels[1], Panel)
    assert isinstance(stat_panels[2], Panel)


@pytest.mark.asyncio
async def test_stat_checker_system_analytics(simulation_container):
    stat_checker = simulation_container.stat_checker()
    mock_client = Mock(AsyncClient)
    stat_checker.client = mock_client

    vm_stats = {
        "vulnbox1": {
            "name": "vulnbox1",
            "ip": "234.123.12.32",
            "cpu": 2,
            "ram": 4.5,
            "disk": 20.1,
            "status": "online",
            "uptime": 123,
            "cpuusage": 0.1,
            "ramusage": 0.2,
            "netrx": 0.3,
            "nettx": 0.4,
        }
    }

    container_stats = {
        "vulnbox1": {
            "test_container": {
                "name": "test_container",
                "cpuusage": 0.3,
                "ramusage": 0.4,
                "netrx": 0.5,
                "nettx": 0.6,
            }
        }
    }
    stat_checker.vm_stats = vm_stats
    stat_checker.container_stats = container_stats

    await stat_checker.system_analytics()

    mock_client.post.assert_any_call(
        "http://localhost:5000/vminfo", json=vm_stats["vulnbox1"]
    )
    mock_client.post.assert_any_call(
        "http://localhost:5000/containerinfo",
        json=container_stats["vulnbox1"]["test_container"],
    )


@pytest.mark.asyncio
async def test_orchestrator_update_teams(simulation_container):
    simulation_container.reset_singletons()
    orchestrator = simulation_container.orchestrator()
    mock_client = Mock(AsyncClient)
    orchestrator.client = mock_client
    mock_client.get.return_value = Mock(status_code=200)

    with patch.object(jsons, "loads") as mock_loads:
        mock_loads.return_value = CheckerInfoMessage(
            service_name="CVExchange",
            flag_variants=3,
            noise_variants=3,
            havoc_variants=1,
            exploit_variants=3,
        )
        await orchestrator.update_team_info()

    mock_client.get.assert_called_once_with("http://234.123.12.32:7331/service")
    assert mock_loads.call_count == 1
    assert orchestrator.service_info["CVExchange"] == (
        "7331",
        "enowars7-service-CVExchange",
    )

    assert orchestrator.setup.teams["TestTeam"].exploiting == {
        "CVExchange": {"Flagstore0": True, "Flagstore1": True, "Flagstore2": True},
    }
    assert orchestrator.setup.teams["TestTeam"].patched == {
        "CVExchange": {
            "Flagstore0": False,
            "Flagstore1": False,
            "Flagstore2": False,
        },
    }

    orchestrator.setup.config.settings.simulation_type = "realistic"
    with patch.object(jsons, "loads") as mock_loads:
        mock_loads.return_value = CheckerInfoMessage(
            service_name="CVExchange",
            flag_variants=3,
            noise_variants=3,
            havoc_variants=1,
            exploit_variants=3,
        )
        await orchestrator.update_team_info()

    assert orchestrator.setup.teams["TestTeam"].exploiting == {
        "CVExchange": {
            "Flagstore0": False,
            "Flagstore1": False,
            "Flagstore2": False,
        },
    }
    assert orchestrator.setup.teams["TestTeam"].patched == {
        "CVExchange": {
            "Flagstore0": False,
            "Flagstore1": False,
            "Flagstore2": False,
        },
    }


def test_orchestrator_parse_scoreboard(simulation_container):
    simulation_container.reset_singletons()
    orchestrator = simulation_container.orchestrator()

    mock_client = Mock(AsyncClient)
    orchestrator.client = mock_client
    mock_client.get.return_value = Mock(status_code=200)

    teams = {
        "TestTeam1": Team(
            id=1,
            name="TestTeam1",
            team_subnet="::ffff:10.1.1.0",
            address="10.1.1.1",
            experience=Experience.NOOB,
            exploiting=dict(),
            patched=dict(),
            points=0.0,
            gain=0.0,
        ),
        "TestTeam2": Team(
            id=1,
            name="TestTeam2",
            team_subnet="::ffff:10.1.1.0",
            address="10.1.2.1",
            experience=Experience.BEGINNER,
            exploiting=dict(),
            patched=dict(),
            points=0.0,
            gain=0.0,
        ),
        "TestTeam3": Team(
            id=1,
            name="TestTeam3",
            team_subnet="::ffff:10.1.1.0",
            address="10.1.3.1",
            experience=Experience.PRO,
            exploiting=dict(),
            patched=dict(),
            points=0.0,
            gain=0.0,
        ),
    }
    orchestrator.setup.teams = teams

    # TODO: - maybe fix test
    # with patch.object(webdriver, "Chrome") as mock_chrome:
    #     with patch.object(ChromeDriverManager, "install") as mock_install:
    #         with patch.object(
    #             webdriver.support.ui.WebDriverWait, "until"
    #         ) as mock_until:
    #             with patch("simulation.orchestrator.BeautifulSoup") as mock_soup:
    #                 mock_install.return_value = "/path/to/chromedriver"
    #                 mock_soup.return_value.find_all.return_value = [
    #                     "<tr class='otherrow'><td class='team-score'>234.43</td><div class='team-name'><a>TestTeam1</a></div></tr>",
    #                     "<tr class='otherrow'><td class='team-score'>432.43</td><div class='team-name'><a>TestTeam2</a></div></tr>",
    #                     "<tr class='otherrow'><td class='team-score'>500002</td><div class='team-name'><a>TestTeam3</a></div></tr>",
    #                 ]

    with patch.object(Console, "status"):
        with patch(
            "simulation.orchestrator.Orchestrator._get_team_scores"
        ) as mock_get_scores:
            mock_get_scores.return_value = {
                "TestTeam1": (234.43, 99.3),
                "TestTeam2": (432.43, 23.9),
                "TestTeam3": (500002, 20.3),
            }
            orchestrator.parse_scoreboard()

    assert orchestrator.setup.teams["TestTeam1"].points == 234.43
    assert orchestrator.setup.teams["TestTeam2"].points == 432.43
    assert orchestrator.setup.teams["TestTeam3"].points == 500002

    assert orchestrator.setup.teams["TestTeam1"].gain == 99.3
    assert orchestrator.setup.teams["TestTeam2"].gain == 23.9
    assert orchestrator.setup.teams["TestTeam3"].gain == 20.3
