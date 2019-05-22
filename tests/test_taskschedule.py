import unittest
import os

from .context import taskschedule
from taskschedule.taskschedule import Schedule

from tasklib import TaskWarrior, Task


class TaskscheduleTest(unittest.TestCase):
    def setUp(self):
        taskwarrior = TaskWarrior(data_location='tests/test_data/.task',
                                  create=True)
        Task(taskwarrior, description='test_9:00_to_10:11',
             scheduled='09:00', estimate='71min').save()
        Task(taskwarrior, description='test_14:00_to_16:00',
             scheduled='14:00', estimate='2hr').save()
        Task(taskwarrior, description='test_16:10_to_16:34',
             scheduled='16:10', estimate='24min').save()

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
