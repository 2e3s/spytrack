from typing import Dict, List, Any, Callable
from aw_client import ActivityWatchClient
from aw_core import Event
from .bucket_point import BucketPoint
from .timeline import Timeline
from config import Config


ClientBuckets = Dict[str, Dict[str, Any]]
Events = List[Event]
BucketPoints = List[BucketPoint]


class Analyzer:
    def __init__(self, config: Config, client: ActivityWatchClient = None) -> None:
        self.config = config
        if client is None:
            self.client = ActivityWatchClient("gui", testing=False)
        else:
            self.client = client

    def get_points(self) -> BucketPoints:
        buckets = {key: value for key, value in self.client.get_buckets().items() if value['type'] in [
            'currentwindow',
            'afkstatus',
            'web.tab.current',
        ]}

        timelines = {}
        for bucket in buckets:
            events = self.client.get_events(bucket, 1000)
            events = [event for event in events if event.duration.total_seconds() > 0]
            timelines[bucket] = Timeline.create_from_bucket_events(buckets[bucket]['type'], events)

        browser_buckets = [key for key, value in buckets.items() if value['type'] == 'web.tab.current']
        app_bucket = [key for key, value in buckets.items() if value['type'] == 'currentwindow'][0]
        afk_bucket = [key for key, value in buckets.items() if value['type'] == 'afkstatus'][0]
        browser_matches = Analyzer._match_browser_buckets(app_bucket, browser_buckets, timelines)
        for bucket in browser_buckets:
            if bucket not in browser_matches:
                del timelines[bucket]

        # leave only windows non-afk events
        timelines[app_bucket].intersect(
            timelines[afk_bucket],
            Analyzer.app_afk_timeline_condition
        )
        all_points: BucketPoints = []
        # leave only web-events belonging to the corresponding app (already non-afk)
        for web_bucket_name, app_name in browser_matches.items():
            timelines[web_bucket_name].intersect(
                timelines[app_bucket],
                self.app_browser_timeline_condition(app_name)
            )
            timelines[app_bucket].intersect(
                timelines[web_bucket_name],
                lambda _: True,
                False
            )
            all_points += timelines[web_bucket_name].get_points()

        all_points += timelines[app_bucket].get_points()
        all_points.sort()

        return all_points

    @staticmethod
    def app_afk_timeline_condition(afk_event: BucketPoint) -> bool:
        return bool(afk_event.get_event_data()['status'] == 'not-afk')

    @staticmethod
    def app_browser_timeline_condition(app_name: str) -> Callable[[BucketPoint], bool]:
        return lambda app_event: bool(app_event.get_event_data()['app'] == app_name)

    @staticmethod
    def _match_browser_buckets(
            app_bucket: str,
            browser_buckets: List[str],
            timelines: Dict[str, Timeline]
    ) -> Dict[str, str]:
        app_timeline = timelines[app_bucket]
        matches = {}
        for browser_bucket in browser_buckets:
            browser_timeline = timelines[browser_bucket]
            match_app = browser_timeline.get_browser_app(app_timeline)

            if match_app is not None:
                matches[browser_bucket] = match_app
        return matches
