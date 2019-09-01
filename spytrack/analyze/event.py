from aw_core import Event as ParentEvent
from .bucket_type import BucketType


class Event(ParentEvent):  # type: ignore
    def __init__(self, event: ParentEvent, bucket_type: BucketType) -> None:
        super().__init__(event.id, event.timestamp, event.duration, event.data)
        self.type = bucket_type

    def stringify_data(self) -> str:
        result = ''
        if 'url' in self.data:
            result += f'url{self.data["url"]}'
        if 'title' in self.data:
            result += f'title{self.data["title"]}'
        if 'app' in self.data:
            result += f'app{self.data["app"]}'

        if len(result) == 0:
            raise Exception

        return result
