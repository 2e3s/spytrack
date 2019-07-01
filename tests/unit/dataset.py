import datetime
from typing import List
from aw_core import Event


def get_date(seconds: int) -> datetime.datetime:
    return datetime.datetime(2010, 10, 1, 10, 0, seconds,
                             tzinfo=datetime.timezone.utc)


# See "MergeEvents.drawio" for better understanding
def get_events(bucket_id: str) -> List[Event]:
    if bucket_id == 'window':
        return [
            Event(1, get_date(1), 1, {'app': 'Another', 'title': 'whatever'}),
            Event(2, get_date(3), 2, {'app': 'Another2', 'title': 'whatever'}),
            Event(3, get_date(6), 5, {
                'app': 'Browser',
                'title': 'website - Browser',
            }),
            Event(4, get_date(12), 6, {
                'app': 'Browser',
                'title': 'whatever - Browser',
            }),
        ]
    elif bucket_id == 'afk':
        return [
            Event(1, get_date(1), 3, {'status': 'afk'}),
            Event(2, get_date(5), 8, {'status': 'not-afk'}),
        ]
    elif bucket_id == 'browser':
        return [
            Event(1, get_date(1), 3, {'title': 'nothing1'}),
            Event(2, get_date(5), 4, {'title': 'nothing2'}),
            Event(3, get_date(10), 5, {'title': 'website'}),
            Event(4, get_date(16), 2, {'title': 'nothing3'}),
        ]
    else:
        return []
