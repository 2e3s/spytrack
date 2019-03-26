import threading
from aw_core.log import setup_logging
from runner.afk import afk_watcher_run
from runner.server import server_run
from runner.windows import windows_watcher_run


class Runner:
    thread_server: threading.Thread
    thread_watcher_awk: threading.Thread
    thread_watcher_windows: threading.Thread

    def run_all(self) -> None:
        setup_logging("activity-watch", testing=False, verbose=False, log_stderr=True, log_file=True)
        self.thread_server = threading.Thread(target=server_run)
        self.thread_server.start()

        self.thread_watcher_awk = threading.Thread(target=afk_watcher_run)
        self.thread_watcher_awk.start()

        self.thread_watcher_windows = threading.Thread(target=windows_watcher_run)
        self.thread_watcher_windows.start()
