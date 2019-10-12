import curses
import time
import datetime
from typing import List
import math

from taskschedule.scheduled_task import ScheduledTask
from taskschedule.hooks import run_hooks
from taskschedule.config_parser import ConfigParser


class Screen:
    """This class handles the rendering of the schedule."""

    def __init__(
        self,
        schedule,
        scheduled_after,
        scheduled_before,
        hide_projects=False,
        hide_empty=False,
    ):
        self.config = ConfigParser().config()
        # TODO Calculate these dates outside of this class
        self.scheduled_before = scheduled_before
        self.scheduled_after = scheduled_after

        self.stdscr = curses.initscr()
        self.stdscr.nodelay(True)
        self.stdscr.scrollok(True)
        self.stdscr.idlok(True)
        curses.noecho()

        self.pad = curses.newpad(800, 800)
        self.scroll_level = 0

        self.hide_projects = hide_projects
        self.hide_empty = hide_empty
        self.buffer = []
        self.prev_buffer = []
        self.init_colors()

        self.current_task = None

        self.schedule = schedule

    def close(self):
        """Close the curses screen."""
        curses.endwin()

    def init_colors(self):
        """Initialize the colors."""
        curses.curs_set(0)
        curses.start_color()
        if curses.can_change_color():
            curses.init_pair(1, 20, curses.COLOR_BLACK)
            curses.init_pair(2, 8, 0)
            curses.init_pair(3, 20, 234)
            curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_BLACK)
            curses.init_pair(5, curses.COLOR_GREEN, curses.COLOR_BLACK)
            curses.init_pair(6, 19, 234)
            curses.init_pair(7, 19, 0)
            curses.init_pair(8, curses.COLOR_BLACK, curses.COLOR_GREEN)
            curses.init_pair(9, curses.COLOR_BLACK, curses.COLOR_BLACK)
            curses.init_pair(10, curses.COLOR_GREEN, curses.COLOR_BLACK)
            curses.init_pair(11, curses.COLOR_YELLOW, curses.COLOR_BLACK)
            curses.init_pair(12, curses.COLOR_YELLOW, 234)
            curses.init_pair(13, curses.COLOR_GREEN, 234)
            curses.init_pair(14, 8, 0)
            curses.init_pair(15, curses.COLOR_GREEN, curses.COLOR_BLACK)
            curses.init_pair(16, 20, curses.COLOR_BLACK)
            curses.init_pair(17, curses.COLOR_BLUE, curses.COLOR_BLACK)

            # pylint: disable=invalid-name
            self.COLOR_DEFAULT = curses.color_pair(1)
            self.COLOR_DEFAULT_ALTERNATE = curses.color_pair(3)
            self.COLOR_HEADER = curses.color_pair(4) | curses.A_UNDERLINE
            self.COLOR_HOUR = curses.color_pair(2)
            self.COLOR_HOUR_CURRENT = curses.color_pair(5)
            self.COLOR_ACTIVE = curses.color_pair(8)
            self.COLOR_SHOULD_BE_ACTIVE = curses.color_pair(10)
            self.COLOR_SHOULD_BE_ACTIVE_ALTERNATE = curses.color_pair(13)
            self.COLOR_OVERDUE = curses.color_pair(11)
            self.COLOR_OVERDUE_ALTERNATE = curses.color_pair(12)
            self.COLOR_COMPLETED = curses.color_pair(7)
            self.COLOR_COMPLETED_ALTERNATE = curses.color_pair(6)
            self.COLOR_GLYPH = curses.color_pair(9)
            self.COLOR_DIVIDER = curses.color_pair(14)
            self.COLOR_DIVIDER_ACTIVE = curses.color_pair(15)
            self.COLOR_DIVIDER_TEXT = curses.color_pair(16)
            self.COLOR_BLUE = curses.color_pair(17)
        else:
            # pylint: disable=invalid-name
            self.COLOR_DEFAULT = curses.color_pair(0)
            self.COLOR_DEFAULT_ALTERNATE = curses.color_pair(0)
            self.COLOR_HEADER = curses.color_pair(0)
            self.COLOR_HOUR = curses.color_pair(0)
            self.COLOR_HOUR_CURRENT = curses.color_pair(0)
            self.COLOR_ACTIVE = curses.color_pair(0)
            self.COLOR_SHOULD_BE_ACTIVE = curses.color_pair(0)
            self.COLOR_SHOULD_BE_ACTIVE_ALTERNATE = curses.color_pair(0)
            self.COLOR_OVERDUE = curses.color_pair(0)
            self.COLOR_OVERDUE_ALTERNATE = curses.color_pair(0)
            self.COLOR_COMPLETED = curses.color_pair(0)
            self.COLOR_COMPLETED_ALTERNATE = curses.color_pair(0)
            self.COLOR_GLYPH = curses.color_pair(0)
            self.COLOR_DIVIDER = curses.color_pair(0)
            self.COLOR_DIVIDER_ACTIVE = curses.color_pair(0)
            self.COLOR_DIVIDER_TEXT = curses.color_pair(0)
            self.COLOR_BLUE = curses.color_pair(0)

    def get_task_color(self, task, alternate):
        """Return the color for the given task."""
        color = None

        if task.completed:
            if alternate:
                color = self.COLOR_COMPLETED_ALTERNATE
            else:
                color = self.COLOR_COMPLETED
        elif task.active:
            color = self.COLOR_ACTIVE
        elif task.should_be_active:
            if alternate:
                color = self.COLOR_SHOULD_BE_ACTIVE_ALTERNATE
            else:
                color = self.COLOR_SHOULD_BE_ACTIVE
        elif task.overdue and not task.completed:
            if alternate:
                color = self.COLOR_OVERDUE_ALTERNATE
            else:
                color = self.COLOR_OVERDUE
        else:
            if alternate:
                color = self.COLOR_DEFAULT_ALTERNATE
            else:
                color = self.COLOR_DEFAULT

        return color

    def get_maxyx(self):
        """Return the screen's maximum height and width."""
        max_y, max_x = self.stdscr.getmaxyx()
        return max_y, max_x

    def scroll(self, direction):
        """Scroll the curses pad by n lines."""
        max_y, max_x = self.get_maxyx()
        self.scroll_level += direction
        if self.scroll_level < 0:
            self.scroll_level = 0

        self.stdscr.refresh()
        self.pad.refresh(self.scroll_level + 1, 0, 1, 0, max_y - 3, max_x - 1)

    def draw_footnote(self):
        """Draw the footnote at the bottom of the screen."""
        max_y, max_x = self.get_maxyx()

        # Draw timebox status
        timeboxed_task: ScheduledTask = self.schedule.get_active_timeboxed_task()
        if timeboxed_task:
            active_start_time: datetime.datetime = timeboxed_task["start"]
            active_start_time.replace(tzinfo=None)
            current_time = datetime.datetime.now()
            active_time = current_time.timestamp() - active_start_time.timestamp()
            max_duration = datetime.timedelta(
                minutes=self.config["timebox"]["time"]
            ).total_seconds()
            progress: float = (active_time / max_duration) * 100

            if progress > 99:
                self.schedule.stop_active_timeboxed_task()
                real = timeboxed_task["tb_real"]
                if real:
                    timeboxed_task["tb_real"] = int(real) + 1
                else:
                    timeboxed_task["tb_real"] = 1
                timeboxed_task.save()
                self.stdscr.move(max_y - 2, 0)
                self.stdscr.clrtoeol()
            else:
                progress_done: int = math.ceil(progress / 4)
                progress_remaining: int = int((100 - progress) / 4)

                # Draw task id
                task_id = timeboxed_task["id"]
                task_id_str = f"task {task_id}: "
                self.stdscr.addstr(max_y - 2, 1, task_id_str, self.COLOR_DEFAULT)

                # Draw completed blocks
                completed_blocks: str = self.config["timebox"][
                    "progress_done_glyph"
                ] * progress_done
                self.stdscr.addstr(
                    max_y - 2, 1 + len(task_id_str), completed_blocks, self.COLOR_BLUE
                )

                # Draw pending blocks
                pending_blocks: str = self.config["timebox"][
                    "progress_pending_glyph"
                ] * progress_remaining
                self.stdscr.addstr(
                    max_y - 2,
                    1 + len(task_id_str) + len(completed_blocks),
                    pending_blocks,
                    self.COLOR_HOUR,
                )

                # Draw time
                time1 = datetime.timedelta(seconds=active_time)
                time1_fmt = str(time1).split(".", 2)[0]
                time1_minutes = str(time1_fmt).split(":", 2)[1]
                time1_seconds = str(time1_fmt).split(":", 2)[2]

                time2 = datetime.timedelta(minutes=self.config["timebox"]["time"])
                time2_fmt = str(time2).split(".", 2)[0]
                time2_minutes = str(time2_fmt).split(":", 2)[1]
                time2_seconds = str(time2_fmt).split(":", 2)[2]

                progress_time: str = f"{time1_minutes}:{time1_seconds}/{time2_minutes}:{time2_seconds}"
                self.stdscr.addstr(
                    max_y - 2,
                    1
                    + len(task_id_str)
                    + len(completed_blocks)
                    + len(pending_blocks)
                    + 1,
                    progress_time,
                    self.COLOR_DEFAULT,
                )
        else:
            self.stdscr.addstr(max_y - 2, 1, "no active timebox", self.COLOR_DEFAULT)

        estimated_count = self.schedule.get_timebox_estimate_count()
        real_count = self.schedule.get_timebox_real_count()

        footnote_timebox_right: str = f"total: {real_count} / {estimated_count}"

        self.stdscr.addstr(
            max_y - 2,
            max_x - len(footnote_timebox_right) - 1,
            footnote_timebox_right,
            self.COLOR_DEFAULT,
        )

        # Draw footnote
        if self.scheduled_before and self.scheduled_after:
            footnote = "{} tasks - from {} until {}".format(
                len(self.schedule.tasks), self.scheduled_after, self.scheduled_before
            )
        else:
            footnote = "{} tasks - {}".format(len(self.schedule.tasks), self.scheduled)

        self.stdscr.addstr(max_y - 1, 1, footnote, self.COLOR_DEFAULT)

    def draw(self, force=False):
        """Draw the current buffer."""
        max_y, max_x = self.get_maxyx()
        if not self.buffer:
            self.stdscr.clear()
            self.stdscr.addstr(0, 0, "No tasks to display.", self.COLOR_DEFAULT)
            self.draw_footnote()
            self.stdscr.refresh()
        else:
            if force or self.prev_buffer != self.buffer:
                self.pad.clear()
                if self.prev_buffer > self.buffer:
                    self.stdscr.clear()
                    self.stdscr.refresh()

                for line, offset, string, color in self.buffer:
                    if line == 0:
                        self.stdscr.addstr(line, offset, string, color)
                    else:
                        self.pad.addstr(line, offset, string, color)

            self.draw_footnote()
            self.pad.refresh(self.scroll_level + 1, 0, 1, 0, max_y - 3, max_x - 1)

    def render_timeboxes(self, task, color) -> List[dict]:
        """Render a task's timebox column."""

        timeboxes: List[dict] = []
        real = 0
        if task["tb_real"]:
            real = task["tb_real"]
            for i in range(task["tb_real"]):
                if i >= task["tb_estimate"]:
                    timeboxes.append(
                        {
                            "char": self.config["timebox"]["underestimated_glyph"],
                            "color": color,
                        }
                    )
                else:
                    timeboxes.append(
                        {"char": self.config["timebox"]["done_glyph"], "color": color}
                    )
        if task["tb_estimate"]:
            for i in range(task["tb_estimate"] - real):
                timeboxes.append(
                    {"char": self.config["timebox"]["pending_glyph"], "color": color}
                )

        return timeboxes

    def refresh_buffer(self):
        """Refresh the buffer."""
        max_y, max_x = self.get_maxyx()
        self.prev_buffer = self.buffer
        self.buffer = []

        self.schedule.load_tasks()
        tasks = self.schedule.tasks

        if not self.schedule.tasks:
            return

        # Run on-progress hook
        current_task = None
        for task_ in tasks:
            if task_.should_be_active:
                current_task = task_

        if current_task is not None:
            if self.current_task is None:
                self.current_task = current_task
                if current_task["id"] != 0:
                    run_hooks("on-progress", data=current_task.as_dict())
            else:
                if self.current_task["id"] != current_task["id"]:
                    self.current_task = current_task
                    if current_task["id"] != 0:
                        run_hooks("on-progress", data=current_task.as_dict())

        # Determine offsets
        offsets = self.schedule.get_column_offsets()
        max_project_column_length = round(max_x / 8)
        if offsets[5] - offsets[4] > max_project_column_length:
            offsets[5] = offsets[4] + max_project_column_length

        # Draw headers
        headers = ["", "", "ID", "Time", "Timeboxes", "Project", "Description"]
        column_lengths = [2, 1]
        column_lengths.append(self.schedule.get_max_length("id"))
        column_lengths.append(11)
        column_lengths.append(9)
        column_lengths.append(max_project_column_length - 1)
        column_lengths.append(self.schedule.get_max_length("description"))

        for i, header in enumerate(headers):
            try:
                extra_length = column_lengths[i] - len(header)
                headers[i] += " " * extra_length
            except IndexError:
                pass

        self.buffer.append((0, offsets[1], headers[2], self.COLOR_HEADER))
        self.buffer.append((0, offsets[2], headers[3], self.COLOR_HEADER))
        self.buffer.append((0, offsets[3], headers[4], self.COLOR_HEADER))
        self.buffer.append((0, offsets[4], headers[5], self.COLOR_HEADER))

        if not self.hide_projects:
            self.buffer.append((0, offsets[5], headers[6], self.COLOR_HEADER))

        # Draw schedule
        alternate = True
        current_line = 1

        # TODO Hide empty hours again
        # if self.hide_empty:
        #    first_task = self.schedule.tasks[0].start
        #    first_hour = first_task.hour
        #    last_task = self.schedule.tasks[-1].start
        #    last_hour = last_task.hour
        # else:
        #    first_hour = 0
        #    last_hour = 23

        time_slots = self.schedule.get_time_slots()
        for day in time_slots:
            # Draw divider
            divider_pt1 = "─" * (offsets[2] - 1)
            self.buffer.append((current_line, 0, divider_pt1, self.COLOR_DIVIDER))

            date_format = "%a %d %b %Y"
            formatted_date = self.schedule.get_calculated_date(day).strftime(
                date_format
            )
            divider_pt2 = " " + formatted_date + " "
            if day == datetime.datetime.now().date().isoformat():
                self.buffer.append(
                    (
                        current_line,
                        len(divider_pt1),
                        divider_pt2,
                        self.COLOR_DIVIDER_ACTIVE,
                    )
                )
            else:
                self.buffer.append(
                    (
                        current_line,
                        len(divider_pt1),
                        divider_pt2,
                        self.COLOR_DIVIDER_TEXT,
                    )
                )

            divider_pt3 = "─" * (max_x - (len(divider_pt1) + len(divider_pt2)))
            self.buffer.append(
                (
                    current_line,
                    len(divider_pt1) + len(divider_pt2),
                    divider_pt3,
                    self.COLOR_DIVIDER,
                )
            )
            current_line += 1
            alternate = False

            for hour in time_slots[day]:
                tasks = time_slots[day][hour]
                if not tasks and not self.hide_empty:
                    # Add empty line
                    if alternate:
                        color = self.COLOR_DEFAULT_ALTERNATE
                    else:
                        color = self.COLOR_DEFAULT

                    # Fill line to screen length
                    self.buffer.append((current_line, 5, " " * (max_x - 5), color))

                    # Draw hour column, highlight current hour
                    current_hour = time.localtime().tm_hour
                    if (
                        int(hour) == current_hour
                        and day == datetime.datetime.now().date().isoformat()
                    ):
                        self.buffer.append(
                            (current_line, 0, hour, self.COLOR_HOUR_CURRENT)
                        )
                    else:
                        self.buffer.append((current_line, 0, hour, self.COLOR_HOUR))

                    current_line += 1
                    alternate = not alternate

                task: ScheduledTask
                for ii, task in enumerate(tasks):
                    color = self.get_task_color(task, alternate)

                    # Only draw hour once for multiple tasks
                    if ii == 0:
                        hour_ = str(hour)
                    else:
                        hour_ = ""

                    # Draw hour column, highlight current hour
                    current_hour = time.localtime().tm_hour
                    if hour_ != "":
                        if (
                            int(hour) == current_hour
                            and day == datetime.datetime.now().date().isoformat()
                        ):
                            self.buffer.append(
                                (current_line, 0, hour_, self.COLOR_HOUR_CURRENT)
                            )
                        else:
                            self.buffer.append(
                                (current_line, 0, hour_, self.COLOR_HOUR)
                            )

                    # Fill line to screen length
                    self.buffer.append((current_line, 5, " " * (max_x - 5), color))

                    # Draw glyph column
                    self.buffer.append((current_line, 3, task.glyph, self.COLOR_GLYPH))

                    # Draw task id column
                    if task["id"] != 0:
                        self.buffer.append((current_line, 5, str(task["id"]), color))

                    # Draw the time column.
                    # Do not show the time if the task is not scheduled at a
                    # specific time, so the column is not cluttered with tasks
                    # having start times as 00:00.
                    start_dt: datetime.datetime = task["scheduled"]
                    if (
                        start_dt.hour == 0
                        and start_dt.minute == 0
                        and start_dt.second == 0
                    ):
                        formatted_time = ""
                    else:
                        start_time = "{}".format(start_dt.strftime("%H:%M"))
                        if task.scheduled_end_time is None:
                            formatted_time = start_time
                        else:
                            end_time = "{}".format(
                                task.scheduled_end_time.strftime("%H:%M")
                            )
                            formatted_time = "{}-{}".format(start_time, end_time)

                    self.buffer.append(
                        (current_line, offsets[2], formatted_time, color)
                    )

                    # Draw timeboxes column
                    timeboxes = self.render_timeboxes(task, color)
                    for i, timebox in enumerate(timeboxes):
                        self.buffer.append(
                            (
                                current_line,
                                offsets[3] + i,
                                timebox.get("char"),
                                timebox.get("color"),
                            )
                        )

                    # Optionally draw project column
                    offset = 0
                    if not self.hide_projects:
                        if task["project"] is None:
                            project = ""
                        else:
                            max_length = offsets[5] - offsets[4] - 1
                            project = task["project"][0:max_length]

                        self.buffer.append((current_line, offsets[4], project, color))
                        offset = offsets[5]
                    else:
                        offset = offsets[4]

                    # Draw description column
                    description = task["description"][0 : max_x - offset]
                    self.buffer.append((current_line, offset, description, color))

                    current_line += 1
                    alternate = not alternate
