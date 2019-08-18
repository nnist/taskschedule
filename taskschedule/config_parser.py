DEFAULTS: dict = {
    'timebox': {
        'time': 25,
        'pending_glyph': '◻',
        'done_glyph': '◼',
        'underestimated_glyph': '◆',
    }
}


class ConfigParser():
    def config(self) -> dict:
        """Returns a default configuration."""
        cfg: dict = DEFAULTS
        return cfg
