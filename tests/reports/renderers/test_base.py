#  Copyright © 2021 CloudBlue. All rights reserved.

import pytest

from connect.reports.renderers.base import BaseRenderer


def test_base_render():
    with pytest.raises(NotImplementedError):
        BaseRenderer.render(None, None, None)
