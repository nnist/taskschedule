import json

from tasklib import TaskWarrior
from tasklib.backends import TaskWarriorException

from taskschedule.scheduled_task import ScheduledTask, ScheduledTaskQuerySet


class PatchedTaskWarrior(TaskWarrior):
    """A patched version of TaskWarrior which returns a custom queryset with a custom
       Task class to provide extra functionality."""

    def __init__(self, *args, **kwargs):
        super(PatchedTaskWarrior, self).__init__(*args, **kwargs)
        self.tasks = ScheduledTaskQuerySet(self)

    def filter_tasks(self, filter_obj):
        self.enforce_recurrence()
        args = ["export"] + filter_obj.get_filter_params()
        tasks = []
        for line in self.execute_command(args):
            if line:
                data = line.strip(",")
                try:
                    filtered_task = ScheduledTask(self)
                    filtered_task._load_data(json.loads(data))
                    tasks.append(filtered_task)
                except ValueError:
                    raise TaskWarriorException("Invalid JSON: %s" % data)
        return tasks
