from typing import List, Dict
from analyze.matched_event import MatchedEvent


class PieChartData:
    data: Dict[str, int] = {}

    def count_event(self, event: MatchedEvent) -> None:
        if event.project not in self.data:
            self.data[event.project] = 0
        self.data[event.project] += event.event.duration.total_seconds()


def get_pie_chart(matched_events: List[MatchedEvent]) -> PieChartData:
    result = PieChartData()
    for event in matched_events:
        result.count_event(event)
    return result
