# pylint: disable=missing-docstring,no-self-use

import unittest
import os
from datetime import datetime
import shutil

from tasklib import TaskWarrior, Task

from taskschedule.schedule import Schedule, UDADoesNotExistError,\
                                  TaskrcDoesNotExistError,\
                                  TaskDirDoesNotExistError
from taskschedule.scheduled_task import ScheduledTask
from .context import taskschedule


class MissingDataTest(unittest.TestCase):
    def setUp(self):
        # Make sure ~/.taskrc and ~/.task/ do not exist to prevent damage
        home = os.path.expanduser("~")
        self.assertEqual(os.path.isfile(home + '/.taskrc'), False)
        self.assertEqual(os.path.isdir(home + '/.task'), False)

    def tearDown(self):
        home = os.path.expanduser("~")
        try:
            os.remove(home + '/.taskrc')
        except FileNotFoundError:
            pass

        try:
            shutil.rmtree(home + '/.task')
        except FileNotFoundError:
            pass

    def create_schedule(self):
        schedule = Schedule()
        schedule.load_tasks()

    def test_no_uda_estimate_raises_exception(self):
        home = os.path.expanduser("~")
        with open(home + '/.taskrc', 'w+') as file:
            file.write('# dummy\n')
        os.makedirs(home + '/.task')
        self.assertRaises(UDADoesNotExistError, self.create_schedule)

    def test_no_task_dir_raises_exception(self):
        home = os.path.expanduser("~")
        with open(home + '/.taskrc', 'w+') as file:
            file.write('# User Defined Attributes\n')
            file.write('uda.estimate.type=duration\n')
            file.write('uda.estimate.label=Est\n')
        self.assertRaises(TaskDirDoesNotExistError, self.create_schedule)
        os.remove(home + '/.taskrc')

    def test_no_taskrc_raises_exception(self):
        home = os.path.expanduser("~")
        os.makedirs(home + '/.task')
        self.assertRaises(TaskrcDoesNotExistError, self.create_schedule)

        try:
            shutil.rmtree(home + '/.task')
        except FileNotFoundError:
            pass


class TaskscheduleTest(unittest.TestCase):
    def setUp(self):
        # Make sure ~/.taskrc and ~/.task/ do not exist to prevent damage
        home = os.path.expanduser("~")
        self.assertEqual(os.path.isfile(home + '/.taskrc'), False)
        self.assertEqual(os.path.isdir(home + '/.task'), False)

        # Create a sample ~/.taskrc
        home = os.path.expanduser("~")
        with open(home + '/.taskrc', 'w+') as file:
            file.write('# User Defined Attributes\n')
            file.write('uda.estimate.type=duration\n')
            file.write('uda.estimate.label=Est\n')

        # Create a sample empty ~/.task directory
        home = os.path.expanduser("~")
        os.makedirs(home + '/.task')

        taskwarrior = TaskWarrior(data_location='tests/test_data/.task',
                                  create=True,
                                  taskrc_location='tests/test_data/.task/.taskrc')
        Task(taskwarrior, description='test_yesterday',
             schedule='yesterday', estimate='20min').save()
        Task(taskwarrior, description='test_9:00_to_10:11',
             schedule='today+9hr', estimate='71min').save()
        Task(taskwarrior, description='test_14:00_to_16:00',
             schedule='today+14hr', estimate='2hr').save()
        Task(taskwarrior, description='test_16:10_to_16:34',
             schedule='today+16hr+10min', estimate='24min').save()
        Task(taskwarrior, description='test_tomorrow',
             schedule='tomorrow', estimate='24min').save()

        self.schedule = Schedule(tw_data_dir='tests/test_data/.task',
                                 tw_data_dir_create=True,
                                 taskrc_location='tests/test_data/.task/.taskrc')

    def tearDown(self):
        home = os.path.expanduser("~")
        try:
            os.remove(home + '/.taskrc')
        except FileNotFoundError:
            pass

        try:
            shutil.rmtree(home + '/.task')
        except FileNotFoundError:
            pass

        os.remove(os.path.dirname(__file__) + '/test_data/.task/backlog.data')
        os.remove(os.path.dirname(__file__) + '/test_data/.task/completed.data')
        os.remove(os.path.dirname(__file__) + '/test_data/.task/pending.data')
        os.remove(os.path.dirname(__file__) + '/test_data/.task/undo.data')

    def test_schedule_can_be_initialized(self):
        schedule = Schedule()
        assert schedule is not None

    def test_get_tasks_returns_correct_tasks(self):
        self.schedule.load_tasks()

        date_str = datetime.now().strftime('%Y-%m-%d')

        task = self.schedule.tasks[0]
        assert str(task.description) == 'test_9:00_to_10:11'
        assert str(task.start)[0:-6] == '{} 09:00:00'.format(date_str)
        assert str(task.end)[0:-6] == '{} 10:11:00'.format(date_str)

        task = self.schedule.tasks[1]
        assert str(task.description) == 'test_14:00_to_16:00'
        assert str(task.start)[0:-6] == '{} 14:00:00'.format(date_str)
        assert str(task.end)[0:-6] == '{} 16:00:00'.format(date_str)

        task = self.schedule.tasks[2]
        assert str(task.description) == 'test_16:10_to_16:34'
        assert str(task.start)[0:-6] == '{} 16:10:00'.format(date_str)
        assert str(task.end)[0:-6] == '{} 16:34:00'.format(date_str)

