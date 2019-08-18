from datetime import datetime, timezone
from typing import Dict, Any, List
from analyze.bucket_type import BucketType
from .event import Event
from aw_client import ActivityWatchClient


Events = List[Event]
Buckets = Dict[str, BucketType]


class EventRepository:
    BUCKET_TYPE_WINDOW = 'currentwindow'
    BUCKET_TYPE_AFK = 'afkstatus'
    BUCKET_TYPE_WEB = 'web.tab.current'

    def __init__(self, client: ActivityWatchClient) -> None:
        self.client = client

    def fetch_buckets(self) -> Buckets:
        return {
            key: self._get_bucket_type(value)
            for key, value
            in self.client.get_buckets().items()
            if value['type'] in [
                EventRepository.BUCKET_TYPE_WINDOW,
                EventRepository.BUCKET_TYPE_AFK,
                EventRepository.BUCKET_TYPE_WEB,
            ]
        }

    def _get_bucket_type(self, data: Any) -> BucketType:
        if data['type'] == EventRepository.BUCKET_TYPE_AFK:
            return BucketType.AFK
        elif data['type'] == EventRepository.BUCKET_TYPE_WINDOW:
            return BucketType.APP
        elif data['type'] == EventRepository.BUCKET_TYPE_WEB:
            return BucketType.WEB
        else:
            raise RuntimeError

    def get_events(self, bucket: str, start_date: datetime,
                   end_date: datetime) -> Events:
        events = self.client.get_events(bucket, -1,
                                        start_date.astimezone(timezone.utc),
                                        end_date.astimezone(timezone.utc))
        bucket_type = self.fetch_buckets()[bucket]
        return [Event(event, bucket_type)
                for event
                in events
                if event.duration.total_seconds() > 0]

    def get_bucket_events(self, buckets: List[str], start_date: datetime,
                          end_date: datetime) -> Dict[str, Events]:
        events = {}
        for bucket_name in buckets:
            events[bucket_name] = self.get_events(
                bucket_name,
                start_date,
                end_date
            )

        return events
