from __future__ import annotations

import os
import shutil
from typing import TYPE_CHECKING

import pytest

from taskschedule.schedule import Schedule, ScheduledTask
from taskschedule.screen import Screen
from taskschedule.taskwarrior import PatchedTaskWarrior
from taskschedule.utils import calculate_datetime

if TYPE_CHECKING:
    from datetime import datetime


@pytest.fixture(scope="module")
def tw():
    """Create a PatchedTaskWarrior instance with a temporary .taskrc and data
       location. Remove the temporary data after testing is finished."""

    taskrc_path = "tests/test-data/.taskrc"
    task_dir_path = "tests/test-data/.task"

    # Create a sample .taskrc
    with open(taskrc_path, "w+") as file:
        file.write("# User Defined Attributes\n")
        file.write("uda.estimate.type=duration\n")
        file.write("uda.estimate.label=Est\n")
        file.write("# User Defined Attributes\n")
        file.write("uda.tb_estimate.type=numeric\n")
        file.write("uda.tb_estimate.label=Est\n")
        file.write("uda.tb_real.type=numeric\n")
        file.write("uda.tb_real.label=Real\n")

    # Create a sample empty .task directory
    os.makedirs(task_dir_path)

    tw = PatchedTaskWarrior(
        data_location=task_dir_path, create=True, taskrc_location=taskrc_path
    )
    tw.overrides.update({"uda.estimate.type": "duration"})
    tw.overrides.update({"uda.estimate.label": "Est"})

    yield tw

    try:
        os.remove(taskrc_path)
    except FileNotFoundError:
        pass

    try:
        shutil.rmtree(task_dir_path)
    except FileNotFoundError:
        pass


@pytest.fixture(scope="module")
def schedule(tw):
    """Create a Schedule instance with a few tasks."""
    ScheduledTask(
        tw, description="test_last_week", schedule="yesterday-7days", estimate="20min"
    ).save()
    ScheduledTask(
        tw, description="test_yesterday", schedule="yesterday", estimate="20min"
    ).save()
    ScheduledTask(tw, description="test_0:00", schedule="today").save()
    ScheduledTask(
        tw, description="test_9:00_to_10:11", schedule="today+9hr", estimate="71min"
    ).save()
    ScheduledTask(
        tw, description="test_14:00_to_16:00", schedule="today+14hr", estimate="2hr"
    ).save()
    ScheduledTask(
        tw,
        description="test_16:10_to_16:34",
        schedule="today+16hr+10min",
        estimate="24min",
    ).save()
    ScheduledTask(
        tw, description="test_tomorrow", schedule="tomorrow", estimate="24min"
    ).save()
    ScheduledTask(
        tw, description="test_next_week", schedule="today+7days", estimate="20min"
    ).save()

    scheduled_after: datetime = calculate_datetime("tomorrow-3days")
    scheduled_before: datetime = calculate_datetime("tomorrow+3days")
    schedule = Schedule(
        backend=tw, scheduled_before=scheduled_before, scheduled_after=scheduled_after
    )

    yield schedule


@pytest.fixture(scope="module")
def screen(tw, schedule):
    screen = Screen(schedule, schedule.scheduled_after, schedule.scheduled_before)
    yield screen
