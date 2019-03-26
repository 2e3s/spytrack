from time import sleep
from aw_client import ActivityWatchClient
from aw_watcher_window.main import heartbeat_loop


def windows_watcher_run() -> None:
    client = ActivityWatchClient("aw-watcher-window", testing=False)

    bucket_id = "{}_{}".format(client.client_name, client.client_hostname)
    event_type = "currentwindow"

    client.create_bucket(bucket_id, event_type, queued=True)
    sleep(1)  # wait for server to start
    with client:
        heartbeat_loop(client, bucket_id, poll_time=2.0, exclude_title=False)
