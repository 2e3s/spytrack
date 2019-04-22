import datetime
from typing import Dict
from aw_core import Event
from .bucket_type import BucketType


class BucketPoint:
    def __init__(self, bucket_type: BucketType, timestamp: datetime.datetime, event: Event, is_end: bool) -> None:
        self._bucket_type = bucket_type
        self._is_end = is_end
        self._event = event
        self._timestamp = timestamp

    def get_timestamp(self) -> datetime.datetime:
        return self._timestamp

    def get_event_data(self) -> Dict[str, str]:
        return self._event.data  # type: ignore

    def get_event_type(self) -> BucketType:
        return self._bucket_type

    def get_event(self) -> Event:
        return self._event

    def is_end(self) -> bool:
        return self._is_end

    def __lt__(self, other: 'BucketPoint') -> bool:
        if self.get_timestamp() == other.get_timestamp():
            return self.get_event_type() == BucketType.AFK and other.get_event_type() != BucketType.AFK
        return self.get_timestamp() < other.get_timestamp()
