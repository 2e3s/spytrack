from typing import Union
from .event import Event

Project = Union[str, None]


class MatchedEvent:
    project: Project
    event: Event

    def __init__(self, project: Project, event: Event) -> None:
        self.event = event
        self.project = project
