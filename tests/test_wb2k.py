import logging

import pytest

from wb2k.__main__ import bail, setup_logging


def test_bail():
    msg_type = 'fatal'
    color = 'red'
    text = "It doesn't go beyond 11."

    given = bail(msg_type, color, text)
    expected = "\x1b[31mfatal\x1b[0m: It doesn't go beyond 11."

    assert given == expected


@pytest.mark.parametrize('verbosity,log_level', [
    (0, 'INFO'),
    (1, 'DEBUG'),
    (2, 'DEBUG'),
])
def test_setup_logging(verbosity, log_level):
    setup_logging(verbosity)

    root_logger = logging.getLogger()
    requests_logger = logging.getLogger('requests.packages.urllib3')

    assert root_logger.level == getattr(logging, log_level)
    assert root_logger.propagate is True
    assert requests_logger.level == logging.CRITICAL

    handler = root_logger.handlers[0]
    formatter = handler.formatter

    assert isinstance(handler, logging.StreamHandler)
    assert formatter._fmt == '%(asctime)s [%(levelname)s] %(message)s'
    assert formatter.datefmt == '[%Y-%m-%d %H:%M:%S %z]'