#   def test_format_task_returns_correct_format(self):
#       self.schedule.get_tasks()

#       task = self.schedule.tasks[0]
#       assert self.schedule.format_task(task) == [9, '○', 2, '09:00-10:11',
#                                                  'test_9:00_to_10:11']

#       task = self.schedule.tasks[1]
#       assert self.schedule.format_task(task) == [14, '○', 3, '14:00-16:00',
#                                                  'test_14:00_to_16:00']

#       task = self.schedule.tasks[2]
#       assert self.schedule.format_task(task) == [16, '○', 4, '16:10-16:34',
#                                                  'test_16:10_to_16:34']

#   def test_format_as_table_returns_correct_format(self):
#       expected_rows = [
#           '        ID    Time         Description',
#           ' 0',
#           ' 1',
#           ' 2',
#           ' 3',
#           ' 4',
#           ' 5',
#           ' 6',
#           ' 7',
#           ' 8',
#           ' 9  ○   2     09:00-10:11  test_9:00_to_10:11',
#           '10',
#           '11',
#           '12',
#           '13',
#           '14  ○   3     14:00-16:00  test_14:00_to_16:00',
#           '15',
#           '16  ○   4     16:10-16:34  test_16:10_to_16:34',
#           '17',
#           '18',
#           '19',
#           '20',
#           '21',
#           '22',
#           '23'
#       ]

#       self.schedule.get_tasks()
#       table = self.schedule.format_as_table(hide_empty=False)
#       rows = table.split('\n')

#       assert rows == expected_rows

#   def test_format_as_table_hide_empty_returns_correct_format(self):
#       expected_rows = [
#           '        ID    Time         Description',
#           ' 8',
#           ' 9  ○   2     09:00-10:11  test_9:00_to_10:11',
#           '10',
#           '11',
#           '12',
#           '13',
#           '14  ○   3     14:00-16:00  test_14:00_to_16:00',
#           '15',
#           '16  ○   4     16:10-16:34  test_16:10_to_16:34',
#           '17'
#       ]

#       self.schedule.get_tasks()
#       table = self.schedule.format_as_table(hide_empty=True)
#       rows = table.split('\n')

#       assert rows == expected_rows

