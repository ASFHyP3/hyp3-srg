from hyp3_back_projection import back_projection


def test_create_param_file(tmp_path):
    dem_path = tmp_path / 'elevation.dem'
    dem_rsc_path = tmp_path / 'elevation.dem.rsc'
    output_dir = tmp_path
    back_projection.create_param_file(dem_path, dem_rsc_path, output_dir)
    assert (tmp_path / 'params').exists()

    with open(tmp_path / 'params') as f:
        lines = [x.strip() for x in f.readlines()]

    assert len(lines) == 2
    assert lines[0] == str(dem_path)
    assert lines[1] == str(dem_rsc_path)
