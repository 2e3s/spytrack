import unittest
from datetime import datetime, timezone

from analyze.bucket_type import BucketType
from analyze.event import Event
from aw_core import Event as ParentEvent


class TestEvent(unittest.TestCase):
    def test_stringify_data(self) -> None:
        current_time = datetime.now().astimezone(timezone.utc)
        event = Event(ParentEvent(1, current_time, 2, {'url': '123'}),
                      BucketType.WEB)
        self.assertEqual('url123', event.stringify_data())

    def test_wrong_data(self) -> None:
        current_time = datetime.now().astimezone(timezone.utc)
        event = Event(ParentEvent(1, current_time, 2, {'test': '123'}),
                      BucketType.WEB)
        self.assertRaises(Exception, event.stringify_data)
