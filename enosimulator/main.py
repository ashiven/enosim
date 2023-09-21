import argparse
import logging
import os
import sys

import jsons
import pytest
import requests
from enochecker_core import CheckerInfoMessage
from requests.adapters import HTTPAdapter
from setup import Setup
from urllib3.util.retry import Retry


def main():
    parser = argparse.ArgumentParser(
        prog="enosimulator",
        description="Simulating an A/D CTF competition",
    )
    parser.add_argument(
        "-c",
        "--config",
        help="A path to the config file containing service info and simulation setup info",
        default=os.environ.get("ENOSIMULATOR_CONFIG"),
    )

    args = parser.parse_args()

    if not args.config:
        parser.print_usage()
        raise Exception(
            "Please supply the path to a config file or set the ENOSIMULATOR_CONFIG environment variable"
        )

    setup = Setup()
    setup.configure(args.config)


"""
def simulate_ctf(host, port, service_address, test_methods):
    s = requests.Session()
    retry_strategy = Retry(
        total=5,
        backoff_factor=1,
    )
    s.mount("http://", HTTPAdapter(max_retries=retry_strategy))
    r = s.get(f"http://{host}:{port}/service")
    if r.status_code != 200:
        raise Exception("Failed to get /service from checker")
    print(r.content)
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

    test_args = [
        f"--checker-address={host}",
        f"--checker-port={port}",
        f"--service-address={service_address}",
        f"--flag-variants={info.flag_variants}",
        f"--noise-variants={info.noise_variants}",
        f"--havoc-variants={info.havoc_variants}",
        f"--exploit-variants={info.exploit_variants}",
        "--durations=0",
        "-v",
    ]

    if test_methods is None or len(test_methods) == 0:
        test_args.append(os.path.join(os.path.dirname(__file__), "tests.py"))
    else:
        for method in test_methods:
            test_args.append(
                os.path.join(os.path.dirname(__file__), "tests.py") + "::" + method
            )

    sys.exit(pytest.main(test_args))
"""
