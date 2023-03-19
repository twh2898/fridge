import configparser
from dataclasses import dataclass


class ConfigError(RuntimeError):
    pass


@dataclass
class LoggingConfig:
    level: str
    filename: str


@dataclass
class DataConfig:
    channels: int
    sample_rate: float
    output_path: str


@dataclass
class Config:
    logging: LoggingConfig
    data: DataConfig


def load_config(path):
    cfg = configparser.ConfigParser()
    cfg.read(path)

    if __debug__:
        if 'debug' not in cfg:
            raise ConfigError('Missing section debug')
        config = cfg['debug']

    else:
        if 'release' not in cfg:
            raise ConfigError('Missing section release')
        config = cfg['release']

    def _get_key(key):
        if key not in config:
            raise ConfigError('Missing key %s', key)
        else:
            return config.get(key)

    def _get_int(key):
        value = _get_key(key)
        try:
            return int(value)

        except ValueError:
            raise ConfigError('Expected int for %s, got %s',
                              key, value)

    def _get_float(key):
        value = _get_key(key)
        try:
            return float(value)

        except ValueError:
            raise ConfigError('Expected float for %s, got %s',
                              key, value)

    channels = _get_int('channels')
    if channels < 0 or channels > 4:
        raise ConfigError('Channels must be a number between 1 and 4, got %d',
                          channels)

    sample_rate = _get_float('sample_rate')
    if sample_rate <= 0:
        raise ConfigError('Sample rate must be > 0')

    return Config(
        LoggingConfig(
            config.get('log_level', 'WARNING'),
            config.get('log_path', ''),
        ),
        DataConfig(
            channels,
            sample_rate,
            _get_key('output_path'),
        ),
    )
