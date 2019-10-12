from datetime import datetime

from taskschedule.scheduled_task import PatchedTaskWarrior, ScheduledTask


def calculate_datetime(date_str: str) -> datetime:
    """Leverage the `task calc` command to convert a date-like string
       to a datetime object."""

    tw = PatchedTaskWarrior()
    task = ScheduledTask(tw, description="dummy")
    task["due"] = date_str
    return task["due"]
