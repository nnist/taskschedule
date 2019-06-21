# pylint: disable=missing-docstring,no-self-use

import unittest
import os
import sys
from datetime import datetime
import shutil
import curses

from tasklib import TaskWarrior, Task

from taskschedule.screen import Screen
from taskschedule.schedule import TaskDirDoesNotExistError,\
                                  TaskrcDoesNotExistError

from .context import taskschedule


class ScreenTest(unittest.TestCase):
    def setUp(self):
        self.taskrc_path = 'tests/test_data/.taskrc'
        self.task_dir_path = 'tests/test_data/.task'
        self.assertEqual(os.path.isdir(self.taskrc_path), False)
        self.assertEqual(os.path.isdir(self.task_dir_path), False)

        # Create a sample .taskrc
        with open(self.taskrc_path, 'w+') as file:
            file.write('# User Defined Attributes\n')
            file.write('uda.estimate.type=duration\n')
            file.write('uda.estimate.label=Est\n')

        # Create a sample empty .task directory
        os.makedirs(self.task_dir_path)

        self.screen = Screen(tw_data_dir=self.task_dir_path,
                             taskrc_location=self.taskrc_path)

    def tearDown(self):
        try:
            os.remove(self.taskrc_path)
        except FileNotFoundError:
            pass

        try:
            shutil.rmtree(self.task_dir_path)
        except FileNotFoundError:
            pass

        # Attempt to gracefully quit curses mode if it is active
        # to prevent messing up terminal
        try:
            curses.endwin()
        except:
            pass

    def test_screen_refresh_buffer(self):
        self.screen.refresh_buffer()

    def test_screen_draw(self):
        self.screen.draw()


if __name__ == '__main__':
    unittest.main()
