import argparse

from runner import Runner
from config import ConfigStorage, get_config_filename
from gui import Gui

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-tray", dest='no_tray', action='store_true', default=False)
    args, _ = parser.parse_known_args()

    config_storage = ConfigStorage(get_config_filename())
    if args.no_tray:
        config = config_storage.load()
        aw_runner = Runner(config)
        aw_runner.run_all()
    else:
        stats_runner = Runner(config_storage.load())
        gui = Gui(config_storage, stats_runner)
        gui.run_headless()
