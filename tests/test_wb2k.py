import logging
from unittest.mock import MagicMock

import pytest

from wb2k.__main__ import (
    bail,
    setup_logging,
    find_channel_id,
    handle_event,
)


@pytest.fixture
def slack_client():
    def api_call(method):
        return dict(
            channels=[{'id': 'D3ADB33F1', 'name': 'general'}],
            groups=[{'id': '1800IDGAF', 'name': 'super_secret_club'}],
        )

    slack_client = MagicMock(api_call=api_call)
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


def test_handle_event_ignores_all_but_group_and_channel_joins(slack_client, monkeypatch):
    channel = 'general'
    channel_id = '1337H4CKS'
    message = 'Hello, World!'

    # Note: This event needs to have a `user` or `handle_event` will just
    # ignore the event altogether regardless of its subtype.
    event = dict(
        type='message',
        channel=channel_id,
        user='XKCDP1337',
        text=message,
        ts='1355517523.000005'
    )

    monkeypatch.setattr(slack_client, 'rtm_send_message', MagicMock())
    logger = MagicMock()

    handle_event(
        event=event,
        channel=channel,
        channel_id=channel_id,
        message=message,
        sc=slack_client,
        logger=logger
    )

    # If the event didn't contain a group_join or channel_join subtype we
    # expect no messages to be sent via the RTM API.
    slack_client.rtm_send_message.assert_not_called()


def test_handle_event_channel_join(slack_client, monkeypatch):
    channel = 'general'
    channel_id = '1337H4CKS'
    message = "Welcome, {user}! :wave:"
    expected_message = 'Welcome, <@XKCDP1337>! :wave:'

    event = dict(
        channel=channel_id,
        subtype='channel_join',
        text='<@XKCDP1337> has joined the channel',
        type='message',
        user='XKCDP1337',
        user_profile=dict(
            display_name='Randall Munroe',
            # Many other fields omitted...
        )
    )

    monkeypatch.setattr(slack_client, 'rtm_send_message', MagicMock())
    logger = MagicMock()

    handle_event(
        event=event,
        channel=channel,
        channel_id=channel_id,
        message=message,
        sc=slack_client,
        logger=logger
    )

    slack_client.rtm_send_message.assert_called_once_with(channel_id,
                                                          expected_message)
