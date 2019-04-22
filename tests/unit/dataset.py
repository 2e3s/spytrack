import datetime
from typing import List
from aw_core import Event


def get_date(hours: int, minutes: int, seconds: int) -> datetime.datetime:
    return datetime.datetime(2010, 10, 1, hours, minutes, seconds, tzinfo=datetime.timezone.utc)


#  | start: 10:00:00
#  12345678901234567890
#  |-- |++++++++        afk: 7-15
#  |-|--|+++++|------   window: Another 1-2, Another2 3-5, Browser 6-11, Browser 12-18
#  |---|----|+++++|--   browser: nothing1 1-4, nothing2 5-9, website 10-15, nothing 16-18
#      ||+++++|-        window/afk: Another2 5-5, Browser 6-11, Browser 12-13
#      ||---|+|+        browser/window/afk: Another2 5-5, nothing2 6-9, website 10-11, website 12-13
#  12345678901234567890
def get_events(bucket_id: str) -> List[Event]:
    if bucket_id == 'window':
        return [
            Event(1, get_date(10, 0, 1), 1, {'app': 'Another', 'title': 'whatever'}),
            Event(2, get_date(10, 0, 3), 2, {'app': 'Another2', 'title': 'whatever'}),
            Event(3, get_date(10, 0, 6), 5, {'app': 'Browser', 'title': 'website - Browser'}),
            Event(4, get_date(10, 0, 12), 6, {'app': 'Browser', 'title': 'whatever - Browser'}),
        ]
    elif bucket_id == 'afk':
        return [
            Event(1, get_date(10, 0, 1), 3, {'status': 'afk'}),
            Event(2, get_date(10, 0, 5), 8, {'status': 'not-afk'}),
        ]
    elif bucket_id == 'browser':
        return [
            Event(1, get_date(10, 0, 1), 3, {'title': 'nothing1'}),
            Event(2, get_date(10, 0, 5), 4, {'title': 'nothing2'}),
            Event(3, get_date(10, 0, 10), 5, {'title': 'website'}),
            Event(4, get_date(10, 0, 16), 2, {'title': 'nothing3'}),
        ]
    else:
        return []