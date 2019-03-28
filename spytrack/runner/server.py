from aw_server.server import create_app
from aw_server.log import FlaskLogHandler
from aw_datastore import get_storage_methods


def server_run() -> None:
    storage_methods = get_storage_methods()
    storage_method = storage_methods['peewee']

    app = create_app(storage_method=storage_method, testing=False, cors_origins=[])
    app.static_folder = '/home/demi/Downloads/activitywatch/aw_server/static/'
    app.run(
        debug=False,
        host='localhost',
        port=5600,
        request_handler=FlaskLogHandler,
        use_reloader=False,
        threaded=False
    )
