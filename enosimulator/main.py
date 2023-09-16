import secrets
from typing import Optional
from enochecker_core import (
    CheckerInfoMessage,
    CheckerMethod,
    CheckerResultMessage,
    CheckerTaskMessage,
    CheckerTaskResult,
)
import jsons
import requests

global_round_id = 0
FLAG_REGEX_ASCII = r"ENO[A-Za-z0-9+\/=]{48}"
FLAG_REGEX_UTF8 = r"🥺[A-Za-z0-9+\/=]{48}🥺🥺"
REQUEST_TIMEOUT = 10
CHAIN_ID_PREFIX = secrets.token_hex(20)


def _create_request_message(
    method: str,
    round_id: int,
    variant_id: int,
    service_address: str,
    flag: Optional[str] = None,
    unique_variant_index: Optional[int] = None,
    flag_regex: Optional[str] = None,
    flag_hash: Optional[str] = None,
    attack_info: Optional[str] = None,
) -> CheckerTaskMessage:
    if unique_variant_index is None:
        unique_variant_index = variant_id

    prefix = "havoc"
    if method in ("putflag", "getflag"):
        prefix = "flag"
    elif method in ("putnoise", "getnoise"):
        prefix = "noise"
    elif method == "exploit":
        prefix = "exploit"
    task_chain_id = (
        f"{CHAIN_ID_PREFIX}_{prefix}_s0_r{round_id}_t0_i{unique_variant_index}"
    )

    return CheckerTaskMessage(
        task_id=round_id,
        method=CheckerMethod(method),
        address=service_address,
        team_id=0,
        team_name="teamname",
        current_round_id=round_id,
        related_round_id=round_id,
        flag=flag,
        variant_id=variant_id,
        timeout=REQUEST_TIMEOUT * 1000,
        round_length=60000,
        task_chain_id=task_chain_id,
        flag_regex=flag_regex,
        flag_hash=flag_hash,
        attack_info=attack_info,
    )


def _jsonify_request_message(request_message: CheckerTaskMessage):
    return jsons.dumps(
        request_message,
        use_enum_name=False,
        key_transformer=jsons.KEY_TRANSFORMER_CAMELCASE,
        strict=True,
    )


def _test_putflag(
    flag,
    round_id,
    flag_id,
    service_address,
    checker_url,
    unique_variant_index=None,
    expected_result=CheckerTaskResult.OK,
) -> Optional[str]:
    if unique_variant_index is None:
        unique_variant_index = flag_id
    request_message = _create_request_message(
        "putflag",
        round_id,
        flag_id,
        service_address,
        flag,
        unique_variant_index=unique_variant_index,
    )
    msg = _jsonify_request_message(request_message)
    r = requests.post(
        f"{checker_url}",
        data=msg,
        headers={"content-type": "application/json"},
        timeout=REQUEST_TIMEOUT,
    )
    result_message: CheckerResultMessage = jsons.loads(
        r.content, CheckerResultMessage, key_transformer=jsons.KEY_TRANSFORMER_SNAKECASE
    )
    assert (
        CheckerTaskResult(result_message.result) == expected_result
    ), f"\nMessage: {result_message.message}\n"
    return result_message.attack_info


def _test_getflag(
    flag,
    round_id,
    flag_id,
    service_address,
    checker_url,
    unique_variant_index=None,
    expected_result=CheckerTaskResult.OK,
):
    if unique_variant_index is None:
        unique_variant_index = flag_id
    request_message = _create_request_message(
        "getflag",
        round_id,
        flag_id,
        service_address,
        flag,
        unique_variant_index=unique_variant_index,
    )
    msg = _jsonify_request_message(request_message)
    r = requests.post(
        f"{checker_url}",
        data=msg,
        headers={"content-type": "application/json"},
        timeout=REQUEST_TIMEOUT,
    )
    assert r.status_code == 200
    result_message: CheckerResultMessage = jsons.loads(
        r.content, CheckerResultMessage, key_transformer=jsons.KEY_TRANSFORMER_SNAKECASE
    )
    assert (
        CheckerTaskResult(result_message.result) == expected_result
    ), f"\nMessage: {result_message.message}\n"


def _test_putnoise(
    round_id,
    noise_id,
    service_address,
    checker_url,
    unique_variant_index=None,
    expected_result=CheckerTaskResult.OK,
):
    if unique_variant_index is None:
        unique_variant_index = noise_id
    request_message = _create_request_message(
        "putnoise",
        round_id,
        noise_id,
        service_address,
        unique_variant_index=unique_variant_index,
    )
    msg = _jsonify_request_message(request_message)
    r = requests.post(
        f"{checker_url}",
        data=msg,
        headers={"content-type": "application/json"},
        timeout=REQUEST_TIMEOUT,
    )
    assert r.status_code == 200
    result_message: CheckerResultMessage = jsons.loads(
        r.content, CheckerResultMessage, key_transformer=jsons.KEY_TRANSFORMER_SNAKECASE
    )
    assert (
        CheckerTaskResult(result_message.result) == expected_result
    ), f"\nMessage: {result_message.message}\n"


