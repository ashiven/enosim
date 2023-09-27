import random
from time import sleep

from colorama import Fore
from orchestrator import Orchestrator

#### Helpers ####


def _random_test(team):
    probability = team["experience"].value
    return random.random() < probability


def _exploit_or_patch(team):
    random_variant = random.choice(["exploiting", "patched"])
    random_service = random.choice(list(team[random_variant]))
    random_flagstore = random.choice(list(team[random_variant][random_service]))

    return random_variant, random_service, random_flagstore


#### End Helpers ####


class Simulation:
    def __init__(self, setup):
        self.setup = setup
        self.orchestrator = Orchestrator(setup)
        self.orchestrator.update_teams()

    def run(self):
        # TODO:
        # - we have our simulation loop that generates a round_id for every minute of the simulation
        # - in every round we have to:
        #   - go through all teams:
        #       - for each team we perform the random test in accordance with their experience level
        #       - if the random test is successful, the team will start exploiting one random flagstore or patch one random flagstore
        #       - this just means that the boolean value for the flagstore in the exploiting or patched dict will be set to True
        #   - then we will tell the orchestrator to send out exploit requests to the teams exploit-checker towards all other teams that haven't patched the flagstore yet
        for round_id in range(self.setup.config["settings"]["duration-in-minutes"]):
            print(
                Fore.BLUE + f"\n==================ROUND {round_id}==================\n"
            )

            # step 1: go through all teams and perform the random test
            for team, settings in self.setup.teams.items():
                if _random_test(settings):
                    variant, service, flagstore = _exploit_or_patch(settings)
                    info_text = (
                        "started exploiting" if variant == "exploiting" else "patched"
                    )
                    print(
                        Fore.GREEN
                        + f"\n[+] Team {team} {info_text} {service}: {flagstore}\n"
                    )

            # step 2: go through all teams and exploit one random flagstore or patch one random flagstore

            # step 3: wait one minute for the next round to start
            sleep(1)


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
"""
