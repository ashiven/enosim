import json
import os
from collections import Counter
from typing import Dict, List, Tuple

import aiofiles
from rich.console import Console


async def copy_file(src: str, dst: str) -> None:
    if os.path.exists(src):
        async with aiofiles.open(src, "rb") as src_file:
            async with aiofiles.open(dst, "wb") as dst_file:
                content = await src_file.read()
                await dst_file.write(content)


async def replace_line(path: str, line_number: int, new_line: str) -> None:
    async with aiofiles.open(path, "rb+") as file:
        lines = await file.readlines()
        lines[line_number] = new_line.replace("\\", "/").encode("utf-8")
        await file.seek(0)
        await file.writelines(lines)
        await file.truncate()


async def insert_after(path: str, after: str, insert_lines: List[str]) -> None:
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
    async with aiofiles.open(path, "ab") as file:
        for line in append_lines:
            await file.write(line.encode("utf-8"))


async def delete_lines(path: str, delete_lines: List[int]) -> None:
    new_lines = []
    async with aiofiles.open(path, "rb") as file:
        lines = await file.readlines()
        for index, line in enumerate(lines):
            if index not in delete_lines:
                new_lines.append(line)
    async with aiofiles.open(path, "wb") as file:
        await file.writelines(new_lines)


def analyze_scoreboard_file(json_path: str) -> Dict[str, Tuple[float, float]]:
    # try to extract distribution and probabilities from a scoreboard file if it exists
    # otherwise return default values that were sourced from the enowars7 scoreboard
    try:
        return _analyze_scoreboard_file(json_path)

    except:
        if json_path:
            Console().print(
                "[bold red]\n[!] Scoreboard file not valid. Using default values.\n"
            )

        return {
            "NOOB": (0.03, 0.91),
            "BEGINNER": (0.1, 0.06),
            "INTERMEDIATE": (0.17, 0.01),
            "ADVANCED": (0.23, 0),
            "PRO": (0.3, 0.02),
        }


def _analyze_scoreboard_file(json_path: str) -> Dict[str, Tuple[float, float]]:
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

    # TODO: - the points per flag value needs to be analyzed further
    POINTS_PER_FLAG = 20
    PARTICIPATING_TEAMS = len(scores)
    TOTAL_FLAGSTORES = sum([service["flagVariants"] for service in data["services"]])
    TOTAL_ROUNDS = data["currentRound"]
    POINTS_PER_ROUND_PER_FLAGSTORE = (PARTICIPATING_TEAMS - 1) * POINTS_PER_FLAG
    HIGH_SCORE = scores[-1]

    NOOB_AVERAGE_POINTS = (0 * HIGH_SCORE + 0.2 * HIGH_SCORE) / 2
    BEGINNER_AVERAGE_POINTS = (0.2 * HIGH_SCORE + 0.4 * HIGH_SCORE) / 2
    INTERMEDIATE_AVERAGE_POINTS = (0.4 * HIGH_SCORE + 0.6 * HIGH_SCORE) / 2
    ADVANCED_AVERAGE_POINTS = (0.6 * HIGH_SCORE + 0.8 * HIGH_SCORE) / 2
    PROFESSIONAL_AVERAGE_POINTS = (0.8 * HIGH_SCORE + 1 * HIGH_SCORE) / 2

    def score_to_experience(score):
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

    def exploit_probability(score):
        score_per_flagstore = score / TOTAL_FLAGSTORES
        rounds_needed = score_per_flagstore / POINTS_PER_ROUND_PER_FLAGSTORE
        exploit_probability = rounds_needed / TOTAL_ROUNDS
        return exploit_probability * 100

    team_distribution = Counter([score_to_experience(score) for score in scores])
    noob_teams = team_distribution["NOOB"]
    beginner_teams = team_distribution["BEGINNER"]
    intermediate_teams = team_distribution["INTERMEDIATE"]
    advanced_teams = team_distribution["ADVANCED"]
    professional_teams = team_distribution["PROFESSIONAL"]

    return {
        "NOOB": (
            round(exploit_probability(NOOB_AVERAGE_POINTS), 2),
            round(noob_teams / PARTICIPATING_TEAMS, 2),
        ),
        "BEGINNER": (
            round(exploit_probability(BEGINNER_AVERAGE_POINTS), 2),
            round(beginner_teams / PARTICIPATING_TEAMS, 2),
        ),
        "INTERMEDIATE": (
            round(exploit_probability(INTERMEDIATE_AVERAGE_POINTS), 2),
            round(intermediate_teams / PARTICIPATING_TEAMS, 2),
        ),
        "ADVANCED": (
            round(exploit_probability(ADVANCED_AVERAGE_POINTS), 2),
            round(advanced_teams / PARTICIPATING_TEAMS, 2),
        ),
        "PRO": (
            round(exploit_probability(PROFESSIONAL_AVERAGE_POINTS), 2),
            round(professional_teams / PARTICIPATING_TEAMS, 2),
        ),
    }
