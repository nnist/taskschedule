import unittest

from .context import taskschedule
from taskschedule.taskschedule import Schedule


class TaskscheduleTest(unittest.TestCase):
    def setUp(self):
        pass

    def test_schedule_can_be_initialized(self):
        schedule = Schedule()
        assert schedule is not None


if __name__ == '__main__':
    unittest.main()
