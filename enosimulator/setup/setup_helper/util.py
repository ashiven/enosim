import json
import os
from collections import Counter
from typing import Dict, List, Tuple

import aiofiles
from rich.console import Console


async def copy_file(src: str, dst: str) -> None:
    """Copy a file from src to dst."""

    if os.path.exists(src):
        async with aiofiles.open(src, "rb") as src_file:
            async with aiofiles.open(dst, "wb") as dst_file:
                content = await src_file.read()
                await dst_file.write(content)


async def replace_line(path: str, line_number: int, new_line: str) -> None:
    """Replace a line in a file with a new line."""

    async with aiofiles.open(path, "rb+") as file:
        lines = await file.readlines()
        lines[line_number] = new_line.replace("\\", "/").encode("utf-8")
        await file.seek(0)
        await file.writelines(lines)
        await file.truncate()


async def insert_after(path: str, after: str, insert_lines: List[str]) -> None:
    """Insert a list of lines after a specific line in a file."""

    new_lines = []
    async with aiofiles.open(path, "rb") as file:
        lines = await file.readlines()
        for line in lines:
            new_lines.append(line)
            if line.startswith(after.encode("utf-8")):
                for insert_line in insert_lines:
                    new_lines.append(insert_line.encode("utf-8"))
    async with aiofiles.open(path, "wb") as file:
        await file.writelines(new_lines)


async def append_lines(path: str, append_lines: List[str]) -> None:
    """Append a list of lines to a file."""

    async with aiofiles.open(path, "ab") as file:
        for line in append_lines:
            await file.write(line.encode("utf-8"))


async def delete_lines(path: str, delete_lines: List[int]) -> None:
    """Delete a list of line numbers from a file."""

    new_lines = []
    async with aiofiles.open(path, "rb") as file:
        lines = await file.readlines()
        for index, line in enumerate(lines):
            if index not in delete_lines:
                new_lines.append(line)
    async with aiofiles.open(path, "wb") as file:
        await file.writelines(new_lines)


def analyze_scoreboard_file(json_path: str) -> Dict[str, Tuple[float, float]]:
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
        return _analyze_scoreboard_file(json_path)

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


def _analyze_scoreboard_file(json_path: str) -> Dict[str, Tuple[float, float]]:
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
        """Calculate the exploit probability a team has for a specific service based on
        their score for that service.
        """

        max_percent = score / MAX_SCORE_PER_SERVICE
        first_success = TOTAL_ROUNDS - (TOTAL_ROUNDS * max_percent)
        exploit_probability = 1 / first_success
        return exploit_probability

    def exploit_probability(average_score):
        """
        Calculate the exploit probability a team has based on their average score.

        Firstly, a specific team from the scoreboard whose score is closest to the given
        average score is selected. Then, the exploit probability is calculated by
        deriving the exploit probability for each service and then summing them up.
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
