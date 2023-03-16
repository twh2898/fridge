"""Temperature sensor."""

from math import log as _log
import Adafruit_ADS1x15 as _adafruit
import logging as _logging

_l = _logging.getLogger(__name__)

# Choose a gain of 1 for reading voltages from 0 to 4.09V.
# Or pick a different gain to change the range of voltages that are read:
#  - 2/3 = +/-6.144V
#  -   1 = +/-4.096V
#  -   2 = +/-2.048V
#  -   4 = +/-1.024V
#  -   8 = +/-0.512V
#  -  16 = +/-0.256V
# See table 3 in the ADS1015/ADS1115 datasheet for more info on gain.
GAIN = 1
VREF = 4.096
_bits = 16
_raw_range = 2 ** (_bits - 1)

VCC = 5

CHANNEL = 0

# Values should be in datasheet
R = 10_000  # ohm
B = 3877  # K

T0 = 23 + 273.15  # 23 C base to kelvin


def _to_v(raw):
    return raw * VREF / _raw_range


def _k_to_c(k):
    return k - 273.15


def _c_to_f(c):
    return c * 1.8 + 32


class ADC:
    """Interface for reading temperature sensors."""

    def __init__(self):
        """Create a new ADC instance."""
        self.adc = _adafruit.ADS1115()
        _l.debug('Create ADC instance')

    def read(self, channel: int = 0) -> tuple[int, float, float, float]:
        """
        Read analog voltage and convert to temperature.

        Returns a tuple of
            - (int) raw
            - (float) kelvin
            - (float) celsius
            - (float) fahrenheit
        """
        assert 0 <= channel <= 3, 'Invalid channel %d' % channel
        _l.info('Read sensor channel %d', channel)

        raw: int = self.adc.read_adc(CHANNEL, gain=GAIN)
        _l.debug('Raw value is %d', raw)

        v = _to_v(raw)
        vr = VCC - v
        rt = v / (vr / R)
        ln = _log(rt / R)

        t_k = 1 / ((ln / B) + (1 / T0))
        t_c = _k_to_c(t_k)
        t_f = _c_to_f(t_c)

        _l.debug('Convert to temperatures %f K %f C %f F', t_k, t_c, t_f)
        return raw, t_k, t_c, t_f
