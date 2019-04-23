import unittest
from . dataset import get_events
from unittest.mock import Mock, MagicMock
from aw_client import ActivityWatchClient
from analyze import Analyzer
from config import Config


class TestAnalyzer(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()

    def test_analyze_empty(self) -> None:
        client_mock: ActivityWatchClient = Mock()
        client_mock.get_buckets = MagicMock()
        client_mock.get_buckets.return_value = {
            'window': {'type': 'currentwindow'},
            'afk': {'type': 'afkstatus'},
            'browser': {'type': 'web.tab.current'},
        }
        client_mock.get_events = MagicMock(side_effect=lambda bucket_id, *args: get_events(bucket_id))

        config: Config = Mock()

        analyzer = Analyzer(config, client_mock)
        events = analyzer.get_points()

        # Application on non-afk
        # [(5, {'app': 'Another2', 'title': 'whatever'}, False),
        #  (5, {'app': 'Another2', 'title': 'whatever'}, True),
        #  (6, {'app': 'Browser', 'title': 'website - Browser'}, False),
        #  (11, {'app': 'Browser', 'title': 'website - Browser'}, True),
        #  (12, {'app': 'Browser', 'title': 'whatever - Browser'}, False),
        #  (13, {'app': 'Browser', 'title': 'whatever - Browser'}, True)]
        # Web tabs matching Browser
        # [(6, {'title': 'nothing2'}, False),
        #  (9, {'title': 'nothing2'}, True),
        #  (10, {'title': 'website'}, False),
        #  (11, {'title': 'website'}, True)]
        # Application on non-afk not-matching browser tabs
        # [(5, {'app': 'Another2', 'title': 'whatever'}, False),
        #  (5, {'app': 'Another2', 'title': 'whatever'}, True),
        #  (6, {'app': 'Browser', 'title': 'website - Browser'}, False),
        #  (6, {'app': 'Browser', 'title': 'website - Browser'}, True),
        #  (9, {'app': 'Browser', 'title': 'website - Browser'}, False),
        #  (10, {'app': 'Browser', 'title': 'website - Browser'}, True)
        #  (12, {'app': 'Browser', 'title': 'website - Browser'}, False),
        #  (12, {'app': 'Browser', 'title': 'website - Browser'}, True)
        check_events = [
            ('nothing2', 6, 3),
            ('website - Browser', 9, 1),
            ('website', 10, 1),
            ('website', 12, 1),
        ]
        self.assertEqual(len(check_events), len(events))
        for i in range(0, len(check_events)):
            check = check_events[i]
            event = events[i]
            self.assertEqual(check[0], event.data['title'])
            self.assertEqual(check[1], event.timestamp.second, event.data['title'])
            self.assertEqual(check[2], event.duration.seconds, event.data['title'])
