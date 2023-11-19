import json
import os
from collections import Counter
from typing import Dict, List, Tuple

from aenum import extend_enum
from rich.console import Console
from types_ import Config, Experience, SimulationType, Team

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


class TeamGenerator:
    """
    Generates unique teams for the simulation.

    The distribution of experience levels differs depending on the simulation type.

    For basic-stress-test, there is only one team with the experience level HAXXOR.
    For stress-test and intensive-stress-test, there are as many teams with the experience level HAXXOR as there are teams in total.
    For all other simulation types, the distribution of experience levels is based on the number of teams and the experience distribution parameters derived from the analyze_scoreboard_file function.

    Attributes:
        config (Config): The configuration file provided by the user.
        team_distribution (Dict): A dictionary mapping experience levels to the number of teams with that experience level.
    """

    def __init__(self, config: Config):
        """
        Initialize the TeamGenerator class.

        If a scoreboard file is provided in the configuration, the team experience
        distribution will be derived from the scoreboard file. Otherwise, the team
        experience will be set according to default values returned by the
        analyze_scoreboard_file function.
        """

        experience_distribution = self.analyze_scoreboard_file(
            config.settings.scoreboard_file
        )
        try:
            for experience, distribution in experience_distribution.items():
                extend_enum(Experience, experience, distribution)
        except Exception:
            pass

        self.config = config
        if (
            self.config.settings.simulation_type
            == SimulationType.BASIC_STRESS_TEST.value
        ):
            self.team_distribution = {Experience.HAXXOR: 1}

        elif self.config.settings.simulation_type in (
            SimulationType.STRESS_TEST.value,
            SimulationType.INTENSIVE_STRESS_TEST.value,
        ):
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
                self.team_distribution[Experience.NOOB] += 1
            while sum(self.team_distribution.values()) > self.config.settings.teams:
                self.team_distribution[Experience.NOOB] -= 1

    def generate(self) -> Tuple[List, Dict]:
        """
        Generate teams for the simulation.

        Returns:
            A tuple containing:
                - A list of teams that will be used to generate a ctf.json file for the engine
                - A dictionary mapping team names to Team objects containing the team's information.
        """

        ctf_json_teams = []
        setup_teams = dict()
        team_id_total = 0

        for experience, teams in self.team_distribution.items():
            for team_id in range(1, teams + 1):
                ctf_json_teams.append(self._generate_ctf_team(team_id_total + team_id))
                setup_teams.update(
                    self._generate_setup_team(team_id_total + team_id, experience)
                )
            team_id_total += teams

        return ctf_json_teams, setup_teams

    def analyze_scoreboard_file(self, json_path: str) -> Dict[str, Tuple[float, float]]:
        """
        Analyze a scoreboard file and return a dictionary containing the experience
        distribution and exploit probabilities.

        This function tries to extract an experience distribution and exploit probabilities from a scoreboard file if it exists.
        Otherwise, it returns default values that were sourced from the enowars7 competition.

        Args:
            json_path (str): The path to the scoreboard file.

        Returns:
            A dictionary containing the experience distribution and exploit probabilities.
        """

        try:
            return self._analyze_scoreboard_file(json_path)

        except Exception:
            if json_path:
                Console().print(
                    "[bold red]\n[!] Scoreboard file not valid. Using default values.\n"
                )

            return {
                "NOOB": (0.003, 0.91),
                "BEGINNER": (0.011, 0.06),
                "INTERMEDIATE": (0.021, 0.01),
                "ADVANCED": (0.03, 0),
                "PRO": (0.058, 0.02),
            }

    def _generate_ctf_team(self, id: int) -> Dict:
        """
        Generate a team for the ctf.json file.

        Args:
            id (int): The id of the team.

        Returns:
            A dictionary containing the team's information.
        """

        name = TEAM_NAMES[id - 1] if id <= len(TEAM_NAMES) else f"Team {id}"
        new_team = {
            "id": id,
            "name": name,
            "teamSubnet": "::ffff:<placeholder>",
            "address": "<placeholder>",
        }
        return new_team

    def _generate_setup_team(self, id: int, experience: Experience) -> Dict[str, Team]:
        """
        Generate a team for the setup.

        Args:
            id (int): The id of the team.
            experience (Experience): The experience level of the team.

        Returns:
            A dictionary mapping the team's name to a Team object containing the team's information.
        """

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

    def _analyze_scoreboard_file(
        self, json_path: str
    ) -> Dict[str, Tuple[float, float]]:
        """The internal implementation of the analyze_scoreboard_file function."""

        if os.path.exists(json_path):
            with open(json_path, "r") as json_file:
                data = json.load(json_file)

        teams = data["teams"]
        attack_points = dict()
        for team in teams:
            team_name = team["teamName"]
            team_attack_points = team["attackScore"]
            attack_points[team_name] = team_attack_points

        scores = sorted([float(p) for p in list(attack_points.values())])

        PARTICIPATING_TEAMS = len(scores)
        # how many rounds on average are still included in a scoreboard.json after the game has already ended
        END_ROUNDS_OFFSET = 40
        TOTAL_ROUNDS = data["currentRound"] - END_ROUNDS_OFFSET
        POINTS_PER_ROUND_PER_FLAGSTORE = 50
        MAX_SCORE_PER_SERVICE = POINTS_PER_ROUND_PER_FLAGSTORE * TOTAL_ROUNDS
        HIGH_SCORE = scores[-1]

        NOOB_AVERAGE_POINTS = (0 * HIGH_SCORE + 0.2 * HIGH_SCORE) / 2
        BEGINNER_AVERAGE_POINTS = (0.2 * HIGH_SCORE + 0.4 * HIGH_SCORE) / 2
        INTERMEDIATE_AVERAGE_POINTS = (0.4 * HIGH_SCORE + 0.6 * HIGH_SCORE) / 2
        ADVANCED_AVERAGE_POINTS = (0.6 * HIGH_SCORE + 0.8 * HIGH_SCORE) / 2
        PROFESSIONAL_AVERAGE_POINTS = (0.8 * HIGH_SCORE + 1 * HIGH_SCORE) / 2

        def score_to_experience(score):
            """Convert a score to an experience level in the form of a string."""

            exp = "NOOB"
            if 0.2 * HIGH_SCORE < score <= 0.4 * HIGH_SCORE:
                exp = "BEGINNER"
            elif 0.4 * HIGH_SCORE < score <= 0.6 * HIGH_SCORE:
                exp = "INTERMEDIATE"
            elif 0.6 * HIGH_SCORE < score <= 0.8 * HIGH_SCORE:
                exp = "ADVANCED"
            elif 0.8 * HIGH_SCORE < score:
                exp = "PROFESSIONAL"
            return exp

        def exploit_probability_service(score):
            """Calculate the exploit probability a team has for a specific service based
            on their score for that service.
            """

            max_percent = score / MAX_SCORE_PER_SERVICE
            first_success = TOTAL_ROUNDS - (TOTAL_ROUNDS * max_percent)
            exploit_probability = 1 / first_success
            return exploit_probability

        def exploit_probability(average_score):
            """
            Calculate the exploit probability a team has based on their average score.

            Firstly, a specific team from the scoreboard whose score is closest to the
            given average score is selected. Then, the exploit probability is calculated
            by deriving the exploit probability for each service and then summing them
            up.
            """

            teams = data["teams"]
            closest_team = None
            closest_team_distance = float("inf")

            for team in teams:
                team_attack_points = team["attackScore"]
                if team_attack_points >= average_score:
                    team_distance = abs(team_attack_points - average_score)
                    if team_distance < closest_team_distance:
                        closest_team = team
                        closest_team_distance = team_distance

            exploit_probability = 0

            for service in closest_team["serviceDetails"]:
                service_score = service["attackScore"]
                service_exploit_probability = exploit_probability_service(service_score)
                exploit_probability += service_exploit_probability

            # double the exploit probability because we are also using it as the patch probability
            exploit_probability *= 2

            # scale exploit probability once more by experience level
            # (e.g. PROFESSIONAL teams are more likely to exploit a service than NOOB teams if they managed to find the vulnerability)
            exploit_probability *= average_score / HIGH_SCORE

            return exploit_probability

        team_distribution = Counter([score_to_experience(score) for score in scores])
        noob_teams = team_distribution["NOOB"]
        beginner_teams = team_distribution["BEGINNER"]
        intermediate_teams = team_distribution["INTERMEDIATE"]
        advanced_teams = team_distribution["ADVANCED"]
        professional_teams = team_distribution["PROFESSIONAL"]

        return {
            "NOOB": (
                round(exploit_probability(NOOB_AVERAGE_POINTS), 3),
                round(noob_teams / PARTICIPATING_TEAMS, 2),
            ),
            "BEGINNER": (
                round(exploit_probability(BEGINNER_AVERAGE_POINTS), 3),
                round(beginner_teams / PARTICIPATING_TEAMS, 2),
            ),
            "INTERMEDIATE": (
                round(exploit_probability(INTERMEDIATE_AVERAGE_POINTS), 3),
                round(intermediate_teams / PARTICIPATING_TEAMS, 2),
            ),
            "ADVANCED": (
                round(exploit_probability(ADVANCED_AVERAGE_POINTS), 3),
                round(advanced_teams / PARTICIPATING_TEAMS, 2),
            ),
            "PRO": (
                round(exploit_probability(PROFESSIONAL_AVERAGE_POINTS), 3),
                round(professional_teams / PARTICIPATING_TEAMS, 2),
            ),
        }
