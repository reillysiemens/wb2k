import os
import sys
import time
import logging
import logging.config

import click
from slackclient import SlackClient


def bail(msg_type, color, text):
    return "{}: {}".format(click.style(msg_type, fg=color), text)


def setup_logging(verbose):
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


def find_channel_id(channel, sc):
    channels_list = sc.api_call("channels.list").get('channels')
    groups_list = sc.api_call("groups.list").get('groups')

    if not channels_list and not groups_list:
        sys.exit(bail('fatal', 'red', "Couldn't enumerate channels/groups"))

    # Is there a better way to search a list of dictionaries? Probably.
    channel_ids = [c['id'] for c in channels_list + groups_list if c['name'] == channel]

    if not channel_ids:
        sys.exit(bail('fatal', 'red', "Couldn't find #{}".format(channel)))

    return channel_ids[0]


def handle_message(message, channel, channel_id, sc, logger):
    logger.debug(message)

    subtype = message.get('subtype')
    user = message.get('user')

    if subtype in ('group_join', 'channel_join') and user:

        message_channel_id = message.get('channel')
        user_profile = message.get('user_profile')
        username = user_profile.get('name')

        if message_channel_id == channel_id:
            try:
                sc.rtm_send_message(channel,
                                    "Welcome, <@{}>! :hand:".format(user))
                logger.info("Welcomed {} to #{}".format(username, channel))
            except AttributeError:
                logger.setLevel(logging.ERROR)
                logger.error("Couldn't send message to #{}".format(channel))


@click.command()
@click.option('-c', '--channel', envvar='WB2K_CHANNEL', default='general',
              show_default=True, metavar='CHANNEL',
              help='The channel to welcome users to.')
@click.option('-v', '--verbose', count=True, help='It goes to 11.')
@click.version_option()
def cli(channel, verbose):

    if verbose > 11:
        sys.exit(bail('fatal', 'red', "It doesn't go beyond 11"))

    # Get our logging in order.
    logger = logging.getLogger(__name__)
    setup_logging(verbose)

    # Make sure we have an API token.
    api_token = os.environ.get('WB2K_TOKEN')
    if not api_token:
        sys.exit(bail('fatal', 'red', 'WB2K_TOKEN envvar undefined'))

    # Instantiate and connect!
    sc = SlackClient(api_token)
    if sc.rtm_connect():
        logger.info("Connected to Slack")

        channel_id = find_channel_id(channel, sc)
        logger.debug("Found channel ID {} for #{}".format(channel_id, channel))

        logger.info("Listening for joins in #{}".format(channel))
        while True:
            # handle bug in slack websocket connection https://github.com/reillysiemens/wb2k/issues/1
            try:
                # Handle dem messages!
                for message in sc.rtm_read():
                    handle_message(message, channel, channel_id, sc, logger)

                time.sleep(0.5)
            except WebSocketConnectionClosedException:
                logger.error("Lost connection to Slack, reconnecting...")
                if not sc.rtm_connect():
                    logger.info("Failed to reconnect to Slack")
                    time.sleep(0.5)
                else:
                    logger.info("Reconnected to Slack")

    else:
        sys.exit(bail('fatal', 'red', "Couldn't connect to Slack"))
