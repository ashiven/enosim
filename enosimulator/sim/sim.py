import random
from time import sleep

from colorama import Fore
from orchestrator import Orchestrator

#### Helpers ####


def _random_test(team):
    probability = team["experience"].value
    random_value = random.random()
    return random_value < probability


def _exploit_or_patch(team):
    random_variant = random.choice(["exploiting", "patched"])
    random_service = random.choice(list(team[random_variant]))
    random_flagstore = random.choice(list(team[random_variant][random_service]))

    return random_variant, random_service, random_flagstore


#### End Helpers ####


class Simulation:
    async def __init__(self, setup):
        self.setup = setup
        self.orchestrator = Orchestrator(setup)
        await self.orchestrator.update_teams()

    def run(self):
        for round_id in range(self.setup.config["settings"]["duration-in-minutes"]):
            print(
                Fore.BLUE + f"\n==================ROUND {round_id}==================\n"
            )

            # Go through all teams and perform the random test
            for team, settings in self.setup.teams.items():
                if _random_test(settings):
                    variant, service, flagstore = _exploit_or_patch(settings)
                    if not self.setup.teams[team][variant][service][flagstore]:
                        self.setup.teams[team][variant][service][flagstore] = True
                        info_text = (
                            "started exploiting"
                            if variant == "exploiting"
                            else "patched"
                        )
                        print(
                            Fore.GREEN
                            + f"\n[+] Team {team} {info_text} {service}: {flagstore}\n"
                        )

            # TODO:
            # - it may be a good idea to do this concurrently for each team
            # - for this i could use the threading library and spawn a thread for each team
            # Instruct orchestrator to send out exploit requests

            sleep(60)
