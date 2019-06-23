# pylint: disable=missing-docstring,no-self-use

import unittest
import os
import shutil

from taskschedule.schedule import Schedule, UDADoesNotExistError,\
    TaskrcDoesNotExistError,\
    TaskDirDoesNotExistError


class MissingDataTest(unittest.TestCase):
    def setUp(self):
        self.taskrc_path = 'tests/test_data/.taskrc'
        self.task_dir_path = 'tests/test_data/.task'
        self.assertEqual(os.path.isdir(self.taskrc_path), False)
        self.assertEqual(os.path.isdir(self.task_dir_path), False)

    def tearDown(self):
        try:
            os.remove(self.taskrc_path)
        except FileNotFoundError:
            pass

        try:
            shutil.rmtree(self.task_dir_path)
        except FileNotFoundError:
            pass

    def create_schedule(self):
        schedule = Schedule(tw_data_dir=self.task_dir_path,
                            taskrc_location=self.taskrc_path)
        schedule.load_tasks()

    def test_no_uda_estimate_raises_exception(self):
        with open(self.taskrc_path, 'w+') as file:
            file.write('# dummy\n')
        os.makedirs(self.task_dir_path)
        self.assertRaises(UDADoesNotExistError, self.create_schedule)

    def test_no_task_dir_raises_exception(self):
        with open(self.taskrc_path, 'w+') as file:
            file.write('# User Defined Attributes\n')
            file.write('uda.estimate.type=duration\n')
            file.write('uda.estimate.label=Est\n')
        self.assertRaises(TaskDirDoesNotExistError, self.create_schedule)
        os.remove(self.taskrc_path)

    def test_no_taskrc_raises_exception(self):
        os.makedirs(self.task_dir_path)
        self.assertRaises(TaskrcDoesNotExistError, self.create_schedule)

        try:
            shutil.rmtree(self.task_dir_path)
        except FileNotFoundError:
            pass


if __name__ == '__main__':
    unittest.main()
