from datetime import datetime, timezone
from typing import Dict, Any, List
from analyze.bucket_type import BucketType
from .event import Event
from aw_client import ActivityWatchClient


Events = List[Event]


class EventRepository:
    BUCKET_TYPE_WINDOW = 'currentwindow'
    BUCKET_TYPE_AFK = 'afkstatus'
    BUCKET_TYPE_WEB = 'web.tab.current'

    def __init__(self, client: ActivityWatchClient) -> None:
        self.client = client
        self.events_cache: Dict[str, Events] = {}

    def fetch_buckets(self) -> Dict[str, BucketType]:
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

    def get_buckets(self) -> List[str]:
        return list(self.fetch_buckets().keys())

    def get_cached_events(self, bucket: str, start_time: datetime,
                          end_time: datetime) -> Events:
        if not self._has_cache(bucket):
            events = self.get_events(bucket, start_time, end_time)
        else:
            original_events = self._get_cache(bucket)
            last_event = original_events[-1]
            next_start_time = last_event.timestamp
            next_events = self.get_events(bucket, next_start_time, end_time)
            next_ids = [event.id for event in next_events]
            if last_event.id not in next_ids:
                # no merging required
                events = original_events + next_events
            else:
                first_position = next_ids.index(last_event.id)
                original_events[-1] = next_events[first_position]
                events = original_events + next_events[first_position + 1:]

        self._set_cache(bucket, events)

        return events

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

    def _has_cache(self, bucket: str) -> bool:
        return bucket in self.events_cache \
               and len(self.events_cache[bucket]) > 0

    def _set_cache(self, bucket: str, events: Events) -> None:
        self.events_cache[bucket] = events

    def _get_cache(self, bucket: str) -> Events:
        return self.events_cache[bucket]
