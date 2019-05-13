import unittest

import yaml

from config import Project, Rule
from tests.integration import get_current_directory
from pathlib import Path
from config.config_storage import FileConfigStorage, Config


class TestFileConfigStorage(unittest.TestCase):
    def test_save_load(self) -> None:
        filename = '%s/test_save.config.yaml' % get_current_directory()
        save_storage = FileConfigStorage(filename)

        initial_yaml = {
            "daemon": {
                "port": 100,
                "host": "http://save.test",
            },
            "gui": {
                "run_daemon": True,
                "interval": 3,
                "start_date_time": "1:00",
                "projects": [
                    {
                        "name": "test1",
                        "rules": [
                            {"app": "Test"},
                        ],
                    },
                ],
            },
        }
        saved_config = Config(initial_yaml)
        save_storage.save(saved_config)
        file = Path(filename)
        self.assertTrue(file.is_file())

        try:
            load_storage = FileConfigStorage(filename)
            load_config = load_storage.load()

            self.assertEqual("http://save.test", load_config.host)
            self.assertEqual(100, load_config.port)
            self.assertEqual(3, load_config.interval)
            self.assertTrue(load_config.run_daemon)
            self.assertEqual(2, len(load_config.projects))
            self.assertEqual(load_config.none_project, load_config.projects[1].name)
            self.assertIsInstance(load_config.projects[0], Project)
            self.assertIsInstance(load_config.projects[0].rules[0], Rule)

            saved_yaml = yaml.safe_load(file.read_text())
            self.assertEqual(initial_yaml, saved_yaml)
        finally:
            file.unlink()
