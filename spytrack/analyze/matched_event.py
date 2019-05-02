from .event import Event


class MatchedEvent:
    project: str
    event: Event

    def __init__(self, project: str, event: Event) -> None:
        self.event = event
        self.project = project