#   def test_cli_returns_0(self):
#       process = subprocess.run(['python3 taskschedule/taskschedule.py'],
#                                shell=True,
#                                timeout=10,
#                                stdout=subprocess.PIPE,
#                                stderr=subprocess.PIPE, check=True)
#       assert process.returncode == 0

    def test_align_matrix(self):
        rows = [
            ['', '', 'ID', 'Time', 'Description'],
            ['8', '', '', '', ''],
            ['9', '○', '2', '09:00-10:11', 'test_9:00_to_10:11'],
            ['10', '', '', '', ''],
            ['11', '', '', '', ''],
            ['14', '○', '654', '12:00', 'test_12:00'],
        ]
        returned_rows = self.schedule.align_matrix(rows)

        expected_rows = [
            ['  ', ' ', 'ID ', 'Time       ', 'Description       '],
            ['8 ', ' ', '   ', '           ', '                  '],
            ['9 ', '○', '2  ', '09:00-10:11', 'test_9:00_to_10:11'],
            ['10', ' ', '   ', '           ', '                  '],
            ['11', ' ', '   ', '           ', '                  '],
            ['14', '○', '654', '12:00      ', 'test_12:00        '],
        ]

        assert returned_rows == expected_rows


class ScheduledTaskTest(unittest.TestCase):
    def setUp(self):
        # Make sure ~/.taskrc and ~/.task/ do not exist to prevent damage
        home = os.path.expanduser("~")
        self.assertEqual(os.path.isfile(home + '/.taskrc'), False)
        self.assertEqual(os.path.isdir(home + '/.task'), False)

        taskwarrior = TaskWarrior(data_location='tests/test_data/.task',
                                  create=True,
                                  taskrc_location='tests/test_data/.task/.taskrc')
        taskwarrior.overrides.update({'uda.estimate.type': 'duration'})
        taskwarrior.overrides.update({'uda.estimate.label': 'Est'})
        Task(taskwarrior, description='test_yesterday',
             schedule='yesterday', estimate='20min').save()
        Task(taskwarrior, description='test_9:00_to_10:11',
             schedule='today+9hr', estimate='71min', project='test').save()
        Task(taskwarrior, description='test_14:00_to_16:00',
             schedule='today+14hr', estimate='2hr').save()
        Task(taskwarrior, description='test_tomorrow',
             schedule='tomorrow', estimate='24min').save()

        self.tasks = taskwarrior.tasks.filter(status='pending')
        self.schedule = Schedule(tw_data_dir='tests/test_data/.task',
                                 tw_data_dir_create=True,
                                 taskrc_location='tests/test_data/.task/.taskrc')
        self.schedule.load_tasks()

    def tearDown(self):
        os.remove(os.path.dirname(__file__) + '/test_data/.task/backlog.data')
        os.remove(os.path.dirname(__file__) + '/test_data/.task/completed.data')
        os.remove(os.path.dirname(__file__) + '/test_data/.task/pending.data')
        os.remove(os.path.dirname(__file__) + '/test_data/.task/undo.data')

    def test_init_works_correctly(self):
        task = ScheduledTask(self.tasks[1], self.schedule)

        self.assertEqual(task.task, self.tasks[1])
        self.assertEqual(task.active, False)
        self.assertEqual(task.completed, False)
        self.assertNotEqual(task.task_id, 0)
        self.assertEqual(task.project, 'test')

        date_str = datetime.now().strftime('%Y-%m-%d')
        self.assertEqual(str(task.description), 'test_9:00_to_10:11')
        self.assertEqual(str(task.start)[0:-6], '{} 09:00:00'.format(date_str))
        self.assertEqual(str(task.end)[0:-6], '{} 10:11:00'.format(date_str))

        self.assertEqual(task.should_be_active, False)

    def test_overdue_task_returns_true(self):
        task = ScheduledTask(self.tasks[0], self.schedule)
        self.assertEqual(task.overdue, True)

    def test_non_overdue_task_returns_false(self):
        task = ScheduledTask(self.tasks[3], self.schedule)
        self.assertEqual(task.overdue, False)


if __name__ == '__main__':
    unittest.main()
