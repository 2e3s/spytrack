from aw_core import Event as ParentEvent
from .bucket_type import BucketType


class Event(ParentEvent):  # type: ignore
    type: BucketType

    def __init__(self, event: ParentEvent, bucket_type: BucketType) -> None:
        super().__init__(event.id, event.timestamp, event.duration, event.data)
        self.type = bucket_type
