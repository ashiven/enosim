from enum import Enum

from attr import dataclass


class SetupVariant(Enum):
    AZURE = "azure"
    LOCAL = "local"

    @staticmethod
    def from_str(s):
        if s == "azure":
            return SetupVariant.AZURE
        elif s == "local":
            return SetupVariant.LOCAL
        else:
            raise NotImplementedError


class Experience(Enum):
    """An enum representing the experience level of a team. The value stands for the probability of the team exploiting / patching a vulnerability."""

    NOOB = 0.01
    BEGINNER = 0.05
    INTERMEDIATE = 0.1
    ADVANCED = 0.2
    PRO = 0.3
    HAXXOR = 1

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
    checkers: list
