default_yaml = """
daemon:
  host: http://localhost
  port: 5600
gui:
  interval: 5
  projects:
  - name: coding
    rules:
    - app: pycharm
      type: app
    - title: Qt Designer
      type: app
    - type: web
      url: .*qt.io.*
    - type: web
      url: python
    - title: python
      type: web
    - title: pyqt
      type: web
    - app: code
      title: .*Visual Studio Code
      type: app
  run_daemon: true
  start_day_time: '5:00'
"""
