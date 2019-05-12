import uuid
from typing import Dict, Any, List, Iterator


class Rule:
    APP = 'app'
    WEB = 'web'

    def __init__(self, values: Dict[str, str]) -> None:
        if 'id' in values:
            self.id = values['id']
            del values['id']
        else:
            self.id = str(uuid.uuid4())
        self.values = values

    def to_json(self) -> Any:
        return self.values

    def __iter__(self) -> Iterator[Dict[str, str]]:
        return iter(self.to_json())

    def __getitem__(self, item: str) -> str:
        return self.values[item]

    def __contains__(self, item: str) -> bool:
        return item in self.values

    def __len__(self) -> int:
        return len(self.values)

    def is_web(self) -> bool:
        return self.values['type'] == Rule.WEB

    def is_app(self) -> bool:
        return self.values['type'] == Rule.APP


class Project:
    @staticmethod
    def reinstate(config_project: Any) -> 'Project':
        return Project(config_project['name'], [Rule(rule) for rule in config_project['rules']])

    @staticmethod
    def create_empty(none_project: str) -> 'Project':
        return Project(none_project, [])

    def __init__(self, name: str, rules: List[Rule]) -> None:
        self.rules = rules
        self.name = name

    def to_json(self) -> Any:
        return {
            'name': self.name,
            'rules': [rule.to_json() for rule in self.rules]
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
        self.projects.append(Project.create_empty(self.none_project))

    def get_full_address(self) -> str:
        return '%s:%s' % (self.host, self.port)