def _test_getnoise(
    round_id,
    noise_id,
    service_address,
    checker_url,
    unique_variant_index=None,
    expected_result=CheckerTaskResult.OK,
):
    if unique_variant_index is None:
        unique_variant_index = noise_id
    request_message = _create_request_message(
        "getnoise",
        round_id,
        noise_id,
        service_address,
        unique_variant_index=unique_variant_index,
    )
    msg = _jsonify_request_message(request_message)
    r = requests.post(
        f"{checker_url}",
        data=msg,
        headers={"content-type": "application/json"},
        timeout=REQUEST_TIMEOUT,
    )
    assert r.status_code == 200
    result_message: CheckerResultMessage = jsons.loads(
        r.content, CheckerResultMessage, key_transformer=jsons.KEY_TRANSFORMER_SNAKECASE
    )
    assert (
        CheckerTaskResult(result_message.result) == expected_result
    ), f"\nMessage: {result_message.message}\n"


def _test_havoc(
    round_id,
    havoc_id,
    service_address,
    checker_url,
    unique_variant_index=None,
    expected_result=CheckerTaskResult.OK,
):
    if unique_variant_index is None:
        unique_variant_index = havoc_id
    request_message = _create_request_message(
        "havoc",
        round_id,
        havoc_id,
        service_address,
        unique_variant_index=unique_variant_index,
    )
    msg = _jsonify_request_message(request_message)
    r = requests.post(
        f"{checker_url}",
        data=msg,
        headers={"content-type": "application/json"},
        timeout=REQUEST_TIMEOUT,
    )
    assert r.status_code == 200
    result_message: CheckerResultMessage = jsons.loads(
        r.content, CheckerResultMessage, key_transformer=jsons.KEY_TRANSFORMER_SNAKECASE
    )
    assert (
        CheckerTaskResult(result_message.result) == expected_result
    ), f"\nMessage: {result_message.message}\n"


def _test_exploit(
    flag_regex,
    flag_hash,
    attack_info,
    round_id,
    exploit_id,
    service_address,
    checker_url,
    unique_variant_index=None,
    expected_result=CheckerTaskResult.OK,
) -> Optional[str]:
    if unique_variant_index is None:
        unique_variant_index = exploit_id
    request_message = _create_request_message(
        "exploit",
        round_id,
        exploit_id,
        service_address,
        unique_variant_index=unique_variant_index,
        flag_regex=flag_regex,
        flag_hash=flag_hash,
        attack_info=attack_info,
    )
    msg = _jsonify_request_message(request_message)
    r = requests.post(
        f"{checker_url}",
        data=msg,
        headers={"content-type": "application/json"},
        timeout=REQUEST_TIMEOUT,
    )
    assert r.status_code == 200
    result_message: CheckerResultMessage = jsons.loads(
        r.content, CheckerResultMessage, key_transformer=jsons.KEY_TRANSFORMER_SNAKECASE
    )
    assert (
        CheckerTaskResult(result_message.result) == expected_result
    ), f"\nMessage: {result_message.message}\n"
    return result_message.flag


import argparse
import logging
import os
import sys

import jsons
import pytest
import requests
from enochecker_core import CheckerInfoMessage
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


def run_tests(host, port, service_address, test_methods):
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


def main():
    parser = argparse.ArgumentParser(
        prog="enochecker_test",
        description="Utility for testing checkers that implement the enochecker API",
    )
    parser.add_argument(
        "-a",
        "--checker-address",
        help="The address on which the checker is listening (defaults to the ENOCHECKER_TEST_CHECKER_ADDRESS environment variable)",
        default=os.environ.get("ENOCHECKER_TEST_CHECKER_ADDRESS"),
    )
    parser.add_argument(
        "-p",
        "--checker-port",
        help="The port on which the checker is listening (defaults to ENOCHECKER_TEST_CHECKER_PORT environment variable)",
        choices=range(1, 65536),
        metavar="{1..65535}",
        type=int,
        default=os.environ.get("ENOCHECKER_TEST_CHECKER_PORT"),
    )
    parser.add_argument(
        "-A",
        "--service-address",
        help="The address on which the service is listening (defaults to ENOCHECKER_TEST_SERVICE_ADDRESS environment variable)",
        default=os.environ.get("ENOCHECKER_TEST_SERVICE_ADDRESS"),
    )
    parser.add_argument(
        "testcase",
        help="Specify the tests that should be run in the syntax expected by pytest, e.g. test_getflag. If no test is specified, all tests will be run.",
        nargs="*",
    )

    args = parser.parse_args()

    if not args.checker_address:
        parser.print_usage()
        raise Exception(
            "Missing enochecker address, please set the ENOCHECKER_TEST_CHECKER_ADDRESS environment variable"
        )
    if not args.checker_port:
        parser.print_usage()
        raise Exception(
            "Missing enochecker port, please set the ENOCHECKER_TEST_CHECKER_PORT environment variable"
        )
    if not args.service_address:
        parser.print_usage()
        raise Exception(
            "Missing service address, please set the ENOCHECKER_TEST_SERVICE_ADDRESS environment variable"
        )

    logging.basicConfig(level=logging.INFO)
    run_tests(
        args.checker_address, args.checker_port, args.service_address, args.testcase
    )
