import argparse
import os

from colorama import init
from dotenv import load_dotenv
from setup import Setup
from sim import Simulation


def main():
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

    setup = Setup(args.config, args.secrets, verbose=False)
    setup.configure()
    setup.build_infra()
    # setup.deploy()
    # setup.destroy()

    simulation = Simulation(setup)
    simulation.run()


if __name__ == "__main__":
    main()


# step 1: create requests session
# step 2: get service info from checker
# step 3: log service info inside of logfile
"""
def simulate_ctf(host, port, service_address, test_methods):

    s = requests.Session()
    retry_strategy = Retry( total=5, backoff_factor=1,)
    s.mount("http://", HTTPAdapter(max_retries=retry_strategy))

    r = s.get(f"http://{host}:{port}/service")
    if r.status_code != 200:
        raise Exception("Failed to get /service from checker")
    
    info: CheckerInfoMessage = jsons.loads(
        r.content, CheckerInfoMessage, key_transformer=jsons.KEY_TRANSFORMER_SNAKECASE
    )

    logging.info(
        "Testing service %s, flagVariants: %d, noiseVariants: %d, havocVariants: %d, exploitVariants: %d",
        info.service_name,
        info.flag_variants,
        info.noise_variants,
        info.havoc_variants,
        info.exploit_variants,
    )
"""
