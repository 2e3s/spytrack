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
        self.cached_start_time = datetime.now()

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

    def get_cached_events(self, bucket: str, start_time: datetime,
                          end_time: datetime) -> Events:
        if bucket not in self.events_cache \
                or len(self.events_cache[bucket]) == 0:
            events = self.get_events(bucket, start_time, end_time)
        else:
            original_events = self.events_cache[bucket]
            last_event = original_events[0]
            next_start_time = last_event.timestamp.astimezone(tz=None)
            next_events = self.get_events(bucket, next_start_time, end_time)
            next_ids = [event.id for event in reversed(next_events)]
            if last_event.id not in next_ids:
                # no merging required
                events = next_events + original_events
            else:
                last_position = len(next_ids) - next_ids.index(
                    last_event.id) - 1
                original_events[0] = next_events[last_position]
                if last_position == len(next_ids) - 1:
                    events = next_events + original_events[1:]
                else:
                    events = next_events[:last_position] + original_events

        self.events_cache[bucket] = events

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

    def get_cached_bucket_events(self, buckets: List[str],
                                 start_time: datetime, end_time: datetime
                                 ) -> Dict[str, Events]:
        if not self._cached_time_matches(start_time):
            self.events_cache.clear()
            self.cached_start_time = start_time

        events = {}
        for bucket_name in buckets:
            events[bucket_name] = self.get_cached_events(
                bucket_name,
                start_time,
                end_time
            )

        return events

    def _cached_time_matches(self, compared_time: datetime) -> bool:
        cached_time = self.cached_start_time.replace(microsecond=0, second=0)
        compared_time = compared_time.replace(microsecond=0, second=0)

        return cached_time == compared_time
