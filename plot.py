#!/usr/bin/env python3

import csv
from datetime import datetime, timedelta
from dateutil.parser import parse
import matplotlib.pyplot as plt
from enum import Enum, auto
from scipy.signal import filtfilt, butter

_TPoint = tuple[datetime, float]


class Unit(Enum):
    Raw = auto()
    C = auto()
    F = auto()


GLOBAL_UNIT = Unit.F


def as_unit(x: float):
    match GLOBAL_UNIT:
        case Unit.Raw:
            return str(int(x))
        case Unit.C:
            return '{:.2f} C'.format(x)
        case Unit.F:
            return '{:.2f} F'.format(x)


def from_row(row: list[str]) -> tuple[datetime, float]:
    assert len(row) == 4, 'Row must have 4 strings'

    time_s, raw, t_c, t_f = row
    time = parse(time_s)

    match GLOBAL_UNIT:
        case Unit.Raw:
            return time, float(raw)
        case Unit.C:
            return time, float(t_c)
        case Unit.F:
            return time, float(t_f)


def last_n(data: list[_TPoint], delta: timedelta):
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


def avg(x: list[float]):
    return sum(x) / len(x)


def avg_points(data: list[_TPoint]):
    av = avg([v for _, v in data])
    return as_unit(av)


def box_average(data: list[float], N: int = 5):
    res = []
    for i in range(len(data)):
        start = max(0, i - N)
        end = min(i + N, len(data))
        res.append(avg(data[start:end]))
    return res


def plot_w_smooth(ax, data: list[_TPoint]):
    x = [t for t, _ in data]
    y = [v for _, v in data]
    ax.set_ylabel('Temperature, {}'.format(GLOBAL_UNIT.name))
    ax.set_xlabel('Time')
    ax.grid()
    ax.plot(x, y, '.-', label='Raw', color='lightblue')

    def bp(n, Wn):
        b, a = butter(n, Wn)
        clean = filtfilt(b, a, y)
        ax.plot(x, clean, label='Butter {}, {}'.format(n, Wn))

    Wn = 0.03
    bp(1, Wn)
    # bp(2, Wn)
    # bp(4, Wn)
    # bp(8, Wn)

    av = avg(y)
    ax.plot([x[0], x[-1]], [av, av], '-k',
            label='Average {}'.format(as_unit(av)))

    N = 10
    box = box_average(y, N)
    ax.plot(x, box, label='Box {}'.format(N))

    ax.legend()


if __name__ == '__main__':
    with open('data/20230314.csv', 'r', newline='') as f:
        reader = csv.reader(f)
        data = list(map(from_row, reader))

    last_point = data[-1][1]
    last_minute = last_n(data, timedelta(minutes=1))
    last_week = last_n(data, timedelta(days=7))
    last_day = last_n(data, timedelta(days=1))
    last_hour = last_n(data, timedelta(hours=1))

    print('Last sample:', as_unit(last_point))
    print('Last minute:', avg_points(last_minute))
    print('Last hour:', avg_points(last_hour))
    print('Last day:', avg_points(last_day))
    print('Last week:', avg_points(last_week))

    fig = plt.figure()

    # ax1 = fig.add_subplot(211)
    # plot_w_smooth(ax1, last_minute)
    # ax1.set_title('Last Minute')

    ax2 = fig.add_subplot(211)
    plot_w_smooth(ax2, last_hour)
    ax2.set_title('Last Hour')

    ax3 = fig.add_subplot(212)
    plot_w_smooth(ax3, last_day)
    ax3.set_title('Last Day')

    fig.tight_layout()

    plt.show()
    # Plots
    # last minute raw + smooth
    # last hour raw + smooth
    # last day row + smooth
    # last week row + smooth
    # last month row + smooth
    # last year row + smooth
