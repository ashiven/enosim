from random import shuffle

from ..types import Config, Experience, Secrets, SetupVariant, Team
from .azure import AzureSetupHelper
from .hetzner import HetznerSetupHelper
from .local import LocalSetupHelper

TEAM_NAMES = [
    "Abyssinian Guinea Pig",
    "Aye-Aye",
    "Amano Shrimp",
    "Assassin Bug",
    "Arizona Blonde Tarantula",
    "Bed Bug",
    "Banana Eel",
    "Bamboo Shark",
    "Baiji",
    "Bolognese Dog",
    "Cabbage Moth",
    "Chihuahua Mix",
    "Common Spotted Cuscus",
    "Chicken Snake",
    "Crappie Fish",
    "De Kay's Brown Snake",
    "Dik-Dik",
    "Dodo",
    "Dogue De Bordeaux",
    "Dorking Chicken",
    "Earless Monitor Lizard",
    "English Cream Golden Retriever",
    "Edible Frog",
    "Eastern Racer",
    "Elk",
    "Fainting Goat",
    "False Water Cobra",
    "Forest Cuckoo Bumble Bee",
    "Fancy Mouse",
    "Flounder Fish",
    "German Cockroach",
    "Gopher Tortoise",
    "German Wirehaired Pointer",
    "Gypsy Cuckoo Bumble Bee",
    "Goblin Shark",
    "Herring",
    "Hamburg Chicken",
    "Hammerhead Worm",
    "Huskydoodle",
    "Hooded Oriole",
    "Irukandji Jellyfish",
    "Irish Elk",
    "Immortal Jellyfish",
    "Indian python",
    "Jack Russells",
    "Jack-Chi",
    "Jonah Crab",
    "Japanese Bantam Chicken",
    "Korean Jindo",
    "Kooikerhondje",
    "Kamehameha Butterfly",
    "Keta Salmon",
    "Lemon Cuckoo Bumble Bee",
    "Lawnmower Blenny",
    "LaMancha Goat",
    "Lone Star Tick",
    "Madagascar Hissing Cockroach",
    "Macaroni Penguin",
    "Modern Game Chicken",
    "Midget Faded Rattlesnake",
    "Nurse Shark",
    "Norwegian Elkhound",
    "New Hampshire Red Chicken",
    "Nebelung" "Orb Weaver",
    "Old House Borer",
    "Ovenbird",
    "Onagadori Chicken",
    "Pacific Spaghetti Eel",
    "Petite Goldendoodle",
    "Peppered Moth",
    "Pomchi",
    "Quahog Clam",
    "Quagga",
    "Quokka",
    "Radiated Tortoise",
    "Rainbow Shark",
    "Red-Tailed Cuckoo Bumble Bee",
    "San Francisco Garter Snake",
    "Southeastern Blueberry Bee",
    "Striped Rocket Frog",
    "Taco Terrier",
    "Teacup Miniature Horse",
    "Thorny Devil",
    "Urutu Snake",
    "Umbrellabird",
    "Upland Sandpiper",
    "Vestal Cuckoo Bumble Bee",
    "Vampire Squid",
    "Venus Flytrap",
    "White Crappie",
    "Walking Catfish",
    "Woolly Rhinoceros",
    "Xerus",
    "X-Ray Tetra",
    "Xenoposeidon",
    "Yak",
    "Yabby",
    "Yorkiepoo",
    "Zebu",
    "Zorse",
    "Zonkey",
]

shuffle(TEAM_NAMES)


#### Helpers ####


def _generate_ctf_team(id: int):
    new_team = {
        "id": id,
        "name": TEAM_NAMES[id - 1],
        "teamSubnet": "::ffff:<placeholder>",
        "address": "<placeholder>",
    }
    return new_team


def _generate_setup_team(id: int, experience: Experience):
    new_team = {
        TEAM_NAMES[id - 1]: Team(
            id=id,
            name=TEAM_NAMES[id - 1],
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


class SetupHelper:
    def __init__(self, config: Config, secrets: Secrets):
        self.config = config
        self.secrets = secrets
        self.helpers = {
            SetupVariant.AZURE: AzureSetupHelper(config, secrets),
            SetupVariant.HETZNER: HetznerSetupHelper(config, secrets),
            SetupVariant.LOCAL: LocalSetupHelper(config, secrets),
        }
        self.team_gen = TeamGenerator(config)

    def generate_teams(self):
        return self.team_gen.generate()

    async def convert_templates(self):
        helper = self.helpers[SetupVariant.from_str(self.config.setup.location)]
        await helper.convert_buildscript()
        await helper.convert_deploy_script()
        await helper.convert_tf_files()
        await helper.convert_vm_scripts()

    async def get_ip_addresses(self):
        helper = self.helpers[SetupVariant.from_str(self.config.setup.location)]
        return await helper.get_ip_addresses()


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

    def generate(self):
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
