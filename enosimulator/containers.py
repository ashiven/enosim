from threading import Lock

from backend import FlaskApp
from dependency_injector import containers, providers
from httpx import AsyncClient
from rich.console import Console
from setup import Setup
from setup.setup_helper import SetupHelper, TeamGenerator
from simulation import FlagSubmitter, Orchestrator, Simulation, StatChecker
from types_ import Config, Secrets


class SetupContainer(containers.DeclarativeContainer):
    """
    Container for setup related classes.

    This container is used to inject dependencies into the setup module.
    """

    configuration = providers.Configuration()

    console = providers.Singleton(Console)
    config = providers.Singleton(Config.from_, configuration.config)
    secrets = providers.Singleton(Secrets.from_, configuration.secrets)

    team_generator = providers.Singleton(TeamGenerator, config=config)

    setup_helper = providers.Singleton(
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
    """
    Container for simulation related classes.

    This container is used to inject dependencies into the simulation module.
    """

    configuration = providers.Configuration()

    setup_container = providers.DependenciesContainer()
    locks = providers.Dependency(instance_of=dict)

    console = providers.Singleton(Console)
    client = providers.Singleton(AsyncClient)
    config = providers.Singleton(Config.from_, configuration.config)
    secrets = providers.Singleton(Secrets.from_, configuration.secrets)

    flag_submitter = providers.Singleton(
        FlagSubmitter,
        setup=setup_container.setup,
        console=console,
        verbose=configuration.verbose,
        debug=configuration.debug,
    )

    stat_checker = providers.Singleton(
        StatChecker,
        config=config,
        secrets=secrets,
        client=client,
        console=console,
        verbose=configuration.verbose,
    )

    orchestrator = providers.Singleton(
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
    """
    Container for backend related classes.

    This container is used to inject dependencies into the backend module.
    """

    setup_container = providers.DependenciesContainer()
    simulation_container = providers.DependenciesContainer()
    locks = providers.Dependency(instance_of=dict)

    flask_app = providers.Singleton(
        FlaskApp,
        setup=setup_container.setup,
        simulation=simulation_container.simulation,
        locks=locks,
    )


class Application(containers.DeclarativeContainer):
    """
    Container for the whole application.

    This container is used to instantiate every component of the application.
    """

    configuration = providers.Configuration()

    thread_lock = providers.Factory(Lock)
    locks = providers.Singleton(
        dict,
        service=thread_lock,
        team=thread_lock,
        round_info=thread_lock,
    )

    setup_container = providers.Container(
        SetupContainer,
        configuration=configuration,
    )

    simulation_container = providers.Container(
        SimulationContainer,
        configuration=configuration,
        setup_container=setup_container,
        locks=locks,
    )

    backend_container = providers.Container(
        BackendContainer,
        setup_container=setup_container,
        simulation_container=simulation_container,
        locks=locks,
    )
