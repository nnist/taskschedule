import os
import subprocess
from typing import List
from scheduled_task import ScheduledTask, PatchedTaskWarrior


class Notifier:
    def __init__(self):
        taskwarrior = PatchedTaskWarrior(
            data_location="~/.task",
            create=False,
            taskrc_location="~/.taskrc",
            task_command="task scheduled.after:today-1sec scheduled.before:now",
        )
        self.tasks: List[ScheduledTask] = taskwarrior.tasks

    def notify(self, task: ScheduledTask):
        """Send a notification for the given task."""

        home = os.path.expanduser("~")
        summary: str = "Scheduled task: {}".format(task["id"])
        body: str = "{}".format(task["description"])
        urgency: str = "critical"

        subprocess.run(["notify-send", "--urgency", urgency, summary, body])

        subprocess.Popen(
            ["aplay", home + "/.taskschedule/hooks/drip.wav"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
        )

    def send_notifications(self):
        """Send notifications for scheduled tasks that should be started."""

        for task in self.tasks:
            if not task.notified:
                self.notify(task)


if __name__ == "__main__":
    notifier = Notifier()
    notifier.send_notifications()
