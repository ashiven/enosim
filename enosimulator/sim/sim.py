import asyncio
import random

from colorama import Fore
from sim.orchestrator import Orchestrator

#### Helpers ####


def _random_test(team):
    probability = team.experience.value
    random_value = random.random()
    return random_value < probability


def _exploit_or_patch(team):
    random_variant = random.choice(["exploiting", "patched"])
    if random_variant == "exploiting":
        random_service = random.choice(list(team.exploiting))
        random_flagstore = random.choice(list(team.exploiting[random_service]))
    else:
        random_service = random.choice(list(team.patched))
        random_flagstore = random.choice(list(team.patched[random_service]))

    return random_variant, random_service, random_flagstore


def _update_team(setup, team_name, variant, service, flagstore):
    if variant == "exploiting":
        setup.teams[team_name].exploiting[service][flagstore] = True
        info_text = "started exploiting"
    elif variant == "patched":
        setup.teams[team_name].patched[service][flagstore] = True
        info_text = "patched"
    print(Fore.GREEN + f"\n[+] Team {team_name} {info_text} {service}: {flagstore}\n")


#### End Helpers ####


class Simulation:
    def __init__(self, setup, orchestrator):
        self.setup = setup
        self.orchestrator = orchestrator
        self.round_id = 0

    @classmethod
    async def new(cls, setup):
        orchestrator = Orchestrator(setup)
        await orchestrator.update_teams()
        return cls(setup, orchestrator)

    def info(self):
        print(
            Fore.BLUE + f"\n==================ROUND {self.round_id}==================\n"
        )
        for team in self.setup.teams.values():
            print(f"{team.name}:\n    Exploiting: \n    Patched: \n")

    async def run(self):
        for round_id in range(self.setup.config["settings"]["duration-in-minutes"]):
            self.info()

            # Go through all teams and perform the random test
            for team_name, team in self.setup.teams.items():
                if _random_test(team):
                    variant, service, flagstore = _exploit_or_patch(team)
                    _update_team(self.setup, team_name, variant, service, flagstore)

            # Instruct orchestrator to send out exploit requests
            async with asyncio.TaskGroup() as task_group:
                for team in self.setup.teams.values():
                    task_group.create_task(
                        self.orchestrator.send_exploits(
                            round_id, team, self.setup.teams.values()
                        )
                    )

            self.round_id += 1
            await asyncio.sleep(2)
