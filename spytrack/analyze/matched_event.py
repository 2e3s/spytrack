from .event import Event


class MatchedEvent:
    project: str
    rule_id: str
    event: Event

    def __init__(self, project: str, rule_id: str, event: Event) -> None:
        self.rule_id = rule_id
        self.event = event
        self.project = project
