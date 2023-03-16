#!/usr/bin/env python3

import os
from time import sleep
from datetime import datetime
import logging

from sensor import ADC

LOGGING_FORMAT = '%(levelname)s:%(asctime)s:%(message)s'
logging.basicConfig(filename='fridge.log',
                    level=logging.INFO,
                    format=LOGGING_FORMAT)
_l = logging.getLogger(__name__)

OUTDIR = 'data'
SAMPLE_RATE = 1  # Hz
N_CHANNELS = 1
assert 1 <= N_CHANNELS <= 4, 'Invalid number of channels to record'

os.makedirs(OUTDIR, exist_ok=True)


def main():
    _l.info('Starting data acquisition')
    _l.debug('Sample frequency %f hz', SAMPLE_RATE)

    sensor = ADC()

    start = datetime.now()
    _l.debug('Start time is %s', start)

    data_file = '{}.csv'.format(start.strftime('%Y%m%d'))
    f = open(os.path.join(OUTDIR, data_file), 'a')
    _l.info('Writing data to %s', data_file)

    while True:
        now = datetime.now()
        if now.date() != start.date():
            _l.debug('Current date %s does not match last date %s',
                     now.date(), start.date())
            _l.info('Rotating data files', now.date())
            if f:
                f.close()
            data_file = '{}.csv'.format(start.strftime('%Y%m%d'))
            f = open(os.path.join(OUTDIR, data_file), 'a')
            _l.info('Writing data to %s', data_file)

        row = [str(now)]
        for channel in range(N_CHANNELS):
            _, _, t_c, t_f = sensor.read(channel)
            print('Channel', channel, f'{t_f:.2f} F')
            row.append(f'{t_c:.4f}')
            row.append(f'{t_f:.4f}')

        f.write(','.join(row) + '\n')
        f.flush()

        wait_s = 1 / SAMPLE_RATE
        _l.debug('Sleeping for %d seconds', wait_s)
        sleep(wait_s)


if __name__ == '__main__':
    try:
        main()

    except RuntimeError as e:
        _l.exception('Runtime error')
        raise e

    except Exception as e:
        _l.exception('Exception')
        raise e
