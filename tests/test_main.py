# pylint: disable=missing-docstring,no-self-use

import unittest
import os
import shutil

from taskschedule.main import main
from taskschedule.schedule import TaskDirDoesNotExistError


class CLITest(unittest.TestCase):
    def setUp(self):
        self.taskrc_path = 'tests/test_data/.taskrc'
        self.task_dir_path = 'tests/test_data/.task'

    def create_test_files(self, taskrc=True, taskdir=True):
        if taskdir:
            self.assertEqual(os.path.isdir(self.task_dir_path), False)
            # Create a sample empty .task directory
            os.makedirs(self.task_dir_path)
            self.assertEqual(os.path.isdir(self.task_dir_path), True)

        if taskrc:
            self.assertEqual(os.path.isfile(self.taskrc_path), False)
            # Create a sample .taskrc
            with open(self.taskrc_path, 'w+') as file:
                file.write('# User Defined Attributes\n')
                file.write('uda.estimate.type=duration\n')
                file.write('uda.estimate.label=Est\n')

            self.assertEqual(os.path.isfile(self.taskrc_path), True)

    def tearDown(self):
        if os.path.isfile(self.taskrc_path):
            os.remove(self.taskrc_path)

        if os.path.isdir(self.task_dir_path):
            shutil.rmtree(self.task_dir_path)

    def test_main(self):
        self.create_test_files()
        main(['-r', '-1',
              '--data-location', self.task_dir_path,
              '--taskrc-location', self.taskrc_path])

    def test_main_no_task_dir_exits_with_1(self):
        self.create_test_files(taskdir=False)
        try:
            main(['-r', '-1',
                  '--data-location', self.task_dir_path,
                  '--taskrc-location', self.taskrc_path])
        except SystemExit as err:
            if err.code == 1:
                pass
            else:
                self.fail()

    def test_main_no_taskrc_exits_with_1(self):
        self.create_test_files(taskrc=False)
        try:
            main(['-r', '-1',
                  '--data-location', self.task_dir_path,
                  '--taskrc-location', self.taskrc_path])
        except SystemExit as err:
            if err.code == 1:
                pass
            else:
                self.fail()


if __name__ == '__main__':
    unittest.main()
