#!/usr/bin/env python3

from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from scipy.signal import filtfilt, butter
import bench as _b
import numpy as np

_TPoint = tuple[datetime, float]


def _last_n(data: list[_TPoint], delta: timedelta):
    assert len(data) > 0

    res: list[_TPoint] = []
    last = data[-1][0]

    for t, v in reversed(data):
        if t + delta < last:
            break
        res.insert(0, (t, v))
    else:
        print('Warning: found end of data for delta', delta)

    return res


def _avg(x: list[float]):
    return sum(x) / len(x)


def _avg_points(data: list[_TPoint]):
    av = _avg([v for _, v in data])
    return f'{av:.2f} F'


def _box_average(data: list[float], N: int = 5):
    res = []
    for i in range(len(data)):
        start = max(0, i - N)
        end = min(i + N, len(data))
        res.append(_avg(data[start:end]))
    return res


@_b.time
def _plot_w_smooth(ax, data: list[_TPoint]):
    x = [t for t, _ in data]
    y = [v for _, v in data]
    ax.set_ylabel('Temperature, F')
    ax.set_xlabel('Time')
    ax.grid()
    ax.plot(x, y, '.-', label='Raw', color='lightblue')

    def bp(n, Wn):
        b, a = butter(n, Wn)
        clean = filtfilt(b, a, y)
        ax.plot(x, clean, label='Butter {}, {}'.format(n, Wn))

    av = _avg(y)
    ax.plot([x[0], x[-1]], [av, av], '-k',
            label='Average {}'.format(f'{av:.2f} F'))

    N = 10
    box = _box_average(y, N)
    ax.plot(x, box, label='Box {}'.format(N))

    ax.legend()


if __name__ == '__main__':
    _b.start('all')

    _b.start('read')
    def _str2date(x): return datetime.fromisoformat(x.decode())
    headings = [('timestamp', 'object'), ('Temp_C', float), ('Temp_F', float)]
    full_data = np.genfromtxt('data/20230319.csv',
                              delimiter=',',
                              dtype=headings,
                              converters={0: _str2date})
    print('Read data in', _b.end('read'), 's')

    _b.start('zip')
    data: list[tuple[datetime, float]] = list(
        zip(full_data['timestamp'], full_data['Temp_F'])
    )
    print('Zip data in', _b.end('zip'), 's')

    _b.start('slice')
    last_point = data[-1][1]
    # last_week = _last_n(data, timedelta(days=7))
    last_day = _last_n(data, timedelta(days=1))
    last_hour = _last_n(data, timedelta(hours=1))
    last_minute = _last_n(data, timedelta(minutes=1))
    print('Slice data in', _b.end('slice'), 's')

    print('Last sample:', f'{last_point:.2f} F')
    # print('Last week:', _avg_points(last_week))
    print('Last day:', _avg_points(last_day))
    print('Last hour:', _avg_points(last_hour))
    print('Last minute:', _avg_points(last_minute))

    _b.start('plot')
    fig = plt.figure()

    ax1 = fig.add_subplot(311)
    _plot_w_smooth(ax1, last_minute)
    ax1.set_title('Last Minute')

    ax2 = fig.add_subplot(312)
    _plot_w_smooth(ax2, last_hour)
    ax2.set_title('Last Hour')

    ax3 = fig.add_subplot(313)
    _plot_w_smooth(ax3, last_day)
    ax3.set_title('Last Day')

    fig.tight_layout()
    print('Plot data in', _b.end('plot'), 's')

    print('All in', _b.end('all'), 's')
    plt.show()
