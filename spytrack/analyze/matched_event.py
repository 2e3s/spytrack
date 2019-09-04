from .event import Event


class MatchedEvent(Event):
    project: str
    rule_id: str

    def __init__(self, project: str, rule_id: str, event: Event) -> None:
        super().__init__(event, event.type)
        self.rule_id = rule_id
        self.project = project
