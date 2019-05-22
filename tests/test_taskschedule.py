import subprocess
import unittest
import os
from datetime import datetime

from .context import taskschedule
from taskschedule.taskschedule import Schedule

from tasklib import TaskWarrior, Task


class TaskscheduleTest(unittest.TestCase):
    def setUp(self):
        taskwarrior = TaskWarrior(data_location='tests/test_data/.task',
                                  create=True)
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
                                 tw_data_dir_create=True)

    def tearDown(self):
        os.remove(os.path.dirname(__file__) + '/test_data/.task/backlog.data')
        os.remove(os.path.dirname(__file__) + '/test_data/.task/completed.data')
        os.remove(os.path.dirname(__file__) + '/test_data/.task/pending.data')
        os.remove(os.path.dirname(__file__) + '/test_data/.task/undo.data')

    def test_schedule_can_be_initialized(self):
        schedule = Schedule()
        assert schedule is not None

    def test_get_tasks_returns_correct_tasks(self):
        self.schedule.get_tasks()

        date_str = datetime.now().strftime('%Y-%m-%d')

        task = self.schedule.tasks[0]
        assert str(task['description']) == 'test_9:00_to_10:11'
        assert str(task['scheduled']) == '{} 09:00:00+02:00'.format(date_str)
        assert str(task['estimate']) == 'PT1H11M'

        task = self.schedule.tasks[1]
        assert str(task['description']) == 'test_14:00_to_16:00'
        assert str(task['scheduled']) == '{} 14:00:00+02:00'.format(date_str)
        assert str(task['estimate']) == 'PT2H'

        task = self.schedule.tasks[2]
        assert str(task['description']) == 'test_16:10_to_16:34'
        assert str(task['scheduled']) == '{} 16:10:00+02:00'.format(date_str)
        assert str(task['estimate']) == 'PT24M'

    def test_format_task_returns_correct_format(self):
        self.schedule.get_tasks()

        task = self.schedule.tasks[0]
        assert self.schedule.format_task(task) == [9, '○', 2, '09:00-10:11',
                                                   'test_9:00_to_10:11']

        task = self.schedule.tasks[1]
        assert self.schedule.format_task(task) == [14, '○', 3, '14:00-16:00',
                                                   'test_14:00_to_16:00']

        task = self.schedule.tasks[2]
        assert self.schedule.format_task(task) == [16, '○', 4, '16:10-16:34',
                                                   'test_16:10_to_16:34']

    def test_format_as_table_returns_correct_format(self):
        expected_rows = [
            '        ID    Time         Description',
            ' 0',
            ' 1',
            ' 2',
            ' 3',
            ' 4',
            ' 5',
            ' 6',
            ' 7',
            ' 8',
            ' 9  ○   2     09:00-10:11  test_9:00_to_10:11',
            '10',
            '11',
            '12',
            '13',
            '14  ○   3     14:00-16:00  test_14:00_to_16:00',
            '15',
            '16  ○   4     16:10-16:34  test_16:10_to_16:34',
            '17',
            '18',
            '19',
            '20',
            '21',
            '22',
            '23'
        ]

        self.schedule.get_tasks()
        table = self.schedule.format_as_table()
        rows = table.split('\n')

        assert rows == expected_rows

    def test_cli_returns_0(self):
        process = subprocess.run(['python3 taskschedule/taskschedule.py'],
                                 shell=True,
                                 timeout=10,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE, check=True)
        assert process.returncode == 0

    def test_cli_help_returns_help_message(self):
        process = subprocess.run(['python3 taskschedule/taskschedule.py -h'],
                                 shell=True,
                                 timeout=10,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE, check=True)
        output = process.stdout.split(b'\n')
        assert output[0].startswith(b'usage:')


if __name__ == '__main__':
    unittest.main()
