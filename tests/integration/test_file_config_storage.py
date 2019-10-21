import unittest

import yaml

from config import Project, Rule
from tests.integration import get_current_directory
from pathlib import Path
from config.config_storage import FileConfigStorage
from config.config import Config


class TestFileConfigStorage(unittest.TestCase):
    def test_load_non_existing(self) -> None:
        current_directory = get_current_directory()
        filename = Path(
            '{}/test/test_save.config.yaml'.format(current_directory)
        )
        file = Path(filename)
        self.assertFalse(file.exists())
        self.assertFalse(file.parent.exists())

        save_storage = FileConfigStorage(filename)
        try:
            config = save_storage.load()
            self.assertEqual('http://localhost', config.host)
            self.assertTrue(file.is_file())
        finally:
            file.unlink()
            file.parent.rmdir()

    def test_save_load(self) -> None:
        current_directory = get_current_directory()
        file = Path('{}/test_save.config.yaml'.format(current_directory))
        save_storage = FileConfigStorage(file)

        initial_yaml = {
            "daemon": {
                "port": 100,
                "host": "http://save.test",
            },
            "gui": {
                "run_daemon": True,
                "interval": 3,
                "start_day_time": "1:00",
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
        self.assertTrue(file.is_file())

        try:
            load_storage = FileConfigStorage(file)
            load_config = load_storage.load()

            self.assertEqual("http://save.test", load_config.host)
            self.assertEqual(100, load_config.port)
            self.assertEqual(3, load_config.interval)
            self.assertTrue(load_config.run_daemon)
            self.assertEqual(2, len(load_config.projects))
            self.assertEqual(
                load_config.projects.none_project,
                load_config.projects.projects[1].name
            )
            self.assertIsInstance(
                load_config.projects.projects[0],
                Project
            )
            self.assertIsInstance(
                load_config.projects.projects[0].rules[0],
                Rule
            )
            saved_yaml = yaml.safe_load(file.read_text())
            self.assertEqual(initial_yaml, saved_yaml)
        finally:
            file.unlink()
