from enum import Enum, auto


class BucketType(Enum):
    AFK = auto()
    APP = auto()
    WEB = auto()

    @staticmethod
    def create(bucket_type: str) -> 'BucketType':
        if bucket_type == 'afkstatus':
            return BucketType.AFK
        elif bucket_type == 'currentwindow':
            return BucketType.APP
        elif bucket_type == 'web.tab.current':
            return BucketType.WEB
        else:
            raise RuntimeError
