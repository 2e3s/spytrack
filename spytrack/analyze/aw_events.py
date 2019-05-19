from datetime import datetime, timezone
from typing import Dict, Any, List
from analyze.bucket_type import BucketType
from .event import Event
from aw_client import ActivityWatchClient


class AWEvents:
    BUCKET_TYPE_WINDOW = 'currentwindow'
    BUCKET_TYPE_AFK = 'afkstatus'
    BUCKET_TYPE_WEB = 'web.tab.current'

    def __init__(self, client: ActivityWatchClient) -> None:
        self.client = client

    def fetch_buckets(self) -> Dict[str, BucketType]:
        return {
            key: self._get_bucket_type(value)
            for key, value
            in self.client.get_buckets().items()
            if value['type'] in [
                AWEvents.BUCKET_TYPE_WINDOW,
                AWEvents.BUCKET_TYPE_AFK,
                AWEvents.BUCKET_TYPE_WEB,
            ]
        }

    def _get_bucket_type(self, data: Any) -> BucketType:
        if data['type'] == AWEvents.BUCKET_TYPE_AFK:
            return BucketType.AFK
        elif data['type'] == AWEvents.BUCKET_TYPE_WINDOW:
            return BucketType.APP
        elif data['type'] == AWEvents.BUCKET_TYPE_WEB:
            return BucketType.WEB
        else:
            raise RuntimeError

    def get_buckets(self) -> List[str]:
        return list(self.fetch_buckets().keys())

    def get_buckets_by_type(self, bucket_type: BucketType) -> List[str]:
        return [key
                for key, value
                in self.fetch_buckets().items()
                if value == bucket_type]

    def get_cached_events(self,
                          bucket: str,
                          start_date: datetime,
                          end_date: datetime
                          ) -> List[Event]:
        return self.get_events(bucket, start_date, end_date)

    def get_events(self,
                   bucket: str,
                   start_date: datetime,
                   end_date: datetime
                   ) -> List[Event]:
        events = self.client.get_events(
            bucket,
            -1,
            start_date.astimezone(timezone.utc),
            end_date.astimezone(timezone.utc)
        )
        bucket_type = self.fetch_buckets()[bucket]
        return [Event(event, bucket_type)
                for event
                in events
                if event.duration.total_seconds() > 0]
