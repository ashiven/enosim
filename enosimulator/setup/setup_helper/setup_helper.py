from typing import Dict, List, Tuple

from types_ import Config, Experience, Secrets, SetupVariant, Team

from .azure import AzureSetupHelper
from .hetzner import HetznerSetupHelper
from .local import LocalSetupHelper

TEAM_NAMES = [
    "Edible Frog",
    "Jonah Crab",
    "English Cream Golden Retriever",
    "Vampire Squid",
    "Bolognese Dog",
    "Abyssinian Guinea Pig",
    "Eastern Racer",
    "Keta Salmon",
    "Korean Jindo",
    "Baiji",
    "Common Spotted Cuscus",
    "Indian python",
    "Kooikerhondje",
    "Gopher Tortoise",
    "Kamehameha Butterfly",
    "X-Ray Tetra",
    "Dodo",
    "Rainbow Shark",
    "Chihuahua Mix",
    "Flounder Fish",
    "Hooded Oriole",
    "Bed Bug",
    "Pacific Spaghetti Eel",
    "Yak",
    "Madagascar Hissing Cockroach",
    "Petite Goldendoodle",
    "Teacup Miniature Horse",
    "Arizona Blonde Tarantula",
    "Aye-Aye",
    "Dorking Chicken",
    "Elk",
    "Xenoposeidon",
    "Urutu Snake",
    "Hamburg Chicken",
    "Thorny Devil",
    "Venus Flytrap",
    "Fancy Mouse",
    "Lawnmower Blenny",
    "NebelungOrb Weaver",
    "Quagga",
    "Woolly Rhinoceros",
    "Radiated Tortoise",
    "De Kay's Brown Snake",
    "Red-Tailed Cuckoo Bumble Bee",
    "Japanese Bantam Chicken",
    "Irukandji Jellyfish",
    "Dogue De Bordeaux",
    "Bamboo Shark",
    "Peppered Moth",
    "German Cockroach",
    "Vestal Cuckoo Bumble Bee",
    "Ovenbird",
    "Irish Elk",
    "Southeastern Blueberry Bee",
    "Modern Game Chicken",
    "Onagadori Chicken",
    "LaMancha Goat",
    "Dik-Dik",
    "Quahog Clam",
    "Jack Russells",
    "Assassin Bug",
    "Upland Sandpiper",
    "Nurse Shark",
    "San Francisco Garter Snake",
    "Zebu",
    "New Hampshire Red Chicken",
    "False Water Cobra",
    "Earless Monitor Lizard",
    "Chicken Snake",
    "Walking Catfish",
    "Gypsy Cuckoo Bumble Bee",
    "Immortal Jellyfish",
    "Zorse",
    "Xerus",
    "Macaroni Penguin",
    "Taco Terrier",
    "Lone Star Tick",
    "Crappie Fish",
    "Yorkiepoo",
    "Lemon Cuckoo Bumble Bee",
    "Amano Shrimp",
    "German Wirehaired Pointer",
    "Cabbage Moth",
    "Huskydoodle",
    "Forest Cuckoo Bumble Bee",
    "Old House Borer",
    "Hammerhead Worm",
    "Striped Rocket Frog",
    "Zonkey",
    "Fainting Goat",
    "White Crappie",
    "Quokka",
    "Banana Eel",
    "Goblin Shark",
    "Umbrellabird",
    "Norwegian Elkhound",
    "Yabby",
    "Midget Faded Rattlesnake",
    "Pomchi",
    "Jack-Chi",
    "Herring",
]


#### Helpers ####


def _generate_ctf_team(id: int) -> Dict:
    name = TEAM_NAMES[id - 1] if id <= len(TEAM_NAMES) else f"Team {id}"
    new_team = {
        "id": id,
        "name": name,
        "teamSubnet": "::ffff:<placeholder>",
        "address": "<placeholder>",
    }
    return new_team


def _generate_setup_team(id: int, experience: Experience) -> Dict[str, Team]:
    name = TEAM_NAMES[id - 1] if id <= len(TEAM_NAMES) else f"Team {id}"
    new_team = {
        TEAM_NAMES[id - 1]: Team(
            id=id,
            name=name,
            team_subnet="::ffff:<placeholder>",
            address="<placeholder>",
            experience=experience,
            exploiting=dict(),
            patched=dict(),
            points=0.0,
            gain=0.0,
        )
    }
    return new_team


#### End Helpers ####


class TeamGenerator:
    def __init__(self, config: Config):
        self.config = config
        if self.config.settings.simulation_type == "stress-test":
            self.team_distribution = {Experience.HAXXOR: self.config.settings.teams}

        else:
            self.team_distribution = {
                experience: int(experience.value[1] * self.config.settings.teams)
                for experience in [
                    Experience.NOOB,
                    Experience.BEGINNER,
                    Experience.INTERMEDIATE,
                    Experience.ADVANCED,
                    Experience.PRO,
                ]
            }
            while sum(self.team_distribution.values()) < self.config.settings.teams:
                self.team_distribution[Experience.BEGINNER] += 1
            while sum(self.team_distribution.values()) > self.config.settings.teams:
                self.team_distribution[Experience.BEGINNER] -= 1

    def generate(self) -> Tuple[List, Dict]:
        ctf_json_teams = []
        setup_teams = dict()
        team_id_total = 0

        for experience, teams in self.team_distribution.items():
            for team_id in range(1, teams + 1):
                ctf_json_teams.append(_generate_ctf_team(team_id_total + team_id))
                setup_teams.update(
                    _generate_setup_team(team_id_total + team_id, experience)
                )
            team_id_total += teams

        return ctf_json_teams, setup_teams


class SetupHelper:
    def __init__(self, config: Config, secrets: Secrets, team_generator: TeamGenerator):
        self.config = config
        self.secrets = secrets
        self.team_generator = team_generator
        self.helpers = {
            SetupVariant.AZURE: AzureSetupHelper(self.config, self.secrets),
            SetupVariant.HETZNER: HetznerSetupHelper(self.config, self.secrets),
            SetupVariant.LOCAL: LocalSetupHelper(self.config, self.secrets),
        }

    def generate_teams(self) -> Tuple[List, Dict]:
        return self.team_generator.generate()

    async def convert_templates(self) -> None:
        helper = self.helpers[SetupVariant.from_str(self.config.setup.location)]
        await helper.convert_buildscript()
        await helper.convert_deploy_script()
        await helper.convert_tf_files()
        await helper.convert_vm_scripts()

    async def get_ip_addresses(self) -> Tuple[Dict, Dict]:
        helper = self.helpers[SetupVariant.from_str(self.config.setup.location)]
        return await helper.get_ip_addresses()
