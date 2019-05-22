import unittest
import os

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
        print(self.schedule.tasks)
        assert self.schedule.tasks is not []


if __name__ == '__main__':
    unittest.main()
