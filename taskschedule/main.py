"""Command line interface of taskschedule"""
import argparse
import os
import sys
import time
from curses import KEY_DOWN, KEY_RESIZE, KEY_UP
from curses import error as curses_error
from curses import napms
from typing import Optional

from tasklib import TaskWarrior

from taskschedule.notifier import Notifier, SoundDoesNotExistError
from taskschedule.schedule import (
    Schedule,
    TaskDirDoesNotExistError,
    TaskrcDoesNotExistError,
    UDADoesNotExistError,
)
from taskschedule.screen import Screen
from taskschedule.taskwarrior import PatchedTaskWarrior
from taskschedule.utils import calculate_datetime


class Main:
    def __init__(self, argv):
        self.home_dir = os.path.expanduser("~")

        self.parse_args(argv)
        self.check_files()

    def check_files(self):
        """Check if the required files, directories and settings are present."""
        # Create a temporary taskwarrior instance to read the config
        taskwarrior = TaskWarrior(
            data_location=self.data_location,
            create=False,
            taskrc_location=self.taskrc_location,
        )

        # Disable _forcecolor because it breaks tw config output
        taskwarrior.overrides.update({"_forcecolor": "off"})

        # Check taskwarrior directory and taskrc
        if os.path.isdir(self.data_location) is False:
            raise TaskDirDoesNotExistError(".task directory not found")
        if os.path.isfile(self.taskrc_location) is False:
            raise TaskrcDoesNotExistError(".taskrc not found")

        # Check if required UDAs exist
        if taskwarrior.config.get("uda.estimate.type") is None:
            raise UDADoesNotExistError(
                ("uda.estimate.type does not exist " "in .taskrc")
            )
        if taskwarrior.config.get("uda.estimate.label") is None:
            raise UDADoesNotExistError(
                ("uda.estimate.label does not exist " "in .taskrc")
            )

        # Check sound file
        sound_file = self.home_dir + "/.taskschedule/hooks/drip.wav"
        if os.path.isfile(sound_file) is False:
            raise SoundDoesNotExistError(
                f"The specified sound file does not exist: {sound_file}"
            )

        # Create user directory if it does not exist
        taskschedule_dir = self.home_dir + "/.taskschedule"
        hooks_directory = self.home_dir + "/.taskschedule/hooks"
        if not os.path.isdir(taskschedule_dir):
            os.mkdir(taskschedule_dir)
        if not os.path.isdir(hooks_directory):
            os.mkdir(hooks_directory)

    def parse_args(self, argv):
        parser = argparse.ArgumentParser(
            description="""Display a schedule report for taskwarrior."""
        )
        parser.add_argument(
            "-r", "--refresh", help="refresh every n seconds", type=int, default=1
        )
        parser.add_argument(
            "--from",
            help="scheduled from date: ex. 'today', 'tomorrow'",
            type=str,
            dest="after",
            default="today-1s",
        )
        parser.add_argument(
            "--to",
            "--until",
            help="scheduled until date: ex. 'today', 'tomorrow'",
            type=str,
            dest="before",
            default="tomorrow",
        )
        parser.add_argument(
            "-d",
            "--data-location",
            help="""data location (e.g. ~/.task)""",
            type=str,
            dest="data_location",
            default=f"{self.home_dir}/.task",
        )
        parser.add_argument(
            "-t",
            "--taskrc-location",
            help="""taskrc location (e.g. ~/.taskrc)""",
            type=str,
            dest="taskrc_location",
            default=f"{self.home_dir}/.taskrc",
        )
        parser.add_argument(
            "-a",
            "--all",
            help="show all hours, even if empty",
            action="store_true",
            default=False,
        )
        parser.add_argument(
            "-c",
            "--completed",
            help="hide completed tasks",
            action="store_false",
            default=True,
        )
        parser.add_argument(
            "-p",
            "--project",
            help="hide project column",
            action="store_true",
            default=False,
        )
        parser.add_argument(
            "--no-notifications",
            help="disable notifications",
            action="store_false",
            default=True,
            dest="notifications",
        )
        args = parser.parse_args(argv)

        if args.before and not args.after or not args.before and args.after:
            print(
                "Error: Either both --until and --from or neither options must be used."
            )
            sys.exit(1)

        self.data_location = args.data_location
        self.taskrc_location = args.taskrc_location
        self.scheduled_after = args.after
        self.scheduled_before = args.before
        self.show_completed = args.completed
        self.hide_empty = not args.all
        self.hide_projects = args.project
        self.refresh_rate = args.refresh
        self.show_notifications = args.notifications

    def main(self):
        task_command_args = ["task", "status.not:deleted"]

        # Parse schedule date range
        scheduled_after = calculate_datetime(self.scheduled_after)
        scheduled_before = calculate_datetime(self.scheduled_before)

        task_command_args.append(f"scheduled.after:{scheduled_after}")
        task_command_args.append(f"scheduled.before:{scheduled_before}")

        if not self.show_completed:
            task_command_args.append(f"status.not:{self.show_completed}")

        backend = PatchedTaskWarrior(
            data_location=self.data_location,
            create=False,
            taskrc_location=self.taskrc_location,
            task_command=" ".join(task_command_args),
        )

        schedule = Schedule(
            backend, scheduled_after=scheduled_after, scheduled_before=scheduled_before
        )

        notifier: Optional[Notifier] = None
        if self.show_notifications:
            notifier = Notifier(backend)

        try:
            screen = Screen(
                schedule,
                scheduled_after=scheduled_after,
                scheduled_before=scheduled_before,
                hide_empty=self.hide_empty,
                hide_projects=self.hide_projects,
            )

            # TODO Refresh on any file change in dir instead of every second
            last_refresh_time = 0.0
            while True:
                key = screen.stdscr.getch()
                if key == 113:  # q
                    break
                elif key == 65 or key == 107:  # Up / k
                    screen.scroll(-1)
                    last_refresh_time = time.time()
                elif key == 66 or key == 106:  # Down / j
                    screen.scroll(1)
                    last_refresh_time = time.time()
                elif key == 54:  # Page down
                    max_y, max_x = screen.get_maxyx()
                    screen.scroll(max_y - 4)
                    last_refresh_time = time.time()
                elif key == 53:  # Page up
                    max_y, max_x = screen.get_maxyx()
                    screen.scroll(-(max_y - 4))
                    last_refresh_time = time.time()
                elif (
                    key == KEY_RESIZE
                    or time.time() > last_refresh_time + self.refresh_rate
                ):
                    if notifier:
                        notifier.send_notifications()

                    last_refresh_time = time.time()
                    schedule.clear_cache()
                    screen.refresh_buffer()
                    screen.draw()
                    napms(50)

                napms(1)

                if self.refresh_rate < 0:
                    break
        except TaskDirDoesNotExistError as err:
            print("Error: {}".format(err))
            sys.exit(1)
        except TaskrcDoesNotExistError as err:
            print("Error: {}".format(err))
            sys.exit(1)
        except KeyboardInterrupt:
            screen.close()
        except ValueError as err:
            screen.close()
            print("Error: {}".format(err))
            sys.exit(1)
        except UDADoesNotExistError as err:
            screen.close()
            print("Error: {}".format(err))
            sys.exit(1)
        except SoundDoesNotExistError as err:
            screen.close()
            print("Error: {}".format(err))
            sys.exit(1)
        else:
            try:
                screen.close()
            except curses_error as err:
                print(err.with_traceback)
