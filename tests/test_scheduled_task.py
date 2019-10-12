import pytest
from taskschedule.scheduled_task import ScheduledTask
from datetime import datetime, timedelta
from tests.fixtures import tw  # noqa: F401


def test_as_dict(tw):  # noqa: F811
    expected_desc = "Test task"
    task = ScheduledTask(backend=tw, description=expected_desc)

    assert task.as_dict()["description"] == expected_desc


def test_scheduled_end_time(tw):  # noqa: F811
    task = ScheduledTask(
        backend=tw,
        description="Test task",
        scheduled=datetime(2019, 10, 12, 0, 0),
        estimate="PT1H",
    )
    difference = task.scheduled_end_time - task["scheduled"]

    assert difference == timedelta(seconds=3600)


def test_notified(tw):  # noqa: F811
    task = ScheduledTask(
        backend=tw, description="Test task", scheduled=datetime(2019, 10, 12, 0, 0)
    )
    task.save()

    assert task.notified is False
    assert task.notified is True


@pytest.mark.skip(reason="This cannot be tested because the method is currently broken")
def test_should_be_active(tw):  # noqa: F811
    # TODO Complete this test after fixing the class method
    ...


def test_overdue(tw):  # noqa: F811
    future_task = ScheduledTask(
        backend=tw, description="Test task", scheduled=datetime(2313, 10, 12, 0, 0)
    )
    old_task = ScheduledTask(
        backend=tw, description="Test task", scheduled=datetime(1448, 10, 12, 0, 0)
    )

    assert future_task.overdue is False
    assert old_task.overdue is True
