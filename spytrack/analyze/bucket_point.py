import datetime
from typing import Dict
from aw_core import Event
from .bucket_type import BucketType


class BucketPoint:
    def __init__(self,
                 bucket_type: BucketType,
                 timestamp: datetime.datetime,
                 event: Event,
                 is_end: bool
                 ) -> None:
        self._bucket_type = bucket_type
        self._is_end = is_end
        self.event = event
        self.timestamp = timestamp

    @property
    def event_data(self) -> Dict[str, str]:
        return self.event.data  # type: ignore

    @property
    def event_type(self) -> BucketType:
        return self._bucket_type

    def is_end(self) -> bool:
        return self._is_end

    def __lt__(self, other: 'BucketPoint') -> bool:
        if self.timestamp == other.timestamp:
            return self.event_type == BucketType.AFK \
                   and other.event_type != BucketType.AFK
        return self.timestamp < other.timestamp
