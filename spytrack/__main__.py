from config import ConfigStorage, get_config_file
from gui import Gui
from runner import Runner

config_storage = ConfigStorage(get_config_file())
stats_runner = Runner(config_storage.load())
gui = Gui(config_storage, stats_runner)
gui.run()
