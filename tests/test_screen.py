# pylint: disable=missing-docstring,no-self-use

import unittest
import os
import shutil
import curses
import time

from tasklib import TaskWarrior, Task

from taskschedule.screen import Screen


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
                             taskrc_location=self.taskrc_path,
                             scheduled='today')

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
            self.screen.close()
        except:
            try:
                curses.endwin()
            except:
                pass

    # TODO Move to /tests/functional/
    # def test_screen_refresh_buffer_hide_empty_lines(self):
    #     self.assertEqual(self.screen.buffer, [])

    #     taskwarrior = TaskWarrior(
    #         data_location=self.task_dir_path,
    #         create=True,
    #         taskrc_location=self.taskrc_path)
    #     Task(taskwarrior, description='test_yesterday',
    #          schedule='yesterday', estimate='20min').save()
    #     Task(taskwarrior, description='test_9:00_to_10:11',
    #          schedule='today+9hr', estimate='71min', project='test').save()

    #     self.screen.hide_empty = False
    #     self.screen.refresh_buffer()
    #     self.assertEqual(len(self.screen.buffer), 61)

    # TODO Move to /tests/functional/
    # def test_screen_refresh_buffer_first_time_fills_buffer(self):
    #     self.assertEqual(self.screen.buffer, [])

    #     taskwarrior = TaskWarrior(
    #         data_location=self.task_dir_path,
    #         create=True,
    #         taskrc_location=self.taskrc_path)
    #     Task(taskwarrior, description='test_yesterday',
    #          schedule='yesterday', estimate='20min').save()
    #     Task(taskwarrior, description='test_9:00_to_10:11',
    #          schedule='today+9hr', estimate='71min', project='test').save()

    #     self.screen.refresh_buffer()
    #     self.assertEqual(len(self.screen.buffer), 15)

    # TODO Move to /tests/functional/
    # def test_screen_refresh_buffer_no_tasks(self):
    #     self.assertEqual(self.screen.buffer, [])
    #     self.screen.refresh_buffer()
    #     self.assertEqual(self.screen.buffer, [])

    def test_screen_draw_no_tasks_to_display(self):
        self.screen.draw()

    def test_screen_draw(self):
        taskwarrior = TaskWarrior(
            data_location=self.task_dir_path,
            create=True,
            taskrc_location=self.taskrc_path)
        Task(taskwarrior, description='test_yesterday',
             schedule='yesterday', estimate='20min').save()
        Task(taskwarrior, description='test_9:00_to_10:11',
             schedule='today+9hr', estimate='71min', project='test').save()

        self.screen.draw()
        self.screen.refresh_buffer()
        Task(taskwarrior, description='test_14:00_to_16:00',
             schedule='today+14hr', estimate='2hr').save()
        time.sleep(0.1)
        self.screen.draw()
        self.screen.refresh_buffer()
        Task(taskwarrior, description='test_tomorrow',
             schedule='tomorrow', estimate='24min').save()
        time.sleep(0.1)
        self.screen.draw()
        self.screen.refresh_buffer()

    def test_screen_scroll_up_at_top_is_blocked(self):
        current_scroll_level = self.screen.scroll_level
        self.screen.scroll(-1)
        self.assertEqual(current_scroll_level, self.screen.scroll_level)

    def test_screen_scroll_down_and_up(self):
        current_scroll_level = self.screen.scroll_level
        self.screen.scroll(1)
        self.assertEqual(current_scroll_level + 1, self.screen.scroll_level)

        current_scroll_level = self.screen.scroll_level
        self.screen.scroll(-1)
        self.assertEqual(current_scroll_level - 1, self.screen.scroll_level)


if __name__ == '__main__':
    unittest.main()
