from threading import Lock

from backend.app import FlaskApp
from dependency_injector import containers, providers
from rich.console import Console
from setup.setup import Setup
from setup.setup_helper import SetupHelper, TeamGenerator
from simulation.simulation import Simulation


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    # Setup
    console = providers.Factory(Console)

    team_generator = providers.Factory(TeamGenerator, config=config.config)

    setup_helper = providers.Factory(
        SetupHelper,
        config=config.config,
        secrets=config.secrets,
        team_generator=team_generator,
    )

    setup = providers.Factory(
        Setup,
        config=config.config,
        secrets=config.secrets,
        setup_helper=setup_helper,
        console=console,
    )

    # Locks

    service_lock = providers.Factory(Lock)

    team_lock = providers.Factory(Lock)

    round_info_lock = providers.Factory(Lock)

    # Simulation

    simulation = providers.Factory(Simulation, setup=setup)

    # Flask

    flask_app = providers.Factory(FlaskApp, setup=setup, simulation=simulation)
