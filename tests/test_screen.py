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
