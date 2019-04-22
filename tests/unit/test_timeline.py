import unittest
from parameterized import parameterized
from typing import Tuple, List
from aw_core import Event
from . dataset import get_events, get_date
from analyze.timeline import Timeline
from analyze.analyzer import Analyzer


class TestTimeline(unittest.TestCase):
    TimelineResults = List[Tuple[str, int, bool]]  # App title, app timestamp (second), is event end
    TimelineData = List[Tuple[int, int]]  # app/afk: timestamp second, duration in seconds

    # 012345678901234567890
    #     |--------|    app
    #  |-------|        afk
    #
    #  |-------|        app
    #     |--------|    afk
    #
    #  |----------|     app
    #     |-----|       afk
    #
    #     |-----|       app
    #  |----------|     afk
    # 012345678901234567890
    timelines = [
        (
            [(4, 9)],
            [(1, 8)],
            [  # inclusive
                ('Browser', 4, False),
                ('Browser', 9, True),
            ],
            [  # exclusive
                ('Browser', 9, False),
                ('Browser', 13, True),
            ],
        ),
        (
            [(1, 8)],
            [(4, 9)],
            [
                ('Browser', 4, False),
                ('Browser', 9, True),
            ],
            [
                ('Browser', 1, False),
                ('Browser', 4, True),
            ],
        ),
        (
            [(1, 11)],
            [(4, 6)],
            [
                ('Browser', 4, False),
                ('Browser', 10, True),
            ],
            [
                ('Browser', 1, False),
                ('Browser', 4, True),
                ('Browser', 10, False),
                ('Browser', 12, True),
            ],
        ),
        (
            [(4, 6)],
            [(1, 11)],
            [
                ('Browser', 4, False),
                ('Browser', 10, True),
            ],
            [],
        ),
        # #  01234567890123456789
        # #  ---|++-|+++++|+++++- app
        # #  ------|++++++++----- afk
        (
            [(3, 2), (7, 5), (13, 5)],
            [(6, 8)],
            [
                ('Browser', 7, False),
                ('Browser', 12, True),
                ('Browser', 13, False),
                ('Browser', 14, True),
            ],
            [
                ('Browser', 3, False),
                ('Browser', 5, True),
                ('Browser', 14, False),
                ('Browser', 18, True),
            ],
        ),
    ]

    @parameterized.expand(timelines)  # type: ignore
    def test_intersect_simple(
            self,
            app_data: TimelineData,
            afk_data: TimelineData,
            inclusive_results: TimelineResults,
            exclusive_results: TimelineResults
    ) -> None:
        app_events = [Event(
            2,
            get_date(10, 0, data[0]),
            data[1],
            {'app': 'Browser', 'title': 'website - Browser'}
        ) for data in app_data]
        afk_events = [Event(2, get_date(10, 0, data[0]), data[1], {'status': 'not-afk'}) for data in afk_data]
        app_timeline = Timeline.create_from_bucket_events('currentwindow', app_events)
        afk_timeline = Timeline.create_from_bucket_events('afkstatus', afk_events)
        app_timeline.intersect(afk_timeline, Analyzer.app_afk_timeline_condition)
        self.assert_timeline(app_timeline, inclusive_results)

        app_timeline = Timeline.create_from_bucket_events('currentwindow', app_events)
        afk_timeline = Timeline.create_from_bucket_events('afkstatus', afk_events)
        app_timeline.intersect(afk_timeline, Analyzer.app_afk_timeline_condition, False)
        self.assert_timeline(app_timeline, exclusive_results)

    def test_intersect(self) -> None:
        app_timeline = Timeline.create_from_bucket_events('currentwindow', get_events('window'))
        afk_timeline = Timeline.create_from_bucket_events('afkstatus', get_events('afk'))

        app_timeline.intersect(afk_timeline, Analyzer.app_afk_timeline_condition)
        self.assert_timeline(app_timeline, [
            ('Browser', 6, False),
            ('Browser', 11, True),
            ('Browser', 12, False),
            ('Browser', 13, True),
        ])

    def assert_timeline(self, timeline: Timeline, check_points: TimelineResults) -> None:
        self.assertEqual(len(check_points), len(timeline._points))
        for i in range(0, len(check_points)):
            check = check_points[i]
            point = timeline._points[i]
            self.assertEqual(check[0], point.get_event_data()['app'])
            self.assertEqual(check[1], point.get_timestamp().second, point.get_event_data()['app'])
            self.assertEqual(check[2], point.is_end(), point.get_event_data()['app'])

    def test_get_events(self) -> None:
        original_events = get_events('window')
        app_timeline = Timeline.create_from_bucket_events('currentwindow', original_events)
        self.assertEqual(8, len(app_timeline.get_points()))
        generated_events = app_timeline.get_events()
        self.assertEqual(4, len(generated_events))
        for i in range(len(original_events)):
            original_event = original_events[i]
            generated_event = generated_events[i]
            self.assertEqual(original_event.timestamp, generated_event.timestamp)
            self.assertEqual(original_event.data, generated_event.data)
