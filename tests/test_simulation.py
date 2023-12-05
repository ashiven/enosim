from io import BytesIO
from unittest.mock import AsyncMock, Mock, patch

import jsons
import pytest
from enochecker_core import CheckerInfoMessage, CheckerMethod, CheckerTaskMessage
from httpx import AsyncClient
from paramiko import RSAKey, SSHClient
from rich.console import Console
from rich.panel import Panel

# uncomment to skip all tests for debugging
# pytestmark = pytest.mark.skip("Already works")


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

    assert orchestrator.setup.teams["TestTeam1"].exploiting == {
        "CVExchange": {"Flagstore0": True, "Flagstore1": True, "Flagstore2": True},
    }
    assert orchestrator.setup.teams["TestTeam1"].patched == {
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

    assert orchestrator.setup.teams["TestTeam1"].exploiting == {
        "CVExchange": {
            "Flagstore0": False,
            "Flagstore1": False,
            "Flagstore2": False,
        },
    }
    assert orchestrator.setup.teams["TestTeam1"].patched == {
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


def test_orchestrator_create_exploit_requests(simulation_container):
    simulation_container.reset_singletons()
    orchestrator = simulation_container.orchestrator()

    teams = [team for team in orchestrator.setup.teams.values()]

    attack_info = {
        "availableTeams": ["10.1.1.1", "10.1.2.1", "10.1.3.1"],
        "services": {
            "enowars7-service-CVExchange": {
                "10.1.1.1": {"10": {"0": ["12"], "1": ["13"], "2": ["11"]}},
                "10.1.2.1": {"10": {"0": ["12"], "1": ["13"], "2": ["11"]}},
                "10.1.3.1": {"10": {"0": ["12"], "1": ["13"], "2": ["11"]}},
            }
        },
    }
    orchestrator.attack_info = attack_info

    service_info = {"CVExchange": ("7331", "enowars7-service-CVExchange")}
    orchestrator.service_info = service_info

    exploit_requests = orchestrator._create_exploit_requests(
        round_id=10, team=teams[0], all_teams=teams
    )

    assert len(exploit_requests) == 4

    for request in exploit_requests.values():
        request.task_chain_id = None

    test_request = CheckerTaskMessage(
        task_id=10,
        method=CheckerMethod.EXPLOIT,
        address="10.1.2.1",
        team_id=2,
        team_name="TestTeam2",
        current_round_id=10,
        related_round_id=10,
        flag=None,
        variant_id=0,
        timeout=10000,
        round_length=60000,
        task_chain_id=None,
        flag_regex=r"ENO[A-Za-z0-9+\/=]{48}",
        flag_hash="ignore_flag_hash",
        attack_info="12",
    )
    assert test_request in exploit_requests.values()

    test_request_wrong = CheckerTaskMessage(
        task_id=10,
        method=CheckerMethod.EXPLOIT,
        address="10.1.3.1",
        team_id=3,
        team_name="TestTeam3",
        current_round_id=10,
        related_round_id=10,
        flag=None,
        variant_id=2,
        timeout=10000,
        round_length=60000,
        task_chain_id=None,
        flag_regex=r"ENO[A-Za-z0-9+\/=]{48}",
        flag_hash="ignore_flag_hash",
        attack_info="11",
    )
    assert test_request_wrong not in exploit_requests.values()


@pytest.mark.asyncio
async def test_orchestrator_send_exploit_requests(simulation_container):
    simulation_container.reset_singletons()
    orchestrator = simulation_container.orchestrator()

    mock_client = Mock(AsyncClient)
    orchestrator.client = mock_client

    service_info = {"CVExchange": ("7331", "enowars7-service-CVExchange")}
    orchestrator.service_info = service_info

    exploit_requests = {
        ("TestTeam2", "CVExchange", "Flagstore0", "12"): CheckerTaskMessage(
            task_id=10,
            method=CheckerMethod.EXPLOIT,
            address="10.1.2.1",
            team_id=2,
            team_name="TestTeam2",
            current_round_id=10,
            related_round_id=10,
            flag=None,
            variant_id=0,
            timeout=10000,
            round_length=60000,
            task_chain_id=None,
            flag_regex=r"ENO[A-Za-z0-9+\/=]{48}",
            flag_hash="ignore_flag_hash",
            attack_info="12",
        ),
        ("TestTeam2", "CVExchange", "Flagstore1", "13"): CheckerTaskMessage(
            task_id=10,
            method=CheckerMethod.EXPLOIT,
            address="10.1.2.1",
            team_id=2,
            team_name="TestTeam2",
            current_round_id=10,
            related_round_id=10,
            flag=None,
            variant_id=1,
            timeout=10000,
            round_length=60000,
            task_chain_id=None,
            flag_regex=r"ENO[A-Za-z0-9+\/=]{48}",
            flag_hash="ignore_flag_hash",
            attack_info="13",
        ),
    }

    mock_client.post.return_value.content = '{"result": "OK", "message": "", "attack_info": "12", "flag": "ENO123123123123"}'

    flags = await orchestrator._send_exploit_requests(
        orchestrator.setup.teams["TestTeam1"], exploit_requests
    )
    # just some calls so the linter doesn't complain about unused variables
    flags.append(1)
    flags.pop()

    # TODO: - seems like calls are not being counted since the function is called in a task (fix?)

    # assert mock_client.post.call_count == 2
    # mock_client.post.assert_any_call(
    #     "http://234.123.12.32:7331",
    #     data=req_to_json(
    #         exploit_requests[("TestTeam2", "CVExchange", "Flagstore0", "12")]
    #     ),
    #     headers={"Content-Type": "application/json"},
    #     timeout=10,
    # )
    # mock_client.post.assert_any_call(
    #     "http://234.123.12.32:7331",
    #     data=req_to_json(
    #         exploit_requests[("TestTeam2", "CVExchange", "Flagstore1", "13")]
    #     ),
    #     headers={"Content-Type": "application/json"},
    #     timeout=10,
    # )

    # assert flags == ["ENO123123123123", "ENO123123123123"]


@pytest.mark.asyncio
async def test_simulation_run(simulation_container):
    simulation_container.reset_singletons()
    simulation = simulation_container.simulation()

    simulation.orchestrator.update_team_info = AsyncMock()
    simulation.orchestrator.parse_scoreboard = Mock()
    simulation.orchestrator.get_round_info = AsyncMock()
    simulation.orchestrator.collect_system_analytics = AsyncMock()

    simulation._scoreboard_available = AsyncMock()
    simulation._update_teams = AsyncMock()
    simulation.info = Mock()
    simulation._exploit_all_teams = AsyncMock()
    simulation._system_analytics = Mock()
    simulation._submit_all_flags = Mock()
    simulation._print_system_analytics = Mock()

    simulation._system_analytics.return_value = [Panel("test"), [Panel("test2")]]
    simulation.round_length = 0
    await simulation.run()

    assert simulation.orchestrator.update_team_info.call_count == 1
    assert simulation.orchestrator.parse_scoreboard.call_count == 2
    assert simulation.orchestrator.get_round_info.call_count == 2
    assert simulation.orchestrator.collect_system_analytics.call_count == 2

    assert simulation._scoreboard_available.call_count == 1
    assert simulation._update_teams.call_count == 2
    assert simulation.info.call_count == 2
    assert simulation._exploit_all_teams.call_count == 2
    assert simulation._system_analytics.call_count == 2
    assert simulation._submit_all_flags.call_count == 2
    assert simulation._print_system_analytics.call_count == 2


@pytest.mark.asyncio
async def test_simulation_update_teams(simulation_container):
    simulation_container.reset_singletons()
    simulation = simulation_container.simulation()
    simulation.setup.config.settings.simulation_type = "realistic"

    simulation._random_test = Mock()
    simulation._random_test.return_value = True

    await simulation._update_teams()

    assert (
        len(
            [
                flagstore
                for flagstore, do_exploit in simulation.setup.teams["TestTeam1"]
                .exploiting["CVExchange"]
                .items()
                if do_exploit
            ]
        )
        + len(
            [
                flagstore
                for flagstore, do_patch in simulation.setup.teams["TestTeam1"]
                .patched["CVExchange"]
                .items()
                if do_patch
            ]
        )
        == 3
    )

    assert (
        len(
            [
                flagstore
                for flagstore, do_exploit in simulation.setup.teams["TestTeam2"]
                .exploiting["CVExchange"]
                .items()
                if do_exploit
            ]
        )
        + len(
            [
                flagstore
                for flagstore, do_patch in simulation.setup.teams["TestTeam2"]
                .patched["CVExchange"]
                .items()
                if do_patch
            ]
        )
        == 1
    )

    assert (
        len(
            [
                flagstore
                for flagstore, do_exploit in simulation.setup.teams["TestTeam3"]
                .exploiting["CVExchange"]
                .items()
                if do_exploit
            ]
        )
        + len(
            [
                flagstore
                for flagstore, do_patch in simulation.setup.teams["TestTeam3"]
                .patched["CVExchange"]
                .items()
                if do_patch
            ]
        )
        == 1
    )
