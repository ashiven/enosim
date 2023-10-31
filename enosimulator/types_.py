from dataclasses import dataclass
from enum import Enum
from typing import Dict, List

############## Enums ##############


class SetupVariant(Enum):
    AZURE = "azure"
    HETZNER = "hetzner"
    LOCAL = "local"

    @staticmethod
    def from_str(s):
        if s == "azure":
            return SetupVariant.AZURE
        elif s == "hetzner":
            return SetupVariant.HETZNER
        elif s == "local":
            return SetupVariant.LOCAL
        else:
            raise NotImplementedError


class Experience(Enum):
    """
    An enum representing the experience level of a team.

    The first value stands for the probability of the team exploiting / patching a vulnerability in any round.
    The second value stands for their prevalence in real ctf competitions.
    """

    NOOB = (0.015, 0.08)
    BEGINNER = (0.04, 0.54)
    INTERMEDIATE = (0.06, 0.29)
    ADVANCED = (0.09, 0.07)
    PRO = (0.12, 0.02)
    HAXXOR = (1, 1)

    __str__ = lambda self: self.name.lower().capitalize()

    @staticmethod
    def from_str(s):
        if s == "noob":
            return Experience.NOOB
        elif s == "beginner":
            return Experience.BEGINNER
        elif s == "intermediate":
            return Experience.INTERMEDIATE
        elif s == "advanced":
            return Experience.ADVANCED
        elif s == "pro":
            return Experience.PRO
        elif s == "haxxor":
            return Experience.HAXXOR
        else:
            raise NotImplementedError


############## Dataclasses ##############


@dataclass
class Team:
    id: int
    name: str
    team_subnet: str
    address: str
    experience: Experience
    exploiting: Dict
    patched: Dict
    points: float
    gain: float

    def to_json(self):
        new_dict = {
            "id": self.id,
            "name": self.name,
            "subnet": self.team_subnet,
            "address": self.address,
            "experience": str(self.experience),
            "exploiting": self.exploiting,
            "patched": self.patched,
            "points": self.points,
            "gain": self.gain,
        }
        return new_dict


@dataclass
class Service:
    id: int
    name: str
    flags_per_round_multiplier: int
    noises_per_round_multiplier: int
    havocs_per_round_multiplier: int
    weight_factor: int
    checkers: List[str]

    def to_json(self):
        new_dict = {
            "id": self.id,
            "name": self.name,
            "flagsPerRound": self.flags_per_round_multiplier,
            "noisesPerRound": self.noises_per_round_multiplier,
            "havocsPerRound": self.havocs_per_round_multiplier,
            "weightFactor": self.weight_factor,
            "github": f"https://github.com/enowars/{self.name}",
        }
        return new_dict

    @staticmethod
    def from_(dictionary):
        new_service = Service(
            id=dictionary["id"],
            name=dictionary["name"],
            flags_per_round_multiplier=dictionary["flagsPerRoundMultiplier"],
            noises_per_round_multiplier=dictionary["noisesPerRoundMultiplier"],
            havocs_per_round_multiplier=dictionary["havocsPerRoundMultiplier"],
            weight_factor=dictionary["weightFactor"],
            checkers=dictionary["checkers"],
        )
        return new_service


@dataclass
class IpAddresses:
    public_ip_addresses: Dict
    private_ip_addresses: Dict


@dataclass
class ConfigSetup:
    ssh_config_path: str
    location: str
    vm_sizes: Dict
    vm_image_references: Dict

    @staticmethod
    def from_(setup):
        if not type(setup["ssh-config-path"]) is str:
            raise ValueError("Invalid ssh config path in config file.")

        if setup["location"] not in ["azure", "hetzner", "local"]:
            raise ValueError("Invalid location in config file.")

        if not type(setup["vm-sizes"]) is dict:
            raise ValueError("Invalid vm sizes in config file.")

        if not type(setup["vm-image-references"]) is dict:
            raise ValueError("Invalid vm image references in config file.")

        new_setup = ConfigSetup(
            ssh_config_path=setup["ssh-config-path"],
            location=setup["location"],
            vm_sizes=setup["vm-sizes"],
            vm_image_references=setup["vm-image-references"],
        )
        return new_setup


