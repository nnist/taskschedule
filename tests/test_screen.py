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
        assert f"{count} tasks" in str(footnote)

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
