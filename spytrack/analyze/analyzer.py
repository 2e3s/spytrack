import datetime
from typing import Dict, List, Union, Any, Optional, Callable
from aw_client import ActivityWatchClient
from aw_core import Event
from config import Config
from enum import Enum, auto


ClientBuckets = Dict[str, Dict[str, Any]]
Events = List[Event]


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


class BucketEvent:
    @staticmethod
    def create(bucket_type: str, event: Event) -> 'BucketEvent':
        return BucketEvent(BucketType.create(bucket_type), event)

    def __init__(self, bucket_type: BucketType, event: Event) -> None:
        self._event = event
        self._bucket_type = bucket_type

    def get_event(self) -> Event:
        return self._event

    def get_bucket_type(self) -> BucketType:
        return self._bucket_type

    def get_timestamp(self) -> datetime.datetime:
        return self._event.timestamp  # type: ignore


class BucketPoint:
    def __init__(self, bucket_type: BucketType, timestamp: datetime.datetime, event: Event, is_end: bool) -> None:
        self._bucket_type = bucket_type
        self._is_end = is_end
        self._event = event
        self._timestamp = timestamp

    def get_timestamp(self) -> datetime.datetime:
        return self._timestamp

    def get_event_data(self) -> Dict[str, str]:
        return self._event.data  # type: ignore

    def get_event_type(self) -> BucketType:
        return self._bucket_type

    def get_event(self) -> Event:
        return self._event

    def is_end(self) -> bool:
        return self._is_end

    def __lt__(self, other: 'BucketPoint') -> bool:
        if self.get_timestamp() == other.get_timestamp():
            return self.get_event_type() == BucketType.AFK and other.get_event_type() != BucketType.AFK
        return self.get_timestamp() < other.get_timestamp()


BucketPoints = List[BucketPoint]


class Timeline:
    CutCondition = Callable[[BucketPoint], bool]

    @staticmethod
    def create_from_bucket_events(bucket_type_str: str, events: Events) -> 'Timeline':
        all_points = []
        bucket_type = BucketType.create(bucket_type_str)
        for event in events:
            all_points.append(BucketPoint(bucket_type, event.timestamp, event, False))
            all_points.append(BucketPoint(
                bucket_type,
                event.timestamp + event.duration,
                event,
                True
            ))

        return Timeline(bucket_type, all_points)

    def __init__(self, bucket_type: BucketType, points: BucketPoints):
        self._bucket_type = bucket_type
        self._points = points
        self._points.sort()

    def intersect(self, spec_timeline: 'Timeline', intersect_condition: CutCondition, inclusive: bool = True) -> None:
        """
        Finds an intersection of 2 timelines.
        :param spec_timeline: Timeline to compare against
        :param intersect_condition: Conditional function which defines which points in spec_timeline are considered
        :param inclusive: If False then those points are returned which don't belong to the intersection
        :return: All points of the current timeline which intersect (or not if exclusively) the given timeline
        """
        points = self._points.copy()
        for point in spec_timeline._points:
            points.append(point)
        points.sort()

        cut_points = []
        include = not inclusive
        opened_point = None
        for point in points:
            if point.get_event_type() == spec_timeline._bucket_type:
                if not intersect_condition(point):
                    continue
                if point.is_end():
                    include = not inclusive
                    if opened_point is not None:
                        cut_points.append(BucketPoint(
                            opened_point.get_event_type(),
                            point.get_timestamp(),
                            opened_point.get_event(),
                            inclusive
                        ))
                else:
                    include = inclusive
                    if opened_point is not None:
                        cut_points.append(BucketPoint(
                            opened_point.get_event_type(),
                            point.get_timestamp(),
                            opened_point.get_event(),
                            not inclusive
                        ))
            else:
                if include:
                    cut_points.append(point)
                if not point.is_end():
                    opened_point = point
                else:
                    opened_point = None

        if len(cut_points) > 0:
            current_time = cut_points[-1].get_timestamp()
            close_points: Dict[int, BucketPoint] = {}
            for i in reversed(range(len(cut_points))):
                point = cut_points[i]
                if point.get_timestamp() != current_time:
                    close_points.clear()
                    current_time = point.get_timestamp()
                if point.is_end():
                    close_points[i] = point
                elif len(close_points) > 0:
                    for index, opened_point in close_points.items():
                        if point.get_event() is opened_point.get_event():
                            del cut_points[index]
                            del cut_points[i]


        self._points = cut_points

    def get_points(self) -> BucketPoints:
        return self._points

    def get_browser_app(self, app_bucket_events: 'Timeline') -> Optional[str]:
        for point in self._points:
            app_point = app_bucket_events._get_event_at(point.get_timestamp())
            if app_point is None:
                continue
            if app_point.get_event_data()['title'].startswith(point.get_event_data()['title']):
                return str(app_point.get_event_data()['app'])
        return None

    def _get_event_at(self, at_time: datetime.datetime) -> Union[BucketPoint, None]:
        last_event = None
        for point in self._points:
            if point.is_end():
                continue
            if last_event is None:
                if point.get_timestamp() > at_time:
                    return None  # we don't know about the event before the 1st event in the timeline
            elif at_time < point.get_timestamp():
                return last_event
            last_event = point
        return None


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
