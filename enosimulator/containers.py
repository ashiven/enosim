from threading import Lock

import httpx
from backend.app import FlaskApp
from dependency_injector import containers, providers
from rich.console import Console
from setup.setup import Setup
from setup.setup_helper import SetupHelper, TeamGenerator
from simulation.flagsubmitter import FlagSubmitter
from simulation.orchestrator import Orchestrator
from simulation.simulation import Simulation
from simulation.statchecker import StatChecker


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    # Util classes (console, client, locks, etc.)

    console = providers.Factory(Console)

    client = providers.Factory(httpx.AsyncClient)

    thread_lock = providers.Factory(Lock)

    # this object gets created once and then gets reused on later calls
    locks = providers.Singleton(
        dict,
        service_lock=thread_lock,
        team_lock=thread_lock,
        round_info_lock=thread_lock,
    )

    # Setup

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

    # Simulation

    flag_submitter = providers.Factory(
        FlagSubmitter,
        ip_addresses=setup.ip_addresses,
        config=config.config,
        secrets=config.secrets,
        verbose=config.args.verbose,
        debug=config.args.debug,
    )

    stat_checker = providers.Factory(
        StatChecker,
        config=config.config,
        secrets=config.secrets,
        client=client,
        console=console,
        verbose=config.args.verbose,
    )

    orchestrator = providers.Factory(
        Orchestrator,
        setup=setup,
        locks=locks,
        client=client,
        flag_submitter=flag_submitter,
        stat_checker=stat_checker,
        console=console,
        verbose=config.args.verbose,
        debug=config.args.debug,
    )

    simulation = providers.Singleton(
        Simulation.new,
        setup=setup,
        locks=locks,
        orchestrator=orchestrator,
        verbose=config.args.verbose,
        debug=config.args.debug,
    )

    # Flask

    flask_app = providers.Factory(FlaskApp, setup=setup, simulation=simulation)
