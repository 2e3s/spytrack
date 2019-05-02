import uuid
from typing import Dict, Any, List

Projects = Dict[str, List[Dict[str, str]]]


class Config:
    config: Dict[str, Any]
    projects: Projects
    none_project: str

    def __init__(self, values: Dict[str, Any]) -> None:
        self.port = int(values['daemon']['port'])
        self.host = str(values['daemon']['host'])
        self.interval = int(values['gui']['interval'])
        self.run_daemon = bool(values['gui']['run_daemon'])
        self.none_project = str(uuid.uuid4())
        self.projects = {
            "work": [
                {'type': 'web', 'url': '.*rebilly.*'},
                {'type': 'app', 'app': 'phpstorm'},
            ],
            "coding": [
                {'type': 'app', 'app': 'pycharm'},
            ],
            self.none_project: []
        }

    def get_full_address(self) -> str:
        return '%s:%s' % (self.get_host(), self.get_port())

    def get_interval(self) -> int:
        return self.interval

    def get_host(self) -> str:
        return self.host

    def get_port(self) -> int:
        return self.port

    def get_projects(self) -> Projects:
        return self.projects

    def is_run_server(self) -> bool:
        return self.run_daemon

    def set_interval(self, interval: int) -> None:
        self.interval = interval

    def set_port(self, port: int) -> None:
        self.port = port

    def set_host(self, host: str) -> None:
        self.host = host

    def set_run_server(self, run_daemon: bool) -> None:
        self.run_daemon = run_daemon
