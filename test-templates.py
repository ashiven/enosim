import asyncio
import json

from enosimulator.setup import SetupHelper
from enosimulator.setup.types import Config, Secrets


def _parse_json(path):
    with open(path, "r") as json_file:
        content = json_file.read()
        return json.loads(content)


config = _parse_json("./config/examples/hetzner.config.json")
secrets = _parse_json("C:/Users/janni/secrets.json")


sh = SetupHelper(Config.from_(config), Secrets.from_(secrets))
asyncio.run(sh.convert_templates())
