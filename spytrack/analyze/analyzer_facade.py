import re
from typing import Dict, List, Any, Callable
from analyze.bucket_type import BucketType
from .event import Event
from .matched_event import MatchedEvent
from .bucket_point import BucketPoint
from .timeline import Timeline
from config import Project, Rule

ClientBuckets = Dict[str, Dict[str, Any]]
Events = List[Event]
BucketName = str
Buckets = Dict[BucketName, BucketType]
BucketPoints = List[BucketPoint]
BucketPointCondition = Callable[[BucketPoint], bool]


class AnalyzerFacade:
    def analyze_events(self, buckets: Buckets,
                       bucket_events: Dict[BucketName, Events]) -> Events:
        timelines = {}
        for bucket_name, bucket_type in buckets.items():
            events = bucket_events[bucket_name]
            timelines[bucket_name] = Timeline.create_from_bucket_events(
                bucket_type,
                events
            )

        browser_buckets = [bucket
                           for bucket, value
                           in buckets.items()
                           if value == BucketType.WEB]
        app_buckets = [bucket
                       for bucket, value
                       in buckets.items()
                       if value == BucketType.APP]
        afk_buckets = [bucket
                       for bucket, value
                       in buckets.items()
                       if value == BucketType.AFK]

        if len(app_buckets) == 0 or len(afk_buckets) == 0:
            return []
        app_bucket = app_buckets[0]
        afk_bucket = afk_buckets[0]
        browser_matches = self._match_browser_buckets(
            app_bucket,
            browser_buckets,
            timelines
        )
        for bucket_name in browser_buckets:
            if bucket_name not in browser_matches:
                del timelines[bucket_name]

        # leave only windows non-afk events
        timelines[app_bucket].intersect(
            timelines[afk_bucket],
            self.app_afk_timeline_condition
        )
        all_events: Events = []
        # leave only web-events belonging to the corresponding app
        # (already non-afk)
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
            all_events += timelines[web_bucket_name].get_events()

        all_events += timelines[app_bucket].get_events()
        all_events.sort()

        return all_events

    def match(self, events: Events, projects: List[Project],
              none_project: str) -> List[MatchedEvent]:
        matched_events = []
        for event in events:
            match_result = False
            for project in projects:
                for rule in project.rules:
                    match_result = self._match_event(event, rule)
                    if match_result:
                        matched_event = MatchedEvent(project.name, rule.id,
                                                     event)
                        matched_events.append(matched_event)
                        break
                if match_result:
                    break
            if not match_result:
                matched_event = MatchedEvent(none_project, none_project,
                                             event)
                matched_events.append(matched_event)

        return matched_events

    def _match_event(self, event: Event, definition: Rule) -> bool:
        if 'url' in definition and 'url' in event.data:
            return re.search(definition['url'], event.data['url'],
                             flags=re.IGNORECASE) is not None
        if 'title' in definition and 'title' in event.data:
            return re.search(definition['title'], event.data['title'],
                             flags=re.IGNORECASE) is not None
        if 'app' in definition and 'app' in event.data:
            return re.search(definition['app'], event.data['app'],
                             flags=re.IGNORECASE) is not None
        return False

    @staticmethod
    def app_afk_timeline_condition(afk_event: BucketPoint) -> bool:
        return bool(afk_event.event_data['status'] == 'not-afk')

    @staticmethod
    def app_browser_timeline_condition(app_name: str) -> BucketPointCondition:
        return lambda app_event: bool(app_event.event_data['app'] == app_name)

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
