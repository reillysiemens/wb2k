import sys
import time
import logging
import logging.config
from pprint import pformat

import click
import websocket  # Depedency of slackclient, needed for exception handling
from slackclient import SlackClient

__author__ = 'Reilly Tucker Siemens'
__email__ = 'reilly@tuckersiemens.com'
__version__ = '0.1.0'


def bail(msg_type: str, color: str, text: str) -> str:
    return f"{click.style(msg_type, fg=color)}: {text}"


def setup_logging(verbose: int) -> None:
    logging.config.dictConfig({
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': "%(asctime)s [%(levelname)s] %(message)s",
                'datefmt': "[%Y-%m-%d %H:%M:%S %z]",
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'standard',
            },
        },
        'loggers': {
            '': {
                'handlers': ['console'],
                'level': logging.INFO if verbose < 1 else logging.DEBUG,
                'propagate': True,
            },
            'requests.packages.urllib3': {  # Oh, do shut up, requests.
                'handlers': ['console'],
                'level': logging.CRITICAL,
            },
        },
    })


def find_channel_id(channel: str, sc: SlackClient) -> str:
    channels_list = sc.api_call("channels.list").get('channels')
    groups_list = sc.api_call("groups.list").get('groups')

    if not channels_list and not groups_list:
        sys.exit(bail('fatal', 'red', "Couldn't enumerate channels/groups"))

    # Is there a better way to search a list of dictionaries? Probably.
    channel_ids = [c['id'] for c in channels_list + groups_list if c['name'] == channel]

    if not channel_ids:
        sys.exit(bail('fatal', 'red', f"Couldn't find #{channel}"))

    return channel_ids[0]


def handle_event(event: dict, channel: str, channel_id: str, message: str,
                 sc: SlackClient, logger: logging.Logger) -> None:
    pretty_event = pformat(event)
    logger.debug(f"Event received:\n{pretty_event}")

    subtype = event.get('subtype')
    user = event.get('user')

    if subtype in ('group_join', 'channel_join') and user:

        # We will use the event's channel ID to send a response and refer to
        # users by their display_name in accordance with new guidelines.
        # https://api.slack.com/changelog/2017-09-the-one-about-usernames
        event_channel_id = event.get('channel')
        user_profile = event.get('user_profile')
        username = user_profile.get('display_name')
        user_mention = f"<@{user}>"
        message = message.replace('{user}', user_mention)

        if event_channel_id == channel_id:
            try:
                sc.rtm_send_message(event_channel_id, message)
                logger.info(f"Welcomed {username} to #{channel}")
            except AttributeError:
                logger.error(f"Couldn't send message to #{channel}")


def run(sc: SlackClient, channel: str, message: str, retries: int,
        logger: logging.Logger) -> None:
    if sc.rtm_connect():
        logger.info("Connected to Slack")

        channel_id = find_channel_id(channel, sc)
        logger.debug(f"Found channel ID {channel_id} for #{channel}")

        logger.info(f"Listening for joins in #{channel}")

        retry_count = 0
        backoff = 0.5

        while True:
            try:
                # Handle dem events!
                for event in sc.rtm_read():
                    handle_event(event, channel, channel_id, message, sc, logger)

                # Reset exponential backoff retry strategy every time we
                # successfully loop. Failure would have happened in rtm_read()
                retry_count = 0

                time.sleep(0.5)

            # This is necessary to handle an error caused by a bug in Slack's
            # Python client. For more information see
            # https://github.com/slackhq/python-slackclient/issues/127
            #
            # The TimeoutError could be more elegantly resolved by making a PR
            # to the websocket-client library and letting them coerce that
            # exception to a WebSocketTimeoutException.
            except (websocket.WebSocketConnectionClosedException, TimeoutError):
                logger.error("Lost connection to Slack, reconnecting...")
                if not sc.rtm_connect():
                    logger.info("Failed to reconnect to Slack")
                    if retry_count >= retries:
                        sys.exit(bail(
                            'fatal',
                            'red',
                            "Too many failed reconnect attempts, shutting down")
                        )
                    time.sleep((backoff ** 2) / 4)
                else:
                    logger.info("Reconnected to Slack")

                retry_count += 1

    else:
        sys.exit(bail('fatal', 'red', "Couldn't connect to Slack"))
