import unittest
from datetime import datetime
from aw_core import Event
from typing import List, Tuple

from analyze.cached_event_repository import CachedEventRepository
from analyze.event_repository import EventRepository
from .dataset import get_date
from unittest.mock import Mock, MagicMock
from aw_client import ActivityWatchClient


class TestEventRepository(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.client_mock: ActivityWatchClient = Mock()
        self.client_mock.get_buckets = MagicMock()
        self.client_mock.get_buckets.return_value = {
            'window': {'type': 'currentwindow'},
            'afk': {'type': 'afkstatus'},
            'browser': {'type': 'web.tab.current'},
        }

        wrapped_repository = EventRepository(self.client_mock)
        self.repository = CachedEventRepository(wrapped_repository)

    def test_get_cached_events(self) -> None:
        mock_events1 = [
            Event(4, get_date(16), 2, {'app': 'x', 'title': 'nothing3'}),
            Event(3, get_date(10), 5, {'app': 'x', 'title': 'website'}),
            Event(2, get_date(5), 4, {'app': 'x', 'title': 'nothing2'}),
            Event(1, get_date(1), 3, {'app': 'x', 'title': 'nothing1'}),
        ]
        mock_events2 = [
            Event(6, get_date(27), 2, {'app': 'x', 'title': 'nothing3'}),
            Event(5, get_date(21), 5, {'app': 'x', 'title': 'website'}),
            Event(4, get_date(16), 4, {'app': 'x', 'title': 'nothing3'}),
            Event(3, get_date(10), 5, {'app': 'x', 'title': 'website'}),
        ]
        self.client_mock.get_events = MagicMock(
            side_effect=[mock_events1, mock_events2]
        )

        time = datetime.now()
        events = self.repository.get_events('window', time, time)
        self.check_events([
            ('x', 'nothing3', 16, 2),
            ('x', 'website', 10, 5),
            ('x', 'nothing2', 5, 4),
            ('x', 'nothing1', 1, 3),
        ], events)

        events = self.repository.get_events('window', time, time)
        self.check_events([
            ('x', 'nothing3', 27, 2),
            ('x', 'website', 21, 5),
            ('x', 'nothing3', 16, 4),
            ('x', 'website', 10, 5),
            ('x', 'nothing2', 5, 4),
            ('x', 'nothing1', 1, 3),
        ], events)

    def check_events(self, checked_events: List[Tuple[str, str, int, int]],
                     events: List[Event]) -> None:
        self.assertEqual(len(checked_events), len(events))
        for i in range(0, len(checked_events)):
            check = checked_events[i]
            event = events[i]
            self.assertEqual(check[0], event.data['app'])
            self.assertEqual(check[1], event.data['title'])
            self.assertEqual(check[2], event.timestamp.second)
            self.assertEqual(check[3], event.duration.total_seconds())
