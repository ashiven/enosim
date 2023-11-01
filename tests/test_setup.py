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


def test_team_generator_realistic(setup_container):
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


def test_setup():
    pass
