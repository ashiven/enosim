import asyncio
import secrets
import urllib
from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager
from typing import Dict

import jsons
from enochecker_core import CheckerMethod, CheckerTaskMessage
from types_ import IpAddresses

CHAIN_ID_PREFIX = secrets.token_hex(20)
REQUEST_TIMEOUT = 10
_pool = ThreadPoolExecutor()


@asynccontextmanager
async def async_lock(lock) -> None:
    """
    Lock context manager for async code.

    Source: https://stackoverflow.com/a/63425191
    """

    loop = asyncio.get_event_loop()
    await loop.run_in_executor(_pool, lock.acquire)
    try:
        yield
    finally:
        lock.release()


def checker_request(
    method: str,
    round_id: int,
    team_id: int,
    team_name: str,
    variant_id: int,
    service_address: str,
    flag: str,
    unique_variant_index: int,
    flag_regex: str,
    flag_hash: str,
    attack_info: str,
) -> CheckerTaskMessage:
    """
    Create a checker task request.

    Args:
        method: Checker method.
        round_id: Round ID.
        team_id: Team ID.
        team_name: Team name.
        variant_id: Variant ID.
        service_address: Service address.
        flag: Flag.
        unique_variant_index: Unique variant index.
        flag_regex: Flag regex.
        flag_hash: Flag hash.
        attack_info: Attack info.

    Returns:
        Checker task request.
    """

    if not unique_variant_index:
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
        team_id=team_id,
        team_name=team_name,
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


def req_to_json(request: CheckerTaskMessage) -> Dict:
    """
    Convert a checker task request to JSON.

    Args:
        request: Checker task request.

    Returns:
        Checker task request as JSON.
    """

    return jsons.dumps(
        request,
        use_enum_name=False,
        key_transformer=jsons.KEY_TRANSFORMER_CAMELCASE,
        strict=True,
    )


def port_from_address(address: str) -> str:
    """
    Extract the port number from an address.

    Args:
        address: Address.

    Returns:
        Port.
    """

    url = urllib.parse.urlparse(address)
    _, _, port = url.netloc.partition(":")
    return port


def private_to_public_ip(ip_addresses: IpAddresses) -> Dict[str, str]:
    """
    Convert private IP addresses to public IP addresses.

    Args:
        ip_addresses: IP addresses.

    Returns:
        A dictionary mapping private IP addresses to public IP addresses
    """

    return {
        ip_addresses.private_ip_addresses[team_name]: ip_addresses.public_ip_addresses[
            team_name
        ]
        for team_name in ip_addresses.private_ip_addresses
    }
