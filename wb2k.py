import logging
import os

import click
from slackclient import SlackClient

from layabout import Layabout, LayaboutError

__author__ = 'Reilly Tucker Siemens'
__email__ = 'reilly@tuckersiemens.com'
__version__ = '0.2.0-what-did-you-expect'

app = Layabout()


class ChannelNotFound(Exception):
    """ TODO """


def configure_logger(verbose: int) -> logging.Logger:
    """ TODO """
    logging.basicConfig(
        level=logging.INFO if verbose < 1 else logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt='[%Y-%m-%d %H:%M:%S %z]'
    )
    logging.getLogger('urllib3').setLevel(logging.CRITICAL)  # Quiet, requests.
    return logging.getLogger('wb2k')


def find_channel_id(slack: SlackClient, channel: str) -> str:
    """ TODO """
    channels = slack.api_call("channels.list")['channels']
    groups = slack.api_call("groups.list")['groups']
    channel_ids = [c['id'] for c in channels + groups if c['name'] == channel]

    if not channel_ids:
        raise ChannelNotFound(f"Couldn't find channel or group #{channel}")

    return channel_ids[0]


def member_joined_channel(
    slack: SlackClient,
    event: dict,
    channel: str,
    message: str,
    logger: logging.Logger
) -> str:
    """ TODO """
    event_channel = event['channel']
    user = slack.api_call('users.info', user=event['user'])['user']
    display_name = user['profile']['display_name']
    message = message.replace('{user}', f"<@{user['id']}>")

    if event_channel == channel:
        slack.rtm_send_message(event_channel, message)
        logger.info(f"Welcomed @{display_name} to #{channel}")

    return message


@click.command()
@click.option('-c', '--channel', envvar='WB2K_CHANNEL', default='general',
              show_default=True, metavar='CHANNEL',
              help='The channel to welcome users to.')
@click.option('-m', '--message', envvar='WB2K_MESSAGE',
              default='Welcome, {user}! :wave:', show_default=True,
              metavar='MESSAGE',
              help='The message to use when welcoming users. If present {user} '
              'will be replaced by a user mention.')
@click.option('-v', '--verbose', count=True, help='It goes to 11.')
@click.option('-r', '--retries', envvar='WB2K_RETRIES', default=8, type=(int), metavar='max_retries',
              help='The maximum number of times to attempt to reconnect on websocket connection errors')
@click.version_option()
def cli(channel: str, message: str, verbose: int, retries: int) -> None:
    """ TODO """
    logger = configure_logger(verbose)
    token = os.getenv('WB2K_TOKEN')
    slack = SlackClient(token=token)

    try:
        channel_id = find_channel_id(slack, channel)
        logger.debug(f"Found channel ID {channel_id} for #{channel}")
    except ChannelNotFound as exc:
        raise click.ClickException(exc)

    kwargs = {'channel': channel_id, 'message': message, 'logger': logger}
    app.handle('member_joined_channel', kwargs=kwargs)(member_joined_channel)

    try:
        app.run(connector=slack)
    except LayaboutError as exc:
        raise click.ClickException(exc)
