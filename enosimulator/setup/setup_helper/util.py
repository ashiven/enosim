import os

import aiofiles

from ..types import Config, Experience, Team

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


#### Exports ####


class TeamGenerator:
    def __init__(self, config):
        self.config: Config = config
        if self.config.settings.simulation_type == "stress-test":
            self.team_distribution = {Experience.HAXXOR: self.config.settings.teams}

        else:
            NOOB_PERCENTAGE = (0.2, Experience.NOOB)
            BEGINNER_PERCENTAGE = (0.2, Experience.BEGINNER)
            INTERMEDIATE_PERCENTAGE = (0.3, Experience.INTERMEDIATE)
            ADVANCED_PERCENTAGE = (0.2, Experience.ADVANCED)
            PRO_PERCENTAGE = (0.1, Experience.PRO)
            self.team_distribution = {
                e: int(p * self.config.settings.teams)
                for p, e in [
                    NOOB_PERCENTAGE,
                    BEGINNER_PERCENTAGE,
                    INTERMEDIATE_PERCENTAGE,
                    ADVANCED_PERCENTAGE,
                    PRO_PERCENTAGE,
                ]
            }
            while sum(self.team_distribution.values()) < self.config.settings.teams:
                self.team_distribution[Experience.NOOB] += 1
            while sum(self.team_distribution.values()) > self.config.settings.teams:
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


async def copy_file(src, dst):
    if os.path.exists(src):
        async with aiofiles.open(src, "rb") as src_file:
            async with aiofiles.open(dst, "wb") as dst_file:
                content = await src_file.read()
                await dst_file.write(content)


async def replace_line(path, line_number, new_line):
    async with aiofiles.open(path, "rb+") as file:
        lines = await file.readlines()
        lines[line_number] = new_line.replace("\\", "/").encode("utf-8")
        await file.seek(0)
        await file.writelines(lines)
        await file.truncate()


async def insert_after(path, after, insert_lines):
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


async def append_lines(path, append_lines):
    async with aiofiles.open(path, "ab") as file:
        for line in append_lines:
            await file.write(line.encode("utf-8"))


async def delete_lines(path, delete_lines):
    new_lines = []
    async with aiofiles.open(path, "rb") as file:
        lines = await file.readlines()
        for index, line in enumerate(lines):
            if index not in delete_lines:
                new_lines.append(line)
    async with aiofiles.open(path, "wb") as file:
        await file.writelines(new_lines)


#### End Exports ####
