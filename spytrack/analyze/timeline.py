import datetime
from typing import Callable, List, Optional, Union, Dict
from aw_core import Event
from .bucket_point import BucketPoint
from .bucket_type import BucketType

Events = List[Event]
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

    def get_events(self) -> Events:
        events = []
        for open_i in range(len(self._points)):
            open_point = self._points[open_i]
            if open_point.is_end():
                continue
            for close_i in range(open_i, len(self._points)):
                close_point = self._points[close_i]
                if not close_point.is_end():
                    continue
                if open_point.get_event() is close_point.get_event():
                    old_event = open_point.get_event()
                    events.append(Event(
                        old_event.id,
                        open_point.get_timestamp(),
                        close_point.get_timestamp() - open_point.get_timestamp(),
                        old_event.data
                    ))

        return events
