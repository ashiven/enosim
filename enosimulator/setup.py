import json
import subprocess
import sys


####  Helpers ####
def _parse_json(path):
    with open(path, "r") as json_file:
        return json.load(json_file)


def _run_bash_script(script_path, args):
    try:
        p_args = ["bash", script_path] + args

        p = subprocess.Popen(
            p_args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        for line in p.stdout:
            print(line)
            sys.stdout.flush()

        p.wait()
        if p.returncode != 0:
            print(f"process exited with return code: {p.returncode}")

    except subprocess.CalledProcessError as e:
        print(e)


def _generate_team(id):
    team_names = ["Kleinmanzama", "Grossmanzama"]
    new_team = {
        "id": id,
        "name": team_names[id],
        "teamSubnet": "::ffff:10.0.2.0",
        "address": f"10.0.2.{id}",
    }
    return new_team


#### End Helpers ####


class Setup:
    def __init__(self, verbose=False):
        self.ips = dict()
        self.teams = dict()
        self.services = dict()
        self.setup_path = ""
        self.verbose = verbose

    def configure(self, config_path):
        config = _parse_json(config_path)
        self.setup_path = f"../test-setup/{config['settings']['location']}"

        with open(f"{self.setup_path}/config/services.txt", "r+") as service_file:
            for service in config["settings"]["services"]:
                service_file.write(f"{service}\n")
            if self.verbose:
                print("[+] Created services.txt")
                service_file.seek(0)
                print(service_file.read())

        ctf_json = _parse_json(f"{self.setup_path}/config/ctf.json")
        for setting, value in config["ctf-json"].items():
            ctf_json[setting] = value

        with open(f"{self.setup_path}/config/ctf.json", "r+") as ctf_file:
            json.dump(ctf_json, ctf_file, indent=4)
            if self.verbose:
                print("[+] Created ctf.json")
                ctf_file.seek(0)
                print(ctf_file.read())

        ## TODO:
        # - Problem: we can't really know the addresses of the services and checkers
        #            before we have built the infrastructure
        # - add config["settings"]["teams"] generated teams to the ctf.json
        # - each service in config["settings"]["services"] needs to be added to the ctf.json

    def build(self):
        _run_bash_script(f"{self.setup_path}/deploy.sh", [])

    def destroy(self):
        _run_bash_script(f"{self.setup_path}/deploy.sh", ["-d"])
