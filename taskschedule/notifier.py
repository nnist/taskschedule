import time
import os
import subprocess
from typing import List
from scheduled_task import ScheduledTask, PatchedTaskWarrior
import argparse
import sys


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

        for task in self.tasks:
            if not task.notified:
                self.notify(task)


def main(argv):
    parser = argparse.ArgumentParser(
        description="""Send notifications for scheduled tasks."""
    )
    parser.add_argument(
        "-r", "--rate", help="check tasks every n seconds", type=int, default=0
    )
    args = parser.parse_args(argv)

    while True:
        notifier = Notifier()
        notifier.send_notifications()

        if args.refresh:
            time.sleep(args.refresh)
        else:
            break


if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except KeyboardInterrupt:
        print("Interrupted by user.")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)  # pylint: disable=protected-access
