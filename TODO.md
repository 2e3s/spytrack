1. (1) - high priority
2. (2) - unknown priority
3. (3) - low priority

# Planned features

- (3) Add pomidoro technique
- (2) Mark web events with browser app
- (2) Self-tracking on click in tray or shortcut (takes more priority over other events)

## Optimization

- (2) Don't fetch all events, only after the last fetched one
- (2) Don't intersect all events, only after the last intersected one
- (2) Don't aggregate on all events, add to the intersection only the last events

## Configuration

- (2) Put the configuration file to the local directory
- (1) Add stop-list for app tracker
- (2) Wildcard rules and special syntax for regexp rules

## UI

- (2) Icon should change depending on the current project
- (1) Projects should be added, removed and edited in a separated UI rather than a config
- (3) Change tray icon depending on a project and its completion
- (2) "Add a rule" dialog to on double-click on project's event
- (3) Inclusive and exclusive filtering for events on the selected project (for analyzing mismatches).
      Maybe a normal string with ES-like syntax: `+search1 +"search2 complex" -"search exclude"` for simplicity
- (3) Add tray icon to the simpler runner

## Projects

- (2) Bar diagram by projects normalized by the specified time to spend
- (2) Add a maximum time for a project

# Planned fixes

- (1) List of projects and their events should be updated after any start-end time change
- (2) Make AW web-ui link configurable
- (2) Redraw chart on Today checkbox or date change

## Refactoring

- (1) Name properties pythonic-way
- (2) Hide analyzer under facade
- (2) Hide AW client under a reading repository
- (1) Add a linter
- (2) Run windows_watcher_run in a thread
