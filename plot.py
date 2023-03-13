#!/usr/bin/env python3

import os
import csv
from time import process_time
from datetime import datetime, timedelta
from dateutil.parser import parse
import matplotlib.pyplot as plt
from enum import Enum, auto
from dataclasses import dataclass
from scipy.signal import filtfilt, butter
import numpy as np


class Unit(Enum):
    Raw = auto()
    C = auto()
    F = auto()


GLOBAL_UNIT = Unit.F


@dataclass
class Point:
    raw: int
    c: float
    f: float
    time: datetime

    def __str__(self):
        unit = GLOBAL_UNIT
        return as_unit(self.unit_value(unit), unit)

    def unit_value(self, unit: Unit = GLOBAL_UNIT) -> int | float:
        if unit == Unit.Raw:
            return self.raw
        elif unit == Unit.C:
            return self.c
        elif unit == Unit.F:
            return self.f
        raise RuntimeError('Invalid Unit', unit)


def as_unit(x: int | float, unit: Unit = GLOBAL_UNIT):
    if unit == Unit.Raw:
        return str(x)
    elif unit == Unit.C:
        return '{:.2f} C'.format(x)
    elif unit == Unit.F:
        return '{:.2f} F'.format(x)


def from_row(row: list[str]) -> Point:
    assert len(row) == 4, 'Row must have 4 strings'
    time, raw, t_c, t_f = row
    return Point(int(float(raw)), float(t_c), float(t_f), parse(time))


def last_n(data: list[Point], delta: timedelta):
    assert len(data) > 0

    res: list[Point] = []
    last = data[-1]

    for curr in reversed(data):
        if curr.time + delta < last.time:
            break
        res.insert(0, curr)
    else:
        print('Warning: found end of data for delta', delta)

    return res


def avg(x: list):
    return sum(x) / len(x)


def avg_points(data: list[Point], time_index=0):
    a_raw = avg([p.raw for p in data])
    a_c = avg([p.c for p in data])
    a_f = avg([p.f for p in data])

    return Point(int(a_raw), a_c, a_f, data[time_index].time)


def _box(n, data):
    assert len(data) > n * 2

    res = [data[n] for _ in range(n)]
    for i in range(n, len(data)-n):
        s = sum(data[i-n: i+n])
        res.append(s / (n * 2))
    res += [data[len(data) - n] for _ in range(n)]
    return res


def avg_per_time(data: list[Point], delta: timedelta):
    res = []

    start = 0
    for i in range(len(data)):
        t_start = data[start].time
        c_time = data[i].time

        if c_time > t_start + delta:
            res.append(avg_points(data[start:i], time_index=-1))
            start = i

    if start != len(data):
        res.append(avg_points(data[start:], time_index=-1))

    return res


def plot_w_smooth(ax, data: list[Point]):
    x = np.array([p.time for p in data])
    values = [p.unit_value() for p in data]
    ax.set_ylabel('Temperature, {}'.format(GLOBAL_UNIT.name))
    ax.set_xlabel('Time')
    ax.grid()
    ax.plot(x, values, label='Raw', color='lightblue')

    def bp(n, Wn):
        b, a = butter(n, Wn)
        clean = filtfilt(b, a, values)
        ax.plot(x, clean, label='Butter {}, {}'.format(n, Wn))

    Wn = 0.03
    bp(1, Wn)
    bp(2, Wn)
    bp(4, Wn)
    bp(8, Wn)

    k_s = 50
    kernel = np.ones(k_s) / k_s
    box = np.convolve(values, kernel, mode='same')
    # ax.plot(x, box, label='Box {}'.format(k_s))

    ra = _box(100, values)
    # ax.plot(x, ra, label='Box')

    average = avg_points(data)
    av = average.unit_value()
    ax.plot([x[0], x[-1]], [av, av], '-k',
            label='Average {}'.format(average))

    a = avg_per_time(data, timedelta(minutes=1))
    x = [p.time for p in a]
    y = [p.unit_value() for p in a]
    # ax.plot(x, y, label='Avg per min')

    ax.legend()


if __name__ == '__main__':
    _start = process_time()
    with open('data/20230313.csv', 'r', newline='') as f:
        reader = csv.reader(f)
        data = list(reader)
    _end = process_time()

    print('Read data in', ((_end - _start) * 1000), 'ms')

    _start = process_time()
    points = [from_row(r) for r in data]
    _end = process_time()

    print('Parse data in', ((_end - _start) * 1000), 'ms')

    _start = process_time()
    last_point = points[-1]
    last_minute = last_n(points, timedelta(minutes=1))
    last_week = last_n(points, timedelta(days=7))
    last_day = last_n(points, timedelta(days=1))
    last_hour = last_n(points, timedelta(hours=1))
    _end = process_time()

    print('Processed lists in', ((_end - _start) * 1000), 'ms')

    print('Last sample:', last_point)
    print('Last minute:', avg_points(last_minute))
    print('Last hour:', avg_points(last_hour))
    print('Last day:', avg_points(last_day))
    print('Last week:', avg_points(last_week))

    _start = process_time()
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
    _end = process_time()

    print('Plot data in', ((_end - _start) * 1000), 'ms')

    plt.show()
    # Plots
    # last minute raw + smooth
    # last hour raw + smooth
    # last day row + smooth
    # last week row + smooth
    # last month row + smooth
    # last year row + smooth
