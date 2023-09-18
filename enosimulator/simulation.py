import secrets
from typing import Optional

import jsons
import requests
from enochecker_core import (
    CheckerInfoMessage,  # the response the checker sends when accessing the /service endpoint, containing info like the name of the service, flag variants etc.
)
from enochecker_core import (
    CheckerMethod,  # this is an Enum with the variants: PUTFLAG, GETFLAG, PUTNOISE, GETNOISE, HAVOC, EXPLOIT
)
from enochecker_core import (
    CheckerResultMessage,  # the response that the checker sends after receiving an instruction to execute putflag, getflag, exploit etc.
)
from enochecker_core import (
    CheckerTaskMessage,  # can be sent to a checker to instruct it to execute putflag, getflag, exploit etc.
)
from enochecker_core import (
    CheckerTaskResult,  # this is an Enum with the variants: OK, MUMBLE, OFFLINE, INTERNAL_ERROR
)

FLAG_REGEX_ASCII = r"ENO[A-Za-z0-9+\/=]{48}"
FLAG_REGEX_UTF8 = r"🥺[A-Za-z0-9+\/=]{48}🥺🥺"
REQUEST_TIMEOUT = 10
CHAIN_ID_PREFIX = secrets.token_hex(20)


# this method creates a CheckerTaskMessage to be sent to the checker to request execution of putflag, getflag etc.
def _create_request_message(
    method: str,  # which method (putflag, getflag, exploit etc.)
    round_id: int,  # which round we are currently in (this will become the unique ID for this task)
    variant_id: int,  # which of the exploits or putflags etc. to use (for example use exploit 1)
    service_address: str,  # this is the ip address of the service that the checker contacts
    flag: Optional[
        str
    ] = None,  # when we want the checker to execute putflag or getflag, we have to tell it the flag that should be put/get
    unique_variant_index: Optional[
        int
    ] = None,  # this is only relevant for the different ways that tests have been implemented for the same checker method
    flag_regex: Optional[
        str
    ] = None,  # a regular expression that the checker can use to find the given flag in a service response (we have to supply it according to the flags we give the checker)
    flag_hash: Optional[
        str
    ] = None,  # the hashed flag, not sure why we need this exactly
    attack_info: Optional[
        str
    ] = None,  # we can supply the attack info from putflag for some reason
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
    # this is a unique identifier that gets created to store related info in the checkers database (for example attack info after a putflag call)
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


# give me the number of exploits the service has defined and the address where the service is running
# also give me the hashed flag and a regular expression so i can find the flag in the service response and verify it is correct
# lastly, give me the attack info that you received depositing the flag
# and i will also need the address where the checker is running so i can send him the request
def every_exploit_once_per_minute(
    exploit_variants,
    service_address,
    flag_hash,
    flag_regex,
    attack_info,
    checker_address,
):
    # repeat for 8 hours
    for round_id in range(8 * 60):
        for variant_id in exploit_variants:
            # TODO: - gotta generate and put some flags before exploiting anything
            task_request = _create_request_message(
                method="exploit",
                round_id=round_id,
                variant_id=variant_id,
                service_address=service_address,
                flag_hash=flag_hash,
                flag_regex=flag_regex,
                attack_info=attack_info,
            )
            # gotta bring this into json format for the http request to the checker
            task_request = _jsonify_request_message(task_request)
            # now i'll send this request to the checker to instruct it to exploit the service
            response = requests.post(
                checker_address,
                data=task_request,
                headers={"Content-Type": "application/json"},
                timeout=REQUEST_TIMEOUT,
            )
            # extract the task result from the checker out of the http response
            task_result = jsons.loads(
                response.content,
                CheckerResultMessage,
                key_transformer=jsons.KEY_TRANSFORMER_SNAKECASE,
            )
            # something went wrong exploiting
            if CheckerTaskResult(task_result.result) is not CheckerTaskResult.OK:
                print(task_result.message)
            # thats the flag we got through the exploit
            print(task_result.flag)
