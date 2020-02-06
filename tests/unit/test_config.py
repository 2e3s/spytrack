import unittest

from config import Config


class TestConfig(unittest.TestCase):
    def test_created(self) -> None:
        config = Config.parse({
            "daemon": {
                "port": 1,
                "host": "2",
                "database": "4",
            },
            "gui": {
                "run_daemon": True,
                "interval": 3,
                "start_day_time": "6:00",
                "projects": [
                    {
                        "name": "test1",
                        "rules": [{"app": "Test"}],
                    },
                ],
            },
        })
        self.assertEqual(1, config.port)
        self.assertEqual(3, config.interval)
        self.assertEqual('2', config.host)
        self.assertTrue(config.run_daemon)

        self.assertEqual(2, len(config.projects))
        self.assertEqual('test1', config.projects.projects[0].name)
        self.assertEqual(
            config.projects.none_project,
            config.projects.projects[1].name
        )
        self.assertEqual(1, len(config.projects.projects[0].rules))
        self.assertEqual(
            1,
            len(config.projects.projects[0].rules[0].to_json())
        )
        self.assertEqual(
            "Test",
            config.projects.projects[0].rules[0]["app"]
        )
        self.assertIsNotNone(
            "id" in config.projects.projects[0].rules[0].id
        )

        config.host = '20'
        self.assertEqual('20', config.host)
        config.interval = 30
        self.assertEqual(30, config.interval)
        config.port = 10
        self.assertEqual(10, config.port)
        config.run_daemon = False
        self.assertFalse(config.run_daemon)
