from ..types import Config, Experience, Secrets, SetupVariant, Team
from .azure import AzureSetupHelper
from .hetzner import HetznerSetupHelper
from .local import LocalSetupHelper

TEAM_NAMES = [
    "Kleinmazama",
    "Wapiti",
    "Karibu",
    "Pudu",
    "Elch",
    "Wasserreh",
    "Leierhirsch",
    "Barasingha",
    "Northern Pudú",
    "Southern Pudú",
    "Gray Brocket",
    "White-Tailed Deer",
    "Chital",
    "Chinese Muntjac",
    "Pygmy brocket",
    "Water Deer",
    "Brazilian Brocket",
    "Tufted Deer",
    "Siberian roe deer",
    "Dwarf brocket",
    "Mule deer",
    "Fallow deer",
    "Javan rusa",
    "Sambar deer",
    "Reindeer",
    "Moose",
    "Sangai",
    "Indian hog deer",
]


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
