import unittest

from config import Config


class TestConfig(unittest.TestCase):
    def test_created(self) -> None:
        config = Config({
            "daemon": {
                "port": 1,
                "host": "2",
                "database": "4",
            },
            "gui": {
                "run_daemon": True,
                "interval": 3,
                "start_date_time": "6:00",
                "projects": [
                    {
                        "name": "test1",
                        "rules": [{"app": "Test"}],
                    },
                ],
            },
        })
        self.assertEqual(1, config.get_port())
        self.assertEqual(3, config.get_interval())
        self.assertEqual('2', config.get_host())
        self.assertTrue(config.is_run_server())

        self.assertEqual(2, len(config.projects))
        self.assertEqual('test1', config.projects[0].name)
        self.assertEqual(config.none_project, config.projects[1].name)
        self.assertEqual(1, len(config.projects[0].rules))
        self.assertEqual(2, len(config.projects[0].rules[0]))
        self.assertEqual("Test", config.projects[0].rules[0]["app"])
        self.assertIsNotNone("id" in config.projects[0].rules[0]['id'])

        config.set_host('20')
        self.assertEqual('20', config.get_host())
        config.set_interval(30)
        self.assertEqual(30, config.get_interval())
        config.set_port(10)
        self.assertEqual(10, config.get_port())
        config.set_run_server(False)
        self.assertFalse(config.is_run_server())
