import inspect
import pathlib


def get_current_directory() -> str:
    filename = inspect.getframeinfo(inspect.currentframe()).filename  # type: ignore
    return str(pathlib.Path(filename).resolve().parent)
