import asyncio
import json

from .enosimulator.setup import SetupHelper


def _parse_json(path):
    with open(path, "r") as json_file:
        content = json_file.read()
        return json.loads(content)


config = _parse_json("./config/examples/config.json")
secrets = _parse_json("C:/Users/janni/secrets.json")


sh = SetupHelper(config, secrets)
asyncio.run(sh.convert_templates())
