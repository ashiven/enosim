import json
import os
from subprocess import PIPE, STDOUT, CalledProcessError, Popen
from typing import Dict

import aiofiles
from rich.console import Console


def kebab_to_camel(s: str) -> str:
    words = s.split("-")
    return words[0] + "".join(w.title() for w in words[1:])


async def parse_json(path: str) -> Dict:
    async with aiofiles.open(path, "r") as json_file:
        content = await json_file.read()
        return json.loads(content)


async def create_file(path: str) -> None:
    if os.path.exists(path):
        os.remove(path)
    async with aiofiles.open(path, "w") as file:
        await file.write("")


def delete_files(path: str) -> None:
    for file in os.listdir(path):
        if file == ".gitkeep":
            continue
        file_path = os.path.join(path, file)
        if os.path.isfile(file_path):
            os.remove(file_path)


def execute_command(cmd: str) -> None:
    console = Console()
    try:
        p = Popen(
            cmd,
            stdout=PIPE,
            stderr=STDOUT,
            shell=True,
            encoding="utf-8",
            errors="replace",
        )

        while True:
            line = p.stdout.readline()
            if not line and p.poll() is not None:
                break
            if line:
                print(line.strip(), flush=True)

        p.wait()
        if p.returncode != 0:
            console.print(
                f"\n[bold red][!] Process exited with return code: {p.returncode}\n"
            )

    except CalledProcessError as e:
        console.print(e)
