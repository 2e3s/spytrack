import unittest

from analyze.bucket_type import BucketType
from analyze.events_analyzer import EventsAnalyzer
from config.config import Projects
from . dataset import get_events
from config import Project, Rule


class TestAnalyzer(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()

    def test_analyze_events(self) -> None:
        analyzer = EventsAnalyzer()
        events = analyzer.analyze_events(
            {
                'window': BucketType.APP,
                'afk': BucketType.AFK,
                'browser': BucketType.WEB,
            },
            {
                'window': get_events('window'),
                'afk': get_events('afk'),
                'browser': get_events('browser'),
            },
        )

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
            self.assertEqual(check[0],
                             event.data['title'])
            self.assertEqual(check[1],
                             event.timestamp.second, event.data['title'])
            self.assertEqual(check[2],
                             event.duration.seconds, event.data['title'])

        matched_events = analyzer.match(events, Projects([
            Project('test1',
                    [Rule({'id': '1', 'type': 'app', 'app': 'Browser'})])
        ], 'none'))
        check_matched_events = [
            ('nothing2', None),
            ('website - Browser', 'test1'),
            ('website', None),
            ('website', None),
        ]
        for i in range(0, len(check_matched_events)):
            matched_check = check_matched_events[i]
            matched_event = matched_events[i]
            self.assertEqual(matched_check[0],
                             matched_event.event.data['title'])
