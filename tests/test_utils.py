from taskschedule.utils import calculate_date
from datetime import date, timedelta


def test_calculate_date():
    assert calculate_date("today") == date.today()
    assert calculate_date("2000-01-01") == date(2000, 1, 1)
    assert calculate_date("today+5days") == date.today() + timedelta(days=5)
