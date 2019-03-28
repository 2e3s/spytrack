import unittest
from tests.integration import get_current_directory
from pathlib import Path
from config.config_storage import FileConfigStorage, Config


class TestFileConfigStorage(unittest.TestCase):
    def test_save_load(self) -> None:
        filename = '%s/test_save.config.yaml' % get_current_directory()
        save_storage = FileConfigStorage(filename)
        saved_config = Config({
            "daemon": {
                "port": 100,
                "host": "http://save.test",
                "interval": 3,
                "database": "save.test.db",
            },
            "gui": {
                "run_daemon": True
            },
        })
        save_storage.save(saved_config)
        file = Path(filename)
        self.assertTrue(file.is_file())

        load_storage = FileConfigStorage(filename)
        load_config = load_storage.load()
        self.assertEqual("http://save.test", load_config.get_host())
        self.assertEqual(100, load_config.get_port())
        self.assertEqual(3, load_config.get_interval())
        self.assertTrue(load_config.is_run_server())

        file.unlink()
