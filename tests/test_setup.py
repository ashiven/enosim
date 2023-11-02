import os

import pytest


def test_team_generator_basic_stress_test(setup_container):
    setup_container.reset_singletons()
    setup_container.configuration.config.from_dict(
        {"settings": {"teams": 50, "simulation-type": "basic-stress-test"}}
    )
    team_generator = setup_container.team_generator()
    assert all([exp.name == "HAXXOR" for exp in team_generator.team_distribution])

    ctf_json_teams, setup_teams = team_generator.generate()
    assert len(ctf_json_teams) == 1
    assert len(ctf_json_teams) == len(setup_teams)


def test_team_generator_stress_test(setup_container):
    setup_container.reset_singletons()
    setup_container.configuration.config.from_dict(
        {"settings": {"teams": 3, "simulation-type": "stress-test"}}
    )
    team_generator = setup_container.team_generator()
    assert all([exp.name == "HAXXOR" for exp in team_generator.team_distribution])

    ctf_json_teams, setup_teams = team_generator.generate()
    assert len(ctf_json_teams) == 3
    assert len(ctf_json_teams) == len(setup_teams)


def test_team_generator_realistic(setup_container, test_setup_dir):
    setup_container.reset_singletons()
    setup_container.configuration.config.from_dict(
        {"settings": {"teams": 15, "simulation-type": "realistic"}}
    )
    team_generator = setup_container.team_generator()
    assert all(
        [
            team_exp in [exp.name for exp in team_generator.team_distribution]
            for team_exp in ["NOOB", "BEGINNER", "INTERMEDIATE", "ADVANCED", "PRO"]
        ]
    )
    ctf_json_teams, setup_teams = team_generator.generate()
    assert len(ctf_json_teams) == 15
    assert len(ctf_json_teams) == len(setup_teams)


@pytest.mark.asyncio
async def test_setup_helper_azure(mock_fs, setup_container, test_setup_dir):
    mock_fs.add_real_directory(test_setup_dir, read_only=False)
    setup_container.reset_singletons()
    setup_container.configuration.config.from_dict(
        {
            "setup": {
                "location": "azure",
            },
            "settings": {
                "teams": 3,
                "simulation-type": "realistic",
            },
        }
    )
    setup_helper = setup_container.setup_helper()
    list(setup_helper.helpers.values())[0].setup_path = test_setup_dir + "/azure"
    await setup_helper.convert_templates()

    assert os.path.exists(test_setup_dir + "/azure/data/checker.sh")
    assert os.path.exists(test_setup_dir + "/azure/data/docker-compose.yml")
    assert os.path.exists(test_setup_dir + "/azure/data/engine.sh")
    assert os.path.exists(test_setup_dir + "/azure/data/vulnbox.sh")
    assert os.path.exists(test_setup_dir + "/azure/build.sh")
    assert os.path.exists(test_setup_dir + "/azure/deploy.sh")
    assert os.path.exists(test_setup_dir + "/azure/main.tf")
    assert os.path.exists(test_setup_dir + "/azure/outputs.tf")
    assert os.path.exists(test_setup_dir + "/azure/variables.tf")
    assert os.path.exists(test_setup_dir + "/azure/versions.tf")

    # TODO: - test ip address parsing


@pytest.mark.asyncio
async def test_setup_helper_hetzner(mock_fs, setup_container, test_setup_dir):
    mock_fs.add_real_directory(test_setup_dir, read_only=False)
    setup_container.reset_singletons()
    setup_container.configuration.config.from_dict(
        {
            "setup": {
                "location": "hetzner",
            },
            "settings": {
                "teams": 90,
                "simulation-type": "stress-test",
            },
        }
    )
    setup_helper = setup_container.setup_helper()
    list(setup_helper.helpers.values())[1].setup_path = test_setup_dir + "/hetzner"
    await setup_helper.convert_templates()

    assert os.path.exists(test_setup_dir + "/hetzner/data/checker.sh")
    assert os.path.exists(test_setup_dir + "/hetzner/data/docker-compose.yml")
    assert os.path.exists(test_setup_dir + "/hetzner/data/engine.sh")
    assert os.path.exists(test_setup_dir + "/hetzner/data/vulnbox.sh")
    assert os.path.exists(test_setup_dir + "/hetzner/build.sh")
    assert os.path.exists(test_setup_dir + "/hetzner/deploy.sh")
    assert os.path.exists(test_setup_dir + "/hetzner/main.tf")
    assert os.path.exists(test_setup_dir + "/hetzner/outputs.tf")
    assert os.path.exists(test_setup_dir + "/hetzner/variables.tf")
    assert os.path.exists(test_setup_dir + "/hetzner/versions.tf")

    # TODO: - test ip address parsing


# TODO: - implement
@pytest.mark.asyncio
async def test_setup_helper_azure(mock_fs, setup_container, test_setup_dir):
    pass


@pytest.mark.asyncio
async def test_setup_configure(mock_fs, setup_container, test_setup_dir):
    # TODO:
    # - patch execute_command() with a mock
    # - check if correct commands are executed
    # - check if correct files are created
    # - check if correct files are deleted
    pass
