import datetime
from typing import Callable, List, Optional, Dict
from aw_core import Event as ParentEvent
from .event import Event
from .bucket_point import BucketPoint
from .bucket_type import BucketType

Events = List[Event]
BucketPoints = List[BucketPoint]


class Timeline:
    CutCondition = Callable[[BucketPoint], bool]

    @staticmethod
    def create_from_bucket_events(bucket_type: BucketType,
                                  events: Events
                                  ) -> 'Timeline':
        all_points = []
        for event in events:
            all_points.append(BucketPoint(bucket_type,
                                          event.timestamp,
                                          event,
                                          False))
            all_points.append(BucketPoint(
                bucket_type,
                event.timestamp + event.duration,
                event,
                True
            ))

        return Timeline(bucket_type, all_points)

    def __init__(self, bucket_type: BucketType, points: BucketPoints):
        self._bucket_type = bucket_type
        self.points = points
        self.points.sort()

    def intersect(self, spec_timeline: 'Timeline',  # noqa
                  intersect_condition: CutCondition,
                  inclusive: bool = True) -> None:
        """
        Finds an intersection of 2 timelines.
        Replaces all points of the current timeline by those which intersect
        (or not if exclusively) the given timeline

        :param spec_timeline: Timeline to compare against
        :param intersect_condition: Conditional function which defines
            which points in spec_timeline are considered
        :param inclusive: If False then those points are returned
            which don't belong to the intersection
        """
        points = self.points
        for point in spec_timeline.points:
            points.append(point)
        points.sort()

        cut_points = []
        include = not inclusive
        opened_point = None
        for point in points:
            if point.event_type == spec_timeline._bucket_type:
                if not intersect_condition(point):
                    continue
                if point.is_end():
                    include = not inclusive
                    if opened_point is not None:
                        cut_points.append(BucketPoint(
                            opened_point.event_type,
                            point.timestamp,
                            opened_point.event,
                            inclusive
                        ))
                else:
                    include = inclusive
                    if opened_point is not None:
                        cut_points.append(BucketPoint(
                            opened_point.event_type,
                            point.timestamp,
                            opened_point.event,
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
            current_time = cut_points[-1].timestamp
            close_points: Dict[int, BucketPoint] = {}
            for i in reversed(range(len(cut_points))):
                point = cut_points[i]
                if point.timestamp != current_time:
                    close_points.clear()
                    current_time = point.timestamp
                if point.is_end():
                    close_points[i] = point
                elif len(close_points) > 0:
                    for index, opened_point in close_points.items():
                        if point.event is opened_point.event:
                            del cut_points[index]
                            del cut_points[i]

        self.points = cut_points

    def get_browser_app(self, app_timeline: 'Timeline') -> Optional[str]:
        for point in self.points:
            app_point = app_timeline._get_event_at(point.timestamp)
            if app_point is None:
                continue
            app_point_title = app_point.event_data['title']
            point_title = point.event_data['title']
            if app_point_title.startswith(point_title):
                return str(app_point.event_data['app'])
        return None

    def _get_event_at(self,
                      at_time: datetime.datetime) -> Optional[BucketPoint]:
        last_event = None
        for point in self.points:
            if point.is_end():
                continue
            if last_event is None:
                if point.timestamp > at_time:
                    # we don't know about the event
                    # before the 1st event in the timeline
                    return None
            elif at_time < point.timestamp:
                return last_event
            last_event = point
        return None

    def get_events(self) -> Events:
        events = []
        for open_i in range(len(self.points)):
            open_point = self.points[open_i]
            if open_point.is_end():
                continue
            for close_i in range(open_i + 1, len(self.points)):
                close_point = self.points[close_i]
                if not close_point.is_end():
                    continue
                if open_point.event is close_point.event:
                    old_event = open_point.event
                    event = ParentEvent(
                        old_event.id,
                        open_point.timestamp,
                        close_point.timestamp - open_point.timestamp,
                        old_event.data
                    )
                    events.append(Event(event, open_point.event_type))
                    break

        return events
