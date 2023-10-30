from threading import Lock

from backend.app import FlaskApp
from dependency_injector import containers, providers
from httpx import AsyncClient
from rich.console import Console
from setup.setup import Setup
from setup.setup_helper.setup_helper import SetupHelper, TeamGenerator
from simulation.flagsubmitter import FlagSubmitter
from simulation.orchestrator import Orchestrator
from simulation.simulation import Simulation
from simulation.statchecker import StatChecker


class SetupContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    console = providers.Dependency(instance_of=Console)

    team_gen = providers.Factory(TeamGenerator, config=config.config)

    setup_helper = providers.Factory(
        SetupHelper,
        config=config.config,
        secrets=config.secrets,
        team_gen=team_gen,
    )

    setup = providers.Singleton(
        Setup,
        config=config.config,
        secrets=config.secrets,
        setup_helper=setup_helper,
        console=console,
    )


class SimulationContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    setup_container = providers.DependenciesContainer()
    console = providers.Dependency(instance_of=Console)
    client = providers.Dependency(instance_of=AsyncClient)
    locks = providers.Dependency(instance_of=dict)

    flag_submitter = providers.Factory(
        FlagSubmitter,
        setup=setup_container.setup,
        console=console,
        verbose=config.verbose,
        debug=config.debug,
    )

    stat_checker = providers.Factory(
        StatChecker,
        config=config.config,
        secrets=config.secrets,
        client=client,
        console=console,
        verbose=config.verbose,
    )

    orchestrator = providers.Factory(
        Orchestrator,
        setup=setup_container.setup,
        locks=locks,
        client=client,
        flag_submitter=flag_submitter,
        stat_checker=stat_checker,
        console=console,
        verbose=config.verbose,
        debug=config.debug,
    )

    simulation = providers.Singleton(
        Simulation,
        setup=setup_container.setup,
        orchestrator=orchestrator,
        locks=locks,
        console=console,
        verbose=config.verbose,
        debug=config.debug,
    )


class BackendContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    setup_container = providers.DependenciesContainer()
    simulation_container = providers.DependenciesContainer()
    locks = providers.Dependency(instance_of=dict)

    flask_app = providers.Factory(
        FlaskApp,
        setup=setup_container.setup,
        simulation=simulation_container.simulation,
        locks=locks,
    )


class Application(containers.DeclarativeContainer):
    config = providers.Configuration()

    console = providers.Factory(Console)
    client = providers.Factory(AsyncClient)
    thread_lock = providers.Factory(Lock)
    locks = providers.Singleton(
        dict,
        service_lock=thread_lock,
        team_lock=thread_lock,
        round_info_lock=thread_lock,
    )

    setup_container = providers.Container(
        SetupContainer, config=config, console=console
    )

    simulation_container = providers.Container(
        SimulationContainer,
        config=config,
        setup_container=setup_container,
        console=console,
        client=client,
        locks=locks,
    )

    backend_container = providers.Container(
        BackendContainer,
        config=config,
        setup_container=setup_container,
        simulation_container=simulation_container,
        locks=locks,
    )
