import yaml
import argparse
from pathlib import Path
from config import Config


def get_config_filename() -> str:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config")
    args = parser.parse_args()

    if args.config is None:
        raise ConfigParseException

    return str(args.config)


class ConfigParseException(BaseException):
    pass


class FileConfigStorage:
    def __init__(self, filename: str) -> None:
        self.filename = filename

    def load(self) -> Config:
        try:
            values = yaml.safe_load(Path(self.filename).read_text())
            return Config(values)
        except yaml.YAMLError:
            raise ConfigParseException

    def save(self, config: Config) -> None:
        dump = {
            "daemon": {
                "host": config.get_host(),
                "port": config.get_port(),
            },
            "gui": {
                "run_daemon": config.is_run_server(),
                "interval": config.get_interval(),
                "projects": [project.to_json() for project in config.projects if project.name != config.none_project]
            }
        }
        with open(self.filename, 'w') as outfile:
            yaml.dump(dump, outfile, default_flow_style=False)
