from aw_server.server import _start
from aw_datastore import get_storage_methods


def server_run() -> None:
    storage_methods = get_storage_methods()
    storage_method = storage_methods['peewee']

    _start(host='localhost', port=5600, testing=False, storage_method=storage_method, cors_origins=[])