@dataclass
class ConfigSettings:
    duration_in_minutes: int
    teams: int
    services: List[str]
    checker_ports: List[int]
    simulation_type: str

    @staticmethod
    def from_(settings):
        if settings["simulation-type"] not in [
            "stress-test",
            "basic-stress-test",
            "realistic",
        ]:
            raise ValueError("Invalid simulation type in config file.")

        if not type(settings["duration-in-minutes"]) is int:
            raise ValueError("Invalid duration in config file.")

        if (
            not type(settings["teams"]) is int
            or settings["teams"] < 1
            or settings["teams"] > 100
        ):
            raise ValueError("Invalid teams in config file.")

        if not type(settings["services"]) is list:
            raise ValueError("Invalid services in config file.")

        if not type(settings["checker-ports"]) is list:
            raise ValueError("Invalid checker ports in config file.")

        new_settings = ConfigSettings(
            duration_in_minutes=settings["duration-in-minutes"],
            teams=settings["teams"],
            services=settings["services"],
            checker_ports=settings["checker-ports"],
            simulation_type=settings["simulation-type"],
        )
        return new_settings


@dataclass
class ConfigCtfJson:
    title: str
    flag_validity_in_rounds: int
    checked_rounds_per_round: int
    round_length_in_seconds: int

    @staticmethod
    def from_(ctf_json):
        if not type(ctf_json["title"]) is str:
            raise ValueError("Invalid title in config file.")

        if not type(ctf_json["flag-validity-in-rounds"]) is int:
            raise ValueError("Invalid flag validity in rounds in config file.")

        if not type(ctf_json["checked-rounds-per-round"]) is int:
            raise ValueError("Invalid checked rounds per round in config file.")

        if not type(ctf_json["round-length-in-seconds"]) is int:
            raise ValueError("Invalid round length in seconds in config file.")

        new_ctf_json = ConfigCtfJson(
            title=ctf_json["title"],
            flag_validity_in_rounds=ctf_json["flag-validity-in-rounds"],
            checked_rounds_per_round=ctf_json["checked-rounds-per-round"],
            round_length_in_seconds=ctf_json["round-length-in-seconds"],
        )
        return new_ctf_json


@dataclass
class Config:
    setup: ConfigSetup
    settings: ConfigSettings
    ctf_json: ConfigCtfJson

    @staticmethod
    def from_(config):
        try:
            new_config = Config(
                setup=ConfigSetup.from_(config["setup"]),
                settings=ConfigSettings.from_(config["settings"]),
                ctf_json=ConfigCtfJson.from_(config["ctf-json"]),
            )
            return new_config
        except Exception as e:
            print(e)
            raise ValueError("Invalid config file.")


@dataclass
class VmSecrets:
    github_personal_access_token: str
    ssh_public_key_path: str
    ssh_private_key_path: str

    @staticmethod
    def from_(vm_secrets):
        if not type(vm_secrets["github-personal-access-token"]) is str:
            raise ValueError("Invalid github personal access token in secrets file.")

        if not type(vm_secrets["ssh-public-key-path"]) is str:
            raise ValueError("Invalid ssh public key path in secrets file.")

        if not type(vm_secrets["ssh-private-key-path"]) is str:
            raise ValueError("Invalid ssh private key path in secrets file.")

        new_vm_secrets = VmSecrets(
            github_personal_access_token=vm_secrets["github-personal-access-token"],
            ssh_public_key_path=vm_secrets["ssh-public-key-path"],
            ssh_private_key_path=vm_secrets["ssh-private-key-path"],
        )
        return new_vm_secrets


@dataclass
class CloudSecrets:
    azure_service_principal: dict
    hetzner_api_token: str

    @staticmethod
    def from_(cloud_secrets):
        if not type(cloud_secrets["azure-service-principal"]) is dict:
            raise ValueError("Invalid azure service principal in secrets file.")

        if not type(cloud_secrets["hetzner-api-token"]) is str:
            raise ValueError("Invalid hetzner api token in secrets file.")

        new_cloud_secrets = CloudSecrets(
            azure_service_principal=cloud_secrets["azure-service-principal"],
            hetzner_api_token=cloud_secrets["hetzner-api-token"],
        )
        return new_cloud_secrets


@dataclass
class Secrets:
    vm_secrets: VmSecrets
    cloud_secrets: CloudSecrets

    @staticmethod
    def from_(secrets):
        try:
            new_secrets = Secrets(
                vm_secrets=VmSecrets.from_(secrets["vm-secrets"]),
                cloud_secrets=CloudSecrets.from_(secrets["cloud-secrets"]),
            )
            return new_secrets
        except Exception as e:
            print(e)
            raise ValueError("Invalid secrets file.")
