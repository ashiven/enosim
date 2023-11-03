def test_flag_submitter(simulation_container):
    flag_submitter = simulation_container.flag_submitter()

    assert flag_submitter.verbose == False
