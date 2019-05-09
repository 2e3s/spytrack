import uuid
from typing import Dict, Any, List


class Project:
    @staticmethod
    def reinstate(config_project: Any) -> 'Project':
        return Project(config_project['name'], config_project['rules'])

    def __init__(self, name: str, rules: List[Dict[str, str]]) -> None:
        self.rules = [{**rule, 'id': str(uuid.uuid4())} for rule in rules]
        self.name = name

    def to_json(self) -> Any:
        return {
            'name': self.name,
            'rules': [{field: value for field, value in rule.items() if field != 'id'} for rule in self.rules]
        }


class Config:
    config: Dict[str, Any]
    projects: List[Project]
    none_project: str

    def __init__(self, values: Dict[str, Any]) -> None:
        self.port = int(values['daemon']['port'])
        self.host = str(values['daemon']['host'])
        self.interval = int(values['gui']['interval'])
        self.run_daemon = bool(values['gui']['run_daemon'])
        self.start_date_time = str(values['gui']['start_date_time'])
        self.none_project = str(uuid.uuid4())
        self.projects = [Project.reinstate(project) for project in values['gui']['projects']]
        self.projects.append(Project(self.none_project, []))

    def get_full_address(self) -> str:
        return '%s:%s' % (self.get_host(), self.get_port())

    def get_interval(self) -> int:
        return self.interval

    def get_host(self) -> str:
        return self.host

    def get_port(self) -> int:
        return self.port

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
