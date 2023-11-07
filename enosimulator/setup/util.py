import json
import os
from subprocess import PIPE, STDOUT, CalledProcessError, Popen
from typing import Dict

import aiofiles
from rich.console import Console


def kebab_to_camel(s: str) -> str:
    """Convert an identifier in kebab-case to camelCase."""

    words = s.split("-")
    return words[0] + "".join(w.title() for w in words[1:])


async def parse_json(path: str) -> Dict:
    """Parse a JSON file."""

    async with aiofiles.open(path, "r") as json_file:
        content = await json_file.read()
        return json.loads(content)


async def create_file(path: str) -> None:
    """
    Create a file at the specified path.

    If the file already exists, it will be overwritten.
    """

    if os.path.exists(path):
        os.remove(path)
    async with aiofiles.open(path, "w") as file:
        await file.write("")


def delete_files(path: str) -> None:
    """Delete all files in a directory that are not .gitkeep."""

    for file in os.listdir(path):
        if file == ".gitkeep":
            continue
        file_path = os.path.join(path, file)
        if os.path.isfile(file_path):
            os.remove(file_path)


def execute_command(cmd: str) -> None:
    """Execute a shell command and print the output to the console in real time."""

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
