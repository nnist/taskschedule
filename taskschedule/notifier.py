import os
import subprocess

from taskschedule.scheduled_task import ScheduledTask


class Notifier:
    def __init__(self, backend):
        self.backend = backend

    def notify(self, task: ScheduledTask):
        """Send a notification for the given task."""

        home = os.path.expanduser("~")

        scheduled_time = task["scheduled"]
        scheduled_time_formatted = scheduled_time.strftime("%H:%M")

        task_id: str = task["id"]
        summary: str = f"{scheduled_time_formatted} | Task {task_id}"
        body: str = "{}".format(task["description"])
        urgency: str = "critical"
        uuid: str = task["uuid"]

        if "termux" in str(os.getenv("PREFIX")):
            urgency = "max"
            subprocess.run(
                [
                    "termux-notification",
                    "--title",
                    summary,
                    "--content",
                    body,
                    "--button1",
                    "Start",
                    "--button1-action",
                    f"task {uuid} start",
                    "--button2",
                    "Stop",
                    "--button2-action",
                    f"task {uuid} stop",
                    "--on-delete",
                    "echo deleted",
                    "--action",
                    "echo action",
                    "--id",
                    f"taskschedule-{uuid}",
                    "--vibrate",
                    "200",
                    "--priority",
                    urgency,
                    "--led-off",
                    "200",
                    "--led-on",
                    "200",
                ]
            )
        else:
            subprocess.run(["notify-send", "--urgency", urgency, summary, body])

            subprocess.Popen(
                ["aplay", home + "/.taskschedule/hooks/drip.wav"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.STDOUT,
            )

    def send_notifications(self):
        """Send notifications for scheduled tasks that should be started."""

        tasks = self.backend.tasks.filter(
            "-ACTIVE scheduled.before:now scheduled.after:today"
        )

        for task in tasks:
            if not task.notified:
                self.notify(task)
