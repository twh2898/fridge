#!/usr/bin/env python3

import os
from time import sleep
from datetime import datetime
import logging
from config import load_config
import sqlite3

from sensor import ADC, Mock

config = load_config('reader.conf')

logging.basicConfig(filename=config.logging.filename,
                    level=config.logging.level,
                    format='%(asctime)s:%(levelname)s:%(name)s:%(message)s')
_l = logging.getLogger(__name__)

OUTDIR = config.data.output_path
os.makedirs(OUTDIR, exist_ok=True)


SQL_INSERT_QUERY = '''
INSERT INTO fridge_data (created, channel, temp_c, temp_f) VALUES(?, ?, ?, ?)
'''


def main(db: sqlite3.Connection):
    _l.info('Starting data acquisition')
    _l.debug('Sample frequency %f hz', config.data.sample_rate)

    sensor: ADC | Mock
    if __debug__:
        _l.info('Using mock sensor')
        sensor = Mock()
    else:
        sensor = ADC()

    while True:
        now = datetime.now()
        for channel in range(config.data.channels):
            _, _, t_c, t_f = sensor.read(channel)
            print('Channel', channel, f'{t_f:.2f} F')
            db.execute(SQL_INSERT_QUERY, (now, channel, t_c, t_f))

        db.commit()

        wait_s = 1 / config.data.sample_rate
        _l.debug('Sleeping for %f seconds', wait_s)
        sleep(wait_s)


if __name__ == '__main__':
    db = None
    try:
        _l.info('Opening database %s', config.data.db_path)
        db = sqlite3.connect(config.data.db_path)
        _l.debug('database open')

        with open('init.sql', 'r') as f:
            _l.debug('Running db init script')
            db.executescript(f.read())

        main(db)

    except sqlite3.Error as e:
        _l.exception('SQLite3 error')
        raise e

    except RuntimeError as e:
        _l.exception('Runtime error')
        raise e

    except Exception as e:
        _l.exception('Exception')
        raise e

    finally:
        if db:
            _l.info('Closing database')
            db.close()
