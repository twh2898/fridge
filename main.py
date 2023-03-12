#!/usr/bin/env python3

import os
from time import sleep
from datetime import datetime
import serial
from serial.serialutil import SerialException
import logging

LOGGING_FORMAT = '%(levelname)s:%(asctime)s:%(message)s'
logging.basicConfig(filename='collect_data.log',
                    level=logging.INFO,
                    format=LOGGING_FORMAT)
l = logging.getLogger(__name__)

PORT = '/dev/ttyUSB0'
BAUD = 9600
OUTDIR = 'data'

os.makedirs(OUTDIR, exist_ok=True)
start = datetime.now()
data_file = '{}.csv'.format(start.strftime('%Y%m%d_%H%M%S'))


def read_data(s, f):
    l.info('Reading data')

    data = s.readline()
    l.debug('Data is %s', data)

    line = data.decode().strip()
    now = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    line = str(now) + ',' + line
    print(line)
    n = f.write(line + '\n')
    l.debug('Write return %d', n)
    f.flush()


def main():
    l.info('Writing data to %s', data_file)
    l.info('Collecting data from %s at baud %d', PORT, BAUD)
    try:
        with serial.Serial(PORT, BAUD) as s, \
                open(os.path.join(OUTDIR, data_file), 'w') as f:

            l.debug('Serial port open')
            while True:
                read_data(s, f)

    except SerialException:
        l.exception('Error reading data')


if __name__ == '__main__':
    try:
        while True:
            main()
            sleep(1)
    except RuntimeError as e:
        l.exception('Runtime error')
