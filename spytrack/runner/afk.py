from aw_watcher_afk.afk import AFKWatcher


def afk_watcher_run() -> None:
    watcher = AFKWatcher()
    watcher.run()
