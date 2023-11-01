from pytest import fixture

from enosimulator.containers import SetupContainer

config = {
    "setup": {
        "ssh-config-path": "C:/Users/janni/.ssh/simconfig",
        "location": "hetzner",
        "vm-sizes": {
            "vulnbox": "cx11",
            "checker": "cx11",
            "engine": "cx11",
        },
        "vm-image-references": {
            "vulnbox": "vulnbox-checker",
            "checker": "vulnbox-checker",
            "engine": "engine",
        },
    },
    "settings": {
        "duration-in-minutes": 300,
        "teams": 3,
        "services": [
            "enowars7-service-CVExchange",
            "enowars7-service-bollwerk",
        ],
        "checker-ports": [7331, 6008],
        "simulation-type": "stress-test",
    },
    "ctf-json": {
        "title": "ctf-sim",
        "flag-validity-in-rounds": 2,
        "checked-rounds-per-round": 3,
        "round-length-in-seconds": 60,
    },
}
secrets = {
    "vm-secrets": {
        "github-personal-access-token": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u",
        "ssh-public-key-path": "/path/to/your/public_key.pub",
        "ssh-private-key-path": "/path/to/your/private_key",
    },
    "cloud-secrets": {
        "azure-service-principal": {
            "subscription-id": "",
            "client-id": "",
            "client-secret": "",
            "tenant-id": "",
        },
        "hetzner-api-token": "a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6q7r8s9t0u",
    },
}
verbose = False
debug = False


@fixture
def setup_container():
    setup_container = SetupContainer()
    setup_container.configuration.config.from_dict(config)
    setup_container.configuration.secrets.from_dict(secrets)
    return setup_container
