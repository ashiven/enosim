import os
from threading import Lock
from unittest.mock import Mock

from dependency_injector import providers
from pyfakefs.fake_filesystem_unittest import Patcher
from pytest import fixture

from enosimulator.containers import (
    BackendContainer,
    SetupContainer,
    SimulationContainer,
)
from enosimulator.types_ import Config, Experience, IpAddresses, Secrets, Service, Team

pytest_plugins = ("pytest_asyncio", "aiofiles")

config = {
    "setup": {
        "ssh-config-path": "C:/Users/janni/.ssh/simconfig",
        "location": "hetzner",
        "vm-sizes": {
            "vulnbox": "cx11",
            "checker": "cx11",
            "engine": "cx11",
        },
        "vm-image-references": {
            "vulnbox": "vulnbox-checker",
            "checker": "vulnbox-checker",
            "engine": "engine",
        },
    },
    "settings": {
        "duration-in-minutes": 2,
        "teams": 3,
        "services": [
            "enowars7-service-CVExchange",
            "enowars7-service-bollwerk",
        ],
        "checker-ports": [7331, 6008],
        "simulation-type": "stress-test",
        "scoreboard-file": "",
    },
    "ctf-json": {
        "title": "ctf-sim",
        "flag-validity-in-rounds": 2,
        "checked-rounds-per-round": 3,
        "round-length-in-seconds": 60,
    },
}
secrets = {
    "vm-secrets": {
        "github-personal-access-token": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u",
        "ssh-public-key-path": "/path/to/your/public_key.pub",
        "ssh-private-key-path": "/path/to/your/private_key",
    },
    "cloud-secrets": {
        "azure-service-principal": {
            "subscription-id": "",
            "client-id": "",
            "client-secret": "",
            "tenant-id": "",
        },
        "hetzner-api-token": "a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6q7r8s9t0u",
    },
}
verbose = False
debug = False


@fixture
def mock_fs():
    with Patcher() as patcher:
        yield patcher.fs


@fixture
def test_setup_dir():
    test_setup_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../enosimulator/infra")
    ).replace("\\", "/")
    return test_setup_dir


@fixture
def backend_path():
    backend_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../enosimulator/backend")
    ).replace("\\", "/")
    return backend_path


@fixture
def setup_container():
    setup_container = SetupContainer()
    setup_container.configuration.config.from_dict(config)
    setup_container.configuration.secrets.from_dict(secrets)
    return setup_container


@fixture
def simulation_container():
    public_ips = {
        "vulnbox1": "234.123.12.32",
        "checker": "123.32.32.21",
        "engine": "123.32.23.21",
    }
    private_ips = {
        "vulnbox1": "10.1.1.1",
        "checker": "10.1.4.1",
        "engine": "10.1.5.1",
    }
    ip_addresses = IpAddresses(public_ips, private_ips)

    teams = {
        "TestTeam1": Team(
            id=1,
            name="TestTeam1",
            team_subnet="::ffff:10.1.1.0",
            address="10.1.1.1",
            experience=Experience.TEST_NOOB,
            exploiting={
                "CVExchange": {
                    "Flagstore0": True,
                    "Flagstore1": True,
                    "Flagstore2": False,
                }
            },
            patched={
                "CVExchange": {
                    "Flagstore0": False,
                    "Flagstore1": False,
                    "Flagstore2": False,
                }
            },
            points=0.0,
            gain=0.0,
        ),
        "TestTeam2": Team(
            id=2,
            name="TestTeam2",
            team_subnet="::ffff:10.1.2.0",
            address="10.1.2.1",
            experience=Experience.TEST_BEGINNER,
            exploiting={
                "CVExchange": {
                    "Flagstore0": False,
                    "Flagstore1": False,
                    "Flagstore2": False,
                }
            },
            patched={
                "CVExchange": {
                    "Flagstore0": False,
                    "Flagstore1": False,
                    "Flagstore2": False,
                }
            },
            points=0.0,
            gain=0.0,
        ),
        "TestTeam3": Team(
            id=3,
            name="TestTeam3",
            team_subnet="::ffff:10.1.3.0",
            address="10.1.3.1",
            experience=Experience.TEST_PRO,
            exploiting={
                "CVExchange": {
                    "Flagstore0": False,
                    "Flagstore1": False,
                    "Flagstore2": False,
                }
            },
            patched={
                "CVExchange": {
                    "Flagstore0": False,
                    "Flagstore1": False,
                    "Flagstore2": False,
                }
            },
            points=0.0,
            gain=0.0,
        ),
    }

    services = {
        "enowars7-service-CVExchange": Service(
            id=1,
            name="enowars7-service-CVExchange",
            flags_per_round_multiplier=1,
            noises_per_round_multiplier=1,
            havocs_per_round_multiplier=1,
            weight_factor=1,
            checkers=["http://234.123.12.32:7331"],
        )
    }

    setup_container = SetupContainer()
    setup_container.override_providers(
        setup=providers.Factory(
            Mock,
            config=Config.from_(config),
            secrets=Secrets.from_(secrets),
            ips=ip_addresses,
            teams=teams,
            services=services,
        )
    )
    setup_container.configuration.config.from_dict(config)
    setup_container.configuration.secrets.from_dict(secrets)

    thread_lock = providers.Factory(Lock)
    locks = providers.Singleton(
        dict, service=thread_lock, team=thread_lock, round_info=thread_lock
    )

    simulation_container = SimulationContainer(
        locks=locks,
        setup_container=setup_container,
    )
    simulation_container.configuration.config.from_dict(config)
    simulation_container.configuration.secrets.from_dict(secrets)
    simulation_container.configuration.verbose.from_value(verbose)
    simulation_container.configuration.debug.from_value(debug)
    return simulation_container


@fixture
def backend_container(setup_container, simulation_container):
    thread_lock = providers.Factory(Lock)
    locks = providers.Singleton(
        dict, service=thread_lock, team=thread_lock, round_info=thread_lock
    )

    backend_container = BackendContainer(
        locks=locks,
        setup_container=setup_container,
        simulation_container=simulation_container,
    )

    return backend_container
