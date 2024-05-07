def test_hyp3_back_projection(script_runner):
    ret = script_runner.run(['python', '-m', 'hyp3_back_projection', '-h'])
    assert ret.success
