from taskschedule.config_parser import ConfigParser


class TestConfigParser:
    def test_config_parser(self):
        parser = ConfigParser()
        assert parser.config()
