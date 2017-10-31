import logging
import unittest.mock as mock

import pytest

from wb2k.__main__ import (
    bail,
    setup_logging,
    find_channel_id,
)


@pytest.fixture
def slack_client():
    def api_call(method):
        return dict(
            channels=[{'id': 'D3ADB33F1', 'name': 'general'}],
            groups=[{'id': '1800IDGAF', 'name': 'super_secret_club'}],
        )

    slack_client = mock.MagicMock(api_call=api_call)
    return slack_client


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


def test_find_channel_id_can_find_channels(slack_client):
    channel = 'general'
    channel_id = find_channel_id(channel, slack_client)
    assert channel_id == 'D3ADB33F1'


def test_find_channel_id_can_find_groups(slack_client):
    group = 'super_secret_club'
    group_id = find_channel_id(group, slack_client)
    assert group_id == '1800IDGAF'


def test_find_channel_id_fails_with_empty_channels_and_groups(slack_client, monkeypatch):
    channel = 'general'
    api_response = dict(
        channels=[],
        groups=[],
    )
    error_message = "\x1b[31mfatal\x1b[0m: Couldn't enumerate channels/groups"

    monkeypatch.setattr(slack_client, 'api_call', lambda m: api_response)

    with pytest.raises(SystemExit, message='Expecting SystemExit') as err:
        find_channel_id(channel, slack_client)

    assert str(err.value) == error_message


def test_find_channel_id_fails_with_missing_channel(slack_client, monkeypatch):
    channel = 'general'
    api_response = dict(
        channels=[{'id': '1337H4CKS', 'name': 'leet_haxors'}],
        groups=[],
    )
    error_message = f"\x1b[31mfatal\x1b[0m: Couldn't find #{channel}"

    monkeypatch.setattr(slack_client, 'api_call', lambda m: api_response)

    with pytest.raises(SystemExit, message='Expecting SystemExit') as err:
        find_channel_id(channel, slack_client)

    assert str(err.value) == error_message
