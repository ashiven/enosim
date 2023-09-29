import argparse
import asyncio
import os

from colorama import init
from dotenv import load_dotenv
from setup import Setup
from sim import Simulation


async def main():
    load_dotenv()
    init(autoreset=True)
    dir_path = os.path.dirname(os.path.abspath(__file__)).replace("\\", "/")

    parser = argparse.ArgumentParser(
        prog="enosimulator",
        description="Simulating an A/D CTF competition",
    )
    parser.add_argument(
        "-c",
        "--config",
        help="A path to the config file containing service info and simulation setup info",
        default=os.environ.get(
            "ENOSIMULATOR_CONFIG", f"{dir_path}/../config/config.json"
        ),
    )
    parser.add_argument(
        "-s",
        "--secrets",
        help="A path to the secrets file containing ssh key paths and login credentials for cloud providers",
        default=os.environ.get(
            "ENOSIMULATOR_SECRETS", f"{dir_path}/../config/secrets.json"
        ),
    )
    args = parser.parse_args()

    if not args.config:
        parser.print_usage()
        raise Exception(
            "Please supply the path to a config file or set the ENOSIMULATOR_CONFIG environment variable"
        )
    if not args.secrets:
        parser.print_usage()
        raise Exception(
            "Please supply the path to a secrets file or set the ENOSIMULATOR_SECRETS environment variable"
        )

    setup = await Setup.new(args.config, args.secrets, verbose=False)
    await setup.configure()
    await setup.build_infra()
    # TODO: - uncomment in production
    # setup.deploy()

    simulation = await Simulation.new(setup)
    simulation.run()

    setup.destroy()


if __name__ == "__main__":
    asyncio.run(main())
