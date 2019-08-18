from _datetime import datetime
from typing import Dict, List, Any, Callable
from analyze.bucket_type import BucketType
from analyze.cached_event_repository import CachedEventRepository
from analyze.event_repository import EventRepository
from analyze.events_analyzer import EventsAnalyzer
from config.config import Config
from .event import Event
from .matched_event import MatchedEvent
from .bucket_point import BucketPoint

ClientBuckets = Dict[str, Dict[str, Any]]
Events = List[Event]
BucketName = str
Buckets = Dict[BucketName, BucketType]
BucketPoints = List[BucketPoint]
BucketPointCondition = Callable[[BucketPoint], bool]


class AnalyzerFacade:
    browser_buckets_cache: Dict[BucketName, str] = {}

    def __init__(self, event_repository: EventRepository,
                 config: Config) -> None:
        self.config = config
        self.event_repository = event_repository
        self.cached_event_repository = CachedEventRepository(event_repository)
        self.analyzer = EventsAnalyzer()

    def analyze(self, start_date: datetime, end_date: datetime,
                is_current: bool) -> List[MatchedEvent]:
        buckets = self.event_repository.fetch_buckets()

        if is_current:
            events = self.cached_event_repository.get_bucket_events(
                list(buckets.keys()),
                start_date,
                end_date
            )
        else:
            events = self.event_repository.get_bucket_events(
                list(buckets.keys()),
                start_date,
                end_date
            )

        analyzed_events = self.analyzer.analyze_events(buckets, events)
        return self.analyzer.match(analyzed_events, self.config.projects)
