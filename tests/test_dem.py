from pathlib import Path
from unittest import mock

from hyp3_srg import dem, utils

from shapely.geometry import box


def test_download_dem_for_back_projection(monkeypatch):
    with monkeypatch.context() as m:
        mock_ensure_egm_model_available = mock.Mock()
        m.setattr(dem, 'ensure_egm_model_available', mock_ensure_egm_model_available)
        mock_call_stanford_module = mock.Mock()
        m.setattr(utils, 'call_stanford_module', mock_call_stanford_module)
        dem.download_dem_for_back_projection(box(0, 1, 2, 3), Path.cwd())
        mock_ensure_egm_model_available.assert_called_once()
        mock_call_stanford_module.assert_called_once_with(
            'DEM/createDEMcop.py',
            [str(Path.cwd() / 'elevation.dem'), str(Path.cwd() / 'elevation.dem.rsc'), 3, 1, 0, 2],
            work_dir=Path.cwd(),
        )
