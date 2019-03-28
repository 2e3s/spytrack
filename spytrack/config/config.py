from typing import Dict, Any


class Config:
    config: Dict[str, Any]

    def __init__(self, values: Dict[str, Any]) -> None:
        self.port = int(values['daemon']['port'])
        self.host = str(values['daemon']['host'])
        self.interval = int(values['daemon']['interval'])
        self.run_daemon = 'gui' not in values or 'run_daemon' not in values['gui'] or values['gui']['run_daemon']

    def get_full_address(self) -> str:
        return '%s:%s' % (self.get_host(), self.get_port())

    def get_interval(self) -> int:
        return self.interval

    def get_host(self) -> str:
        return self.host

    def get_port(self) -> int:
        return self.port

    def is_run_server(self) -> bool:
        return self.run_daemon

    def set_interval(self, interval: int) -> None:
        self.interval = interval

    def set_port(self, port: int) -> None:
        self.port = port

    def set_host(self, host: str) -> None:
        self.host = host

    def set_run_server(self, run_daemon: bool) -> None:
        self.run_daemon = run_daemon
