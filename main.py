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


def read_data(s, f):
    last_date = datetime.now().date()

    while True:
        l.info('Reading data')

        data = s.readline()
        l.debug('Data is %s', data)

        line = data.decode().strip()

        now = datetime.now()
        if now.date() != last_date:
            # Yes, I know this drops one point... sue me
            l.info('Date changed %s to %s, Switching', now.date(), last_date)
            return
        last_date = now.date()

        now_str = now.strftime('%Y-%m-%dT%H:%M:%S')
        line = now_str + ',' + line
        print(line)
        n = f.write(line + '\n')
        l.debug('Write return %d', n)
        f.flush()

        l.debug('loop')


def main():
    l.info('Connecting to %s at baud %d', PORT, BAUD)
    try:
        with serial.Serial(PORT, BAUD) as s:
            l.debug('Serial port open')

            while True:
                start = datetime.now()
                data_file = '{}.csv'.format(start.strftime('%Y%m%d'))
                l.info('Writing data to %s', data_file)

                with open(os.path.join(OUTDIR, data_file), 'a') as f:
                    read_data(s, f)

    except SerialException:
        l.exception('Error reading data')

    l.info('Exiting main')


if __name__ == '__main__':
    try:
        while True:
            main()
            l.info('Waiting for a new connection')
            sleep(1)

    except RuntimeError as e:
        l.exception('Runtime error')
        raise e

    except Exception as e:
        l.exception('Exception')
        raise e
