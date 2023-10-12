from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Tuple

from httpx import AsyncClient
from rich.console import Console

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
    The second value stands for their occurences in a simulation setup.
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
    exploiting: dict
    patched: dict


@dataclass
class Service:
    id: int
    name: str
    flags_per_round_multiplier: int
    noises_per_round_multiplier: int
    havocs_per_round_multiplier: int
    weight_factor: int
    checkers: List[str]

    @staticmethod
    def from_(service):
        new_service = Service(
            id=service["id"],
            name=service["name"],
            flags_per_round_multiplier=service["flagsPerRoundMultiplier"],
            noises_per_round_multiplier=service["noisesPerRoundMultiplier"],
            havocs_per_round_multiplier=service["havocsPerRoundMultiplier"],
            weight_factor=service["weightFactor"],
            checkers=service["checkers"],
        )
        return new_service


@dataclass
class IpAddresses:
    public_ip_addresses: dict
    private_ip_addresses: dict


@dataclass
class ConfigSetup:
    ssh_config_path: str
    location: str
    vm_size: str
    vm_image_references: dict

    @staticmethod
    def from_(setup):
        new_setup = ConfigSetup(
            ssh_config_path=setup["ssh-config-path"],
            location=setup["location"],
            vm_size=setup["vm-size"],
            vm_image_references=setup["vm-image-references"],
        )
        return new_setup


@dataclass
class ConfigSettings:
    duration_in_minutes: int
    teams: int
    vulnboxes: int
    services: List[str]
    checker_ports: List[int]
    simulation_type: str

    @staticmethod
    def from_(settings):
        new_settings = ConfigSettings(
            duration_in_minutes=settings["duration-in-minutes"],
            teams=settings["teams"],
            vulnboxes=settings["vulnboxes"],
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
        new_config = Config(
            setup=ConfigSetup.from_(config["setup"]),
            settings=ConfigSettings.from_(config["settings"]),
            ctf_json=ConfigCtfJson.from_(config["ctf-json"]),
        )
        return new_config


@dataclass
class VmSecrets:
    github_personal_access_token: str
    ssh_public_key_path: str
    ssh_private_key_path: str

    @staticmethod
    def from_(vm_secrets):
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
        new_secrets = Secrets(
            vm_secrets=VmSecrets.from_(secrets["vm-secrets"]),
            cloud_secrets=CloudSecrets.from_(secrets["cloud-secrets"]),
        )
        return new_secrets


@dataclass
class HelperType:
    config: Config
    secrets: Secrets
    setup_path: str
    use_vm_images: bool


@dataclass
class TeamGeneratorType:
    config: Config


@dataclass
class SetupHelperType:
    config: Config
    secrets: Secrets
    helpers: Dict[SetupVariant, HelperType]
    team_gen: TeamGeneratorType


@dataclass
class SetupType:
    ips: IpAddresses
    teams: Dict[str, Team]
    services: Dict[str, Service]
    verbose: bool
    config: Config
    secrets: Secrets
    skip_infra: bool
    setup_path: str
    setup_helper: SetupHelperType
    console: Console


@dataclass
class FlagSubmitterType:
    config: Config
    secrets: Secrets
    ip_addresses: IpAddresses
    verbose: bool
    usernames: Dict[SetupVariant, str]
    console: Console


@dataclass
class StatCheckerType:
    config: Config
    secrets: Secrets
    usernames: Dict[SetupVariant, str]
    console: Console


@dataclass
class OrchestratorType:
    setup: SetupType
    verbose: bool
    service_info: Dict[str, Tuple[str, str]]
    attack_info: Dict
    client: AsyncClient
    flag_submitter: FlagSubmitterType
    stat_checker: StatCheckerType
    console: Console
