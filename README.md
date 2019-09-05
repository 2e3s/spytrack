# Spytrack

Spytrack is a desktop application to track and correct your work and other activities.
It analyzes your activity in applications and the Internet, builds a chart and looks into improving your efficiency.
The main goal is to be productive, hence all the provided functionality is built around that idea. Particularly to
fight procrastination and distractions and plan your work, hobbies etc.

## Install

TODO

To track your activities in browsers install the plugin for your browser from 
[here](https://github.com/ActivityWatch/aw-watcher-web) (Firefox, Chrome etc).

### From sources

```
git clone https://github.com/2e3s/spytrack.git
``` 
In the source folder:

- Full GUI application: `python spytrack`
- Just a tray icon (send stats only): `python spytrack/runner.py`
- Console, no GUI (send stats only): `python spytrack/runner.py --no-tray`

### Build

```
make build-all
```

### Run tests

Install a git hook to run on commit:
```
cat >> .git/hooks/pre-commit  <<EOL
#!/bin/bash

source venv/bin/activate
make test
exit \$?
chmod +x .git/hooks/pre-commit
```

### ActivityWatch

It's built on the base of [ActivityWatch server](https://github.com/ActivityWatch/aw-server/) being its desktop client. 
There is Qt application already which is basic, not well architected and pretty much useless. 
Also its [web-interface](http://localhost:5600) is available accordingly,
but having 2 applications is inconvenient, and the integration of a web-application with the desktop is rather subpar.

Thanks to the architecture, the daemon may be run separately, even on a different machine.
The loggers can also be run separately in with a very basic functionality if UI seems to take too much resources.

## Compatibility

The system is tested on the Linux only. Windows will follow.
