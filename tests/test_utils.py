from datetime import datetime, timedelta

from taskschedule.utils import calculate_datetime


def test_calculate_datetime():
    assert calculate_datetime("2000-01-01").year == 2000
    assert (
        calculate_datetime("today+5days").day
        == (datetime.today() + timedelta(days=5)).day
    )
