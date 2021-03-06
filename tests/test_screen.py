from taskschedule.screen import Screen


class TestScreen:
    def test_screen_scroll_up_at_top_is_blocked(self, screen):
        current_scroll_level = screen.scroll_level
        screen.scroll(-1)
        assert current_scroll_level == screen.scroll_level

    def test_screen_scroll_down_and_up(self, screen):
        current_scroll_level = screen.scroll_level
        screen.scroll(1)
        assert current_scroll_level + 1 == screen.scroll_level

        current_scroll_level = screen.scroll_level
        screen.scroll(-1)
        assert current_scroll_level - 1 == screen.scroll_level

    def test_prerender_footnote(self, screen: Screen):
        footnote = screen.prerender_footnote()
        count = len(screen.schedule.tasks)
        assert f"{count} tasks" in footnote

    def test_prerender_buffer(self, screen: Screen):
        header_buffer = screen.prerender_headers()
        assert "ID" in header_buffer[0][2]
        assert header_buffer[0][1] == 5
        assert "Time" in header_buffer[1][2]
        assert header_buffer[1][1] == 7
        assert "Timeboxes" in header_buffer[2][2]
        assert header_buffer[2][1] == 19
        assert "Project" in header_buffer[3][2]
        assert header_buffer[3][1] == 29
        assert "Description" in header_buffer[4][2]
        assert header_buffer[4][1] == 37

    def test_predender_divider(self, screen: Screen):
        divider_buffer = screen.prerender_divider("2019-12-07", 0)
        assert "──────" in divider_buffer[0][2]
        assert "Sat 07 Dec 2019" in divider_buffer[1][2]
        assert divider_buffer[1][1] == 6
        assert (
            "─────────────────────────────────────────────────────────"
            in divider_buffer[2][2]
        )
        assert divider_buffer[2][1] == 23

    def test_prerender_empty_line(self, screen: Screen):
        empty_line_buffer = screen.prerender_empty_line(True, 0, 22, "2019-12-08")
        assert "  " in empty_line_buffer[0][2]
        assert empty_line_buffer[0][1] == 5
        assert empty_line_buffer[1][2] == "22"
        assert empty_line_buffer[1][1] == 0

    def test_prerender_task(self, screen: Screen):
        task = screen.schedule.tasks[0]
        task_buffer = screen.prerender_task(0, task, False, 11, 0, "2019-12-08")
        assert task_buffer[0][1] == 0
        assert "11" in task_buffer[0][2]

        # Glyph column
        assert task_buffer[1][1] == 5
        assert "  " in task_buffer[1][2]

        # ID column
        assert task_buffer[3][1] == 5
        assert "1" in task_buffer[3][2]

        # Time column
        assert task_buffer[4][1] == 7
        assert "00:20" in task_buffer[4][2]

        # Project column
        assert task_buffer[5][1] == 29
        assert task_buffer[5][2] == ""

        # Description column
        assert task_buffer[6][1] == 37
        assert "test_last_week" in task_buffer[6][2]
