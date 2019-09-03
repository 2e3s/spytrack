1. (1) - high priority
2. (2) - unknown priority
3. (3) - low priority
4. (4) - Under question

# Planned features

- (3) Add pomidoro technique
- (2) Mark web events with browser app
- (2) Self-tracking on click in tray or shortcut (takes more priority over other events)
- (3) Add tags over projects

## Optimization

- (1) Don't re-render if the window is hidden
- (1) Move out computations to a separate window
- (1) Reduce memory footprint by [optimizing](https://habr.com/ru/post/455722/) events
- (3) Don't intersect all events, only after the last intersected one
- (3) Don't aggregate on all events, add to the intersection only the last events

## Configuration

- (1) The config file should be create from the default one
- (2) Put the configuration file to the local directory
- (1) Add stop-list for app tracker
- (2) Wildcard rules and special syntax for regexp rules
- (1) Validate input forms

## UI

- (1) Aggregate events by data
- (2) Icon should change depending on the current project
- (4) Projects should be added, removed and edited in a separated UI rather than a config
- (3) Change tray icon depending on a project and its completion
- (2) "Add a rule" dialog to on double-click on project's event
- (3) Inclusive and exclusive filtering for events on the selected project (for analyzing mismatches).
      Maybe a normal string with ES-like syntax: `+search1 +"search2 complex" -"search exclude"` for simplicity
- (2) Make projects settings collapsable
- (2) Edit start of the day

## Projects

- (2) Bar diagram by projects normalized by the specified time to spend
- (2) Add a maximum time for a project

# Planned fixes

- (1) List of projects and their events should be updated after any start-end time change
- (2) Make AW web-ui link configurable
- (2) Redraw chart on Today checkbox or date change

## Refactoring

- (2) Run windows_watcher_run in a thread
- (3) Move out settings widget
- (3) Remove EventsAnalyzer in favor of root functions
- (3) Remove aw_core.Event usage besides repository

## Bugs

July 31 -> August 1
Traceback (most recent call last):
  File "spytrack/gui/main_page_widget.py", line 78, in _run_chart
    start_date = self._get_last_day_beginning(end_date)
  File "spytrack/gui/main_page_widget.py", line 64, in _get_last_day_beginning
    start_time = start_time.replace(day=start_time.day - 1)
ValueError: day is out of range for month


Traceback (most recent call last):
  File "/usr/lib/python3.6/threading.py", line 916, in _bootstrap_inner
    self.run()
  File "~/projects/spytrack/venv/lib/python3.6/site-packages/pykeyboard/x11.py", line 252, in run
    self.display2.record_enable_context(self.ctx, self.handler)
  File "~/projects/spytrack/venv/lib/python3.6/site-packages/Xlib/ext/record.py", line 243, in enable_context
    context = context)
  File "~/projects/spytrack/venv/lib/python3.6/site-packages/Xlib/ext/record.py", line 220, in __init__
    rq.ReplyRequest.__init__(self, *args, **keys)
  File "~/projects/spytrack/venv/lib/python3.6/site-packages/Xlib/protocol/rq.py", line 1369, in __init__
    self.reply()
  File "~/projects/spytrack/venv/lib/python3.6/site-packages/Xlib/protocol/rq.py", line 1381, in reply
    self._display.send_and_recv(request = self._serial)
  File "~/projects/spytrack/venv/lib/python3.6/site-packages/Xlib/protocol/display.py", line 612, in send_and_recv
    gotreq = self.parse_response(request)
  File "~/projects/spytrack/venv/lib/python3.6/site-packages/Xlib/protocol/display.py", line 704, in parse_response
    gotreq = self.parse_request_response(request) or gotreq
  File "~/projects/spytrack/venv/lib/python3.6/site-packages/Xlib/protocol/display.py", line 792, in parse_request_response
    req._parse_response(self.data_recv[:self.recv_packet_len])
  File "~/projects/spytrack/venv/lib/python3.6/site-packages/Xlib/ext/record.py", line 224, in _parse_response
    self._callback(r)
  File "~/projects/spytrack/venv/lib/python3.6/site-packages/pykeyboard/x11.py", line 273, in handler
    self._tap(event)
  File "~/projects/spytrack/venv/lib/python3.6/site-packages/pykeyboard/x11.py", line 285, in _tap
    character = self.keysym_to_string[keysym]
KeyError: 65032

ERROR:aw_watcher_window.main:Exception thrown while trying to get active
window: 'NoneType' object has no attribute 'decode' Traceback (most
recent call last): File
"~/projects/spytrack/venv/lib/python3.6/site-packages/aw_watcher_window/main.py",
line 65, in heartbeat_loop current_window = get_current_window() File
"~/projects/spytrack/venv/lib/python3.6/site-packages/aw_watcher_window/lib.py",
line 44, in get_current_window return get_current_window_linux() File
"~/projects/spytrack/venv/lib/python3.6/site-packages/aw_watcher_window/lib.py",
line 14, in get_current_window_linux name = xlib.get_window_name(window)
File
"~/projects/spytrack/venv/lib/python3.6/site-packages/aw_watcher_window/xlib.py",
line 65, in get_window_name return r.decode('latin1') # WM_NAME with
type=STRING. AttributeError: 'NoneType' object has no attribute 'decode'
