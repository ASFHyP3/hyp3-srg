from unittest import mock

import pytest

from hyp3_back_projection import back_projection, utils


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


def test_back_project_single_granule(tmp_path, monkeypatch):
    granule_path = tmp_path / 'granule.SAFE'
    orbit_path = tmp_path / 'orbit.xml'
    with pytest.raises(FileNotFoundError):
        back_projection.back_project_single_granule(granule_path, orbit_path, tmp_path)

    for f in ['elevation.dem', 'elevation.dem.rsc', 'params']:
        (tmp_path / f).touch()

    cleanup_file = tmp_path / 'foo_positionburst_bar.tiff'
    cleanup_file.touch()

    with monkeypatch.context() as m:
        mock_call_stanford_module = mock.Mock()
        m.setattr(utils, 'call_stanford_module', mock_call_stanford_module)
        back_projection.back_project_single_granule(granule_path, orbit_path, tmp_path)
        mock_call_stanford_module.assert_called_once_with(
            'sentinel/sentinel_scene_cpu.py',
            [str(granule_path.with_suffix('')), str(orbit_path)],
            work_dir=tmp_path,
        )
    assert not cleanup_file.exists()
