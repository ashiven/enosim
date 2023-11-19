import os
from typing import List

import aiofiles


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
