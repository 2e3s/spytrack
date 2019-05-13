import threading
import multiprocessing
from time import sleep
from typing import Union, Optional, Type
from types import TracebackType
from aw_core.log import setup_logging
from config import Config
from runner.afk import AfkRunner
from runner.server import server_run
from runner.windows import windows_watcher_run


class Runner:
    process_server: Union[multiprocessing.Process, None]
    thread_watcher_awk: threading.Thread
    process_watcher_windows: multiprocessing.Process

    def __init__(self, config: Config) -> None:
        self.config = config
        self.afk_runner = AfkRunner()
        setup_logging(
            "aw-runner",
            testing=False,
            verbose=False,
            log_stderr=False,
            log_file=False
        )

    def run_all(self) -> None:
        if self.config.run_daemon:
            self.process_server = multiprocessing.Process(target=server_run)
            self.process_server.start()
            sleep(1)

        self.thread_watcher_awk = threading.Thread(target=self.afk_runner.run)
        self.thread_watcher_awk.start()

        # TODO.md make it a thread
        self.process_watcher_windows = multiprocessing.Process(
            target=windows_watcher_run
        )
        self.process_watcher_windows.start()

    def reload(self, config: Config) -> None:
        self.config = config
        self.stop()
        sleep(1)
        self.run_all()

    def stop(self) -> None:
        if self.process_server is not None:
            self.process_server.terminate()
            self.process_server = None

        self.afk_runner.stop()
        self.process_watcher_windows.terminate()

    def __enter__(self) -> None:
        self.run_all()

    def __exit__(self,
                 exc_type: Optional[Type[BaseException]],
                 exc_val: Optional[BaseException],
                 exc_tb: Optional[TracebackType]) -> None:
        self.stop()
