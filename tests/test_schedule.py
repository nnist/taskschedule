# pylint: disable=missing-docstring,no-self-use

import unittest
import os
import shutil
import datetime

from tasklib import TaskWarrior, Task

from taskschedule.schedule import Schedule, ScheduledTask


class ScheduleTest(unittest.TestCase):
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
            file.write('# User Defined Attributes\n')
            file.write('uda.tb_estimate.type=numeric\n')
            file.write('uda.tb_estimate.label=Est\n')
            file.write('uda.tb_real.type=numeric\n')
            file.write('uda.tb_real.label=Real\n')

        # Create a sample empty .task directory
        os.makedirs(self.task_dir_path)

        taskwarrior = TaskWarrior(
            data_location='tests/test_data/.task',
            create=True,
            taskrc_location='tests/test_data/.taskrc')
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

        self.schedule = Schedule(
            tw_data_dir='tests/test_data/.task',
            tw_data_dir_create=False,
            taskrc_location='tests/test_data/.taskrc')

    def tearDown(self):
        try:
            os.remove(self.taskrc_path)
        except FileNotFoundError:
            pass

        try:
            shutil.rmtree(self.task_dir_path)
        except FileNotFoundError:
            pass

    def test_schedule_can_be_initialized(self):
        schedule = Schedule(
            tw_data_dir='tests/test_data/.task',
            tw_data_dir_create=False,
            taskrc_location='tests/test_data/.taskrc')
        assert schedule is not None

    # TODO Move to /tests/functional/
    # def test_get_tasks_returns_correct_tasks(self):
    #     self.schedule.load_tasks()

    #     date_str = datetime.datetime.now().strftime('%Y-%m-%d')

    #     task: ScheduledTask = self.schedule.tasks[0]
    #     assert str(task['description']) == 'test_9:00_to_10:11'
    #     assert str(task['scheduled'])[0:-6] == '{} 09:00:00'.format(date_str)
    #     assert str(task.scheduled_end_time)[0:-6] == '{} 10:11:00'.format(date_str)

    #     task = self.schedule.tasks[1]
    #     assert str(task['description']) == 'test_14:00_to_16:00'
    #     assert str(task['start'])[0:-6] == '{} 14:00:00'.format(date_str)
    #     assert str(task.scheduled_end_time)[0:-6] == '{} 16:00:00'.format(date_str)

    #     task = self.schedule.tasks[2]
    #     assert str(task['description']) == 'test_16:10_to_16:34'
    #     assert str(task['start'])[0:-6] == '{} 16:10:00'.format(date_str)
    #     assert str(task.scheduled_end_time)[0:-6] == '{} 16:34:00'.format(date_str)

    def test_get_calculated_date_returns_correct_values(self):
        calculated = self.schedule.get_calculated_date('today').date()
        expected = datetime.datetime.now().date()
        self.assertEqual(calculated, expected)

        calculated = self.schedule.get_calculated_date('now+1day').date()
        expected = datetime.datetime.now().date() + datetime.timedelta(days=1)
        self.assertEqual(calculated, expected)

        calculated = self.schedule.get_calculated_date('now+1week').date()
        expected = datetime.datetime.now().date() + datetime.timedelta(days=7)
        self.assertEqual(calculated, expected)

    def test_get_timeslots_returns_correct_amount_of_days(self):
        schedule = Schedule(
            tw_data_dir='tests/test_data/.task',
            tw_data_dir_create=False,
            taskrc_location='tests/test_data/.taskrc',
            scheduled_before='tomorrow+3days',
            scheduled_after='tomorrow-3days',
            scheduled=None)
        output = schedule.get_time_slots()
        self.assertEqual(len(output), 7)

        schedule = Schedule(
            tw_data_dir='tests/test_data/.task',
            tw_data_dir_create=False,
            taskrc_location='tests/test_data/.taskrc',
            scheduled_before='today+15days',
            scheduled_after='today',
            scheduled=None)
        output = schedule.get_time_slots()
        self.assertEqual(len(output), 16)

        schedule = Schedule(
            tw_data_dir='tests/test_data/.task',
            tw_data_dir_create=False,
            taskrc_location='tests/test_data/.taskrc',
            scheduled_before=None,
            scheduled_after=None,
            scheduled='today')
        output = schedule.get_time_slots()
        self.assertEqual(len(output), 1)

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

    def test_get_time_slots(self):
        schedule = Schedule(
            tw_data_dir='tests/test_data/.task',
            tw_data_dir_create=False,
            taskrc_location='tests/test_data/.taskrc')
        schedule.get_time_slots()

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


if __name__ == '__main__':
    unittest.main()
