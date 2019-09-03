import yaml
import argparse
from pathlib import Path
from config import Config, ConfigDict
import appdirs

default_config = """
daemon:
  host: http://localhost
  port: 9011
gui:
  interval: 5
  projects:
  - name: coding
    rules:
    - app: pycharm
      type: app
    - title: Qt Designer
      type: app
    - type: web
      url: .*qt.io.*
    - type: web
      url: python
    - title: python
      type: web
    - title: pyqt
      type: web
    - app: code
      title: .*Visual Studio Code
      type: app
  run_daemon: true
  start_day_time: '5:00'
"""


def get_config_file() -> Path:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config")
    args, _ = parser.parse_known_args()

    if args.config is None:
        config_dir = appdirs.user_config_dir('spytrack')
        return Path(config_dir).joinpath("config.yaml")
    else:
        return Path(args.config)


class ConfigParseException(BaseException):
    pass


class FileConfigStorage:
    def __init__(self, file: Path) -> None:
        self.file = file

    def load(self) -> Config:
        try:
            if not self.file.exists():
                self.file.parent.mkdir(parents=True, exist_ok=True)
                values = yaml.safe_load(default_config)
                self._persist(values)
            else:
                values = yaml.safe_load(self.file.read_text())
            return Config(values)
        except yaml.YAMLError:
            raise ConfigParseException

    def save(self, config: Config) -> None:
        dump = {
            "daemon": {
                "host": config.host,
                "port": config.port,
            },
            "gui": {
                "run_daemon": config.run_daemon,
                "interval": config.interval,
                "start_day_time": config.start_day_time,
                "projects": config.projects.to_json()}
        }
        self._persist(dump)

    def _persist(self, dump: ConfigDict) -> None:
        with self.file.open('w') as outfile:
            yaml.dump(dump, outfile, default_flow_style=False)
