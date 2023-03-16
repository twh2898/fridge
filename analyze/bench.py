
from time import process_time

_timers: dict[str, float] = {}


def start(name: str):
    _timers[name] = process_time()


def end(name: str):
    assert name in _timers, 'No timer {} exists'.format(name)
    return process_time() - _timers[name]
