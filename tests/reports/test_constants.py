#  Copyright © 2021 CloudBlue. All rights reserved.

from connect.reports.constants import CLI_ENV, REPORTS_ENV


def test_constants():
    assert 'CLI Tool' == CLI_ENV
    assert 'Connect Reports' == REPORTS_ENV
