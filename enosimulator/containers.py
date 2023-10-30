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
from types_ import Config, Secrets


class SetupContainer(containers.DeclarativeContainer):
    console = providers.Dependency(instance_of=Console)
    config = providers.Dependency(instance_of=Config)
    secrets = providers.Dependency(instance_of=Secrets)

    team_generator = providers.Factory(TeamGenerator, config=config)

    setup_helper = providers.Factory(
        SetupHelper,
        config=config,
        secrets=secrets,
        team_generator=team_generator,
    )

    setup = providers.Singleton(
        Setup,
        config=config,
        secrets=secrets,
        setup_helper=setup_helper,
        console=console,
    )


class SimulationContainer(containers.DeclarativeContainer):
    configuration = providers.Configuration()

    setup_container = providers.DependenciesContainer()
    console = providers.Dependency(instance_of=Console)
    client = providers.Dependency(instance_of=AsyncClient)
    locks = providers.Dependency(instance_of=dict)
    config = providers.Dependency(instance_of=Config)
    secrets = providers.Dependency(instance_of=Secrets)

    flag_submitter = providers.Factory(
        FlagSubmitter,
        setup=setup_container.setup,
        console=console,
        verbose=configuration.verbose,
        debug=configuration.debug,
    )

    stat_checker = providers.Factory(
        StatChecker,
        config=config,
        secrets=secrets,
        client=client,
        console=console,
        verbose=configuration.verbose,
    )

    orchestrator = providers.Factory(
        Orchestrator,
        setup=setup_container.setup,
        locks=locks,
        client=client,
        flag_submitter=flag_submitter,
        stat_checker=stat_checker,
        console=console,
        verbose=configuration.verbose,
        debug=configuration.debug,
    )

    simulation = providers.Singleton(
        Simulation,
        setup=setup_container.setup,
        orchestrator=orchestrator,
        locks=locks,
        console=console,
        verbose=configuration.verbose,
        debug=configuration.debug,
    )


class BackendContainer(containers.DeclarativeContainer):
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
    configuration = providers.Configuration()

    console = providers.Factory(Console)
    client = providers.Factory(AsyncClient)
    thread_lock = providers.Factory(Lock)
    config = providers.Singleton(Config.from_, configuration.config)
    secrets = providers.Singleton(Secrets.from_, configuration.secrets)

    locks = providers.Dict(
        service=thread_lock,
        team=thread_lock,
        round_info=thread_lock,
    )

    setup_container = providers.Container(
        SetupContainer,
        config=config,
        secrets=secrets,
        console=console,
    )

    simulation_container = providers.Container(
        SimulationContainer,
        configuration=configuration,
        setup_container=setup_container,
        console=console,
        client=client,
        locks=locks,
        config=config,
        secrets=secrets,
    )

    backend_container = providers.Container(
        BackendContainer,
        setup_container=setup_container,
        simulation_container=simulation_container,
        locks=locks,
    )
