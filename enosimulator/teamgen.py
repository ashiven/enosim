from enum import Enum

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


class Experience(Enum):
    """An enum representing the experience level of a team. The value stands for the probability of the team exploiting / patching a vulnerability."""

    NOOB = 0.01
    BEGINNER = 0.05
    INTERMEDIATE = 0.1
    ADVANCED = 0.2
    PRO = 0.3
    HAXXOR = 1

    @staticmethod
    def from_str(s):
        if s == "noob":
            return Experience.NOOB
        elif s == "beginner":
            return Experience.BEGINNER
        elif s == "intermediate":
            return Experience.INTERMEDIATE
        elif s == "advanced":
            return Experience.ADVANCED
        elif s == "pro":
            return Experience.PRO
        elif s == "haxxor":
            return Experience.HAXXOR
        else:
            raise NotImplementedError


#### Helpers ####


def _generate_ctf_team(id):
    new_team = {
        "id": id,
        "name": TEAM_NAMES[id - 1],
        "teamSubnet": "::ffff:<placeholder>",
        "address": "<placeholder>",
    }
    return new_team


def _generate_setup_team(id, experience):
    new_team = {
        TEAM_NAMES[id - 1]: {
            "id": id,
            "name": TEAM_NAMES[id - 1],
            "teamSubnet": "::ffff:<placeholder>",
            "address": "<placeholder>",
            "experience": experience,
            "exploiting": dict(),
            "patched": dict(),
        }
    }
    return new_team


#### End Helpers ####


class TeamGenerator:
    def __init__(self, config):
        self.config = config
        if self.config["settings"]["simulation-type"] == "stress-test":
            self.team_distribution = {
                Experience.HAXXOR: self.config["settings"]["teams"]
            }

        else:
            NOOB_PERCENTAGE = (0.2, Experience.NOOB)
            BEGINNER_PERCENTAGE = (0.2, Experience.BEGINNER)
            INTERMEDIATE_PERCENTAGE = (0.3, Experience.INTERMEDIATE)
            ADVANCED_PERCENTAGE = (0.2, Experience.ADVANCED)
            PRO_PERCENTAGE = (0.1, Experience.PRO)
            self.team_distribution = {
                e: int(p * self.config["settings"]["teams"])
                for p, e in [
                    NOOB_PERCENTAGE,
                    BEGINNER_PERCENTAGE,
                    INTERMEDIATE_PERCENTAGE,
                    ADVANCED_PERCENTAGE,
                    PRO_PERCENTAGE,
                ]
            }
            while (
                sum(self.team_distribution.values()) < self.config["settings"]["teams"]
            ):
                self.team_distribution[Experience.NOOB] += 1
            while (
                sum(self.team_distribution.values()) > self.config["settings"]["teams"]
            ):
                self.team_distribution[Experience.NOOB] -= 1

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
