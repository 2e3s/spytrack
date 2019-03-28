from runner import Runner
from config import ConfigStorage, get_config_filename

config_storage = ConfigStorage(get_config_filename())

aw_runner = Runner()
aw_runner.run_all(config_storage.load())
