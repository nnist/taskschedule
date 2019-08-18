# pylint: disable=missing-docstring,no-self-use

import unittest
import os
import shutil
import datetime

from tasklib import TaskWarrior, Task

from taskschedule.schedule import Schedule
from taskschedule.scheduled_task import ScheduledTask


class ScheduledTaskTest(unittest.TestCase):
    def setUp(self):
        self.taskrc_path = "tests/test_data/.taskrc"
        self.task_dir_path = "tests/test_data/.task"
        self.assertEqual(os.path.isdir(self.taskrc_path), False)
        self.assertEqual(os.path.isdir(self.task_dir_path), False)

        # Create a sample .taskrc
        with open(self.taskrc_path, "w+") as file:
            file.write("# User Defined Attributes\n")
            file.write("uda.estimate.type=duration\n")
            file.write("uda.estimate.label=Est\n")
            file.write("# User Defined Attributes\n")
            file.write("uda.tb_estimate.type=numeric\n")
            file.write("uda.tb_estimate.label=Est\n")
            file.write("uda.tb_real.type=numeric\n")
            file.write("uda.tb_real.label=Real\n")

        # Create a sample empty .task directory
        os.makedirs(self.task_dir_path)

        taskwarrior = TaskWarrior(
            data_location=self.task_dir_path,
            create=True,
            taskrc_location=self.taskrc_path,
        )
        taskwarrior.overrides.update({"uda.estimate.type": "duration"})
        taskwarrior.overrides.update({"uda.estimate.label": "Est"})
        Task(
            taskwarrior,
            description="test_yesterday",
            schedule="yesterday",
            estimate="20min",
        ).save()
        Task(
            taskwarrior,
            description="test_9:00_to_10:11",
            schedule="today+9hr",
            estimate="71min",
            project="test",
        ).save()
        Task(
            taskwarrior,
            description="test_14:00_to_16:00",
            schedule="today+14hr",
            estimate="2hr",
        ).save()
        Task(
            taskwarrior,
            description="test_tomorrow",
            schedule="tomorrow",
            estimate="24min",
        ).save()
        Task(
            taskwarrior, description="test_tomorrow_+_2_day", schedule="tomorrow+2day"
        ).save()

        self.tasks = taskwarrior.tasks.filter(status="pending")
        self.schedule = Schedule(
            tw_data_dir=self.task_dir_path,
            tw_data_dir_create=True,
            taskrc_location=self.taskrc_path,
        )
        self.schedule.load_tasks()

    def tearDown(self):
        try:
            os.remove(self.taskrc_path)
        except FileNotFoundError:
            pass

        try:
            shutil.rmtree(self.task_dir_path)
        except FileNotFoundError:
            pass


if __name__ == "__main__":
    unittest.main()
