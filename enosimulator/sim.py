from orchestrator import Orchestrator


class Simulation:
    def __init__(self, setup):
        self.setup = setup
        self.orchestrator = Orchestrator(setup)

    def run(self):
        self.orchestrator.update_teams()
        self.setup.info()


"""
def _exploit(
    round_id,
    variant_id,
    service_address,
    flag_hash,
    flag_regex,
    attack_info,
    checker_address,
):
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
            # TODO:
            # - generate and put flag before exploiting

            # _generate_flag()
            # _putflag()
            _exploit(
                round_id,
                variant_id,
                service_address,
                flag_hash,
                flag_regex,
                attack_info,
                checker_address,
            )


def exploit_services_in_threads():
    pass
    # TODO:
    # - generate one thread per service and run every_exploit_once_per_minute() on every thread
"""
