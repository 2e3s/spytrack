from aw_client import ActivityWatchClient
from datetime import datetime, timedelta, timezone
from aw_core.models import Event
from time import sleep
from platform import system
import os
if system() == "Windows":
    from aw_watcher_afk.windows import seconds_since_last_input
elif system() == "Darwin":
    from aw_watcher_afk.macos import seconds_since_last_input
elif system() == "Linux":
    from aw_watcher_afk.unix import seconds_since_last_input
else:
    raise Exception("Unsupported platform: {}".format(system()))


def afk_watcher_run() -> None:
    watcher = AfkRunner()
    watcher.run()


class AfkRunner:
    timeout = 180
    poll_time = 5
    initiated_shutdown = False

    def __init__(self) -> None:
        self.client = ActivityWatchClient("aw-watcher-afk", testing=False)
        self.bucketname = "{}_{}".format(self.client.client_name, self.client.client_hostname)

    def ping(self, afk: bool, timestamp: datetime, duration: float = 0) -> None:
        data = {"status": "afk" if afk else "not-afk"}
        e = Event(timestamp=timestamp, duration=duration, data=data)
        pulsetime = self.timeout + self.poll_time
        self.client.heartbeat(self.bucketname, e, pulsetime=pulsetime, queued=True)

    def run(self) -> None:
        # Initialization
        sleep(1)

        eventtype = "afkstatus"
        self.client.create_bucket(self.bucketname, eventtype, queued=True)

        with self.client:
            self.heartbeat_loop()

    def stop(self) -> None:
        self.initiated_shutdown = True

    def heartbeat_loop(self) -> None:
        afk = False
        while True:
            if self.initiated_shutdown:
                self.initiated_shutdown = False
                break
            try:
                if system() in ["Darwin", "Linux"] and os.getppid() == 1:
                    break

                now = datetime.now(timezone.utc)
                seconds_since_input = seconds_since_last_input()
                last_input = now - timedelta(seconds=seconds_since_input)

                # If no longer AFK
                if afk and seconds_since_input < self.timeout:
                    self.ping(afk, timestamp=last_input)
                    afk = False
                    self.ping(afk, timestamp=last_input)
                # If becomes AFK
                elif not afk and seconds_since_input >= self.timeout:
                    self.ping(afk, timestamp=last_input)
                    afk = True
                    self.ping(afk, timestamp=last_input, duration=seconds_since_input)
                # Send a heartbeat if no state change was made
                else:
                    if afk:
                        self.ping(afk, timestamp=last_input, duration=seconds_since_input)
                    else:
                        self.ping(afk, timestamp=last_input)

                sleep(self.poll_time)

            except KeyboardInterrupt:
                break
