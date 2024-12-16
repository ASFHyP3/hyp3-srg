def test_hyp3_srg(script_runner):
    ret = script_runner.run(['python', '-m', 'hyp3_srg', '-h'])
    assert ret.success
