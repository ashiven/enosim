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


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    # Util classes (console, client, locks, etc.)

    console = providers.Factory(Console)
    client = providers.Factory(AsyncClient)
    thread_lock = providers.Factory(Lock)
    locks = providers.Singleton(
        dict,
        service=thread_lock,
        team=thread_lock,
        round_info=thread_lock,
    )

    # Setup

    team_gen = providers.Singleton(TeamGenerator, config=config.config)

    setup_helper = providers.Singleton(
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

    # Simulation

    flag_submitter = providers.Singleton(
        FlagSubmitter,
        setup=setup,
        console=console,
        verbose=config.verbose,
        debug=config.debug,
    )

    stat_checker = providers.Singleton(
        StatChecker,
        config=config.config,
        secrets=config.secrets,
        client=client,
        console=console,
        verbose=config.verbose,
    )

    orchestrator = providers.Singleton(
        Orchestrator,
        setup=setup,
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
        setup=setup,
        orchestrator=orchestrator,
        locks=locks,
        console=console,
        verbose=config.verbose,
        debug=config.debug,
    )

    # Flask

    flask_app = providers.Singleton(
        FlaskApp, setup=setup, simulation=simulation, locks=locks
    )
