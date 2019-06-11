import inspect
import pathlib


def get_current_directory() -> str:
    frame = inspect.currentframe()
    filename = inspect.getframeinfo(frame).filename  # type: ignore
    return str(pathlib.Path(filename).resolve().parent)
