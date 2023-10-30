from unittest import TestCase


class TestSetup(TestCase):
    def test_team_generator(self, setup_container):
        team_generator = setup_container.team_generator()
        ctf_json_teams, setup_teams = team_generator.generate()
        assert len(ctf_json_teams) == 3
        assert len(ctf_json_teams) == len(setup_teams)

    def test_setup(self):
        pass
