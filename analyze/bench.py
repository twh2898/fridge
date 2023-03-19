"""Helper functions for benchmark and timing."""

from time import process_time

_timers: dict[str, float] = {}


def start(name: str):
    """Store the current time for name."""
    _timers[name] = process_time()


def end(name: str):
    """Get the time delta for name."""
    assert name in _timers, 'No timer {} exists'.format(name)
    return process_time() - _timers[name]


def time(fn):
    """Time a function."""
    name = f'{fn.__module__}.{fn.__name__}'

    def wrapper(*a, **kw):
        start = process_time()
        res = fn(*a, **kw)
        end = process_time()
        delta = end - start
        print(name, 'in', delta, 's')
        return res

    return wrapper
