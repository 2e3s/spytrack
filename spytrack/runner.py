from runner import Runner
from config import ConfigStorage, get_config_filename

config_storage = ConfigStorage(get_config_filename())
config = config_storage.load()
aw_runner = Runner(config)
aw_runner.run_all()
