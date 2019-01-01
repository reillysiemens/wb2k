import logging
import os

import click
from slackclient import SlackClient

from layabout import Layabout, LayaboutError

__author__ = 'Reilly Tucker Siemens'
__email__ = 'reilly@tuckersiemens.com'
__version__ = '0.3.0-spanish-inquisition'


class ChannelNotFound(Exception):
    """ A channel was not found. """


def configure_logger(verbose: int) -> logging.Logger:
    """
    Configure logging.

    Note:
        This disables ``urllib3`` logging for all but critical events.

    Args:
        verbose: The verbosity level. Anything greater than zero results in
            debug logging.

    Returns:
        A logger.
    """
    logging.basicConfig(
        level=logging.INFO if verbose < 1 else logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt='[%Y-%m-%d %H:%M:%S %z]'
    )
    logging.getLogger('urllib3').setLevel(logging.CRITICAL)  # Quiet, requests.
    return logging.getLogger('wb2k')


def find_channel_id(slack: SlackClient, channel: str) -> str:
    """
    Given the name of a channel, find its Slack ID.

    Args:
        slack: A connected instance of :obj:`slackclient.SlackClient`.
        channel: The name of a Slack channel.

    Returns:
        The Slack ID for the ``channel``.
    """
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
    """
    A Layabout handler for ``member_joined_channel`` events.

    Args:
        slack: A connected instance of :obj:`slackclient.SlackClient`.
        event: The ``member_joined_channel`` event.
        channel: The ID of the channel to respond to.
        message: The message to send in response to the event.
        logger: A logger.

    Returns:
        The message sent to the ``channel``.
    """
    event_channel = event['channel']
    user = slack.api_call('users.info', user=event['user'])['user']
    display_name = user['profile']['display_name']
    message = message.replace('{user}', f"<@{user['id']}>")

    if event_channel == channel:
        slack.rtm_send_message(event_channel, message)
        logger.info(f"Welcomed @{display_name} to #{channel}")

    return message


@click.command(help='A tool for welcoming new folks to a Slack channel.')
@click.option('-c', '--channel', envvar='WB2K_CHANNEL', default='general',
              show_default=True, metavar='CHANNEL',
              help='The channel to welcome users to.')
@click.option('-m', '--message', envvar='WB2K_MESSAGE',
              default='Welcome, {user}! :wave:', show_default=True,
              metavar='MESSAGE',
              help='The message to use when welcoming users. If present, '
              '{user} will be replaced by a user mention.')
@click.option('-v', '--verbose', count=True, help='It goes to 11.')
@click.option('-r', '--retries', envvar='WB2K_RETRIES', default=8, type=(int),
              metavar='max_retries', help='The maximum number of times to '
              'attempt to reconnect on websocket connection errors')
@click.version_option()
def cli(channel: str, message: str, verbose: int, retries: int) -> None:
    """
    The CLI entry point for wb2k.

    Args:
        channel: The channel to welcome users to.
        message: The message to use when welcoming users. If present, {user}
            will be replaced by a user mention.
        verbose: It goes to 11.
        retries: The maximum number of times to attempt to reconnect on
            websocket connection errors.

    Raises:
        :obj:`click.ClickException`: If an error occurs.
    """
    if verbose > 11:
        raise click.ClickException("It doesn't go beyond 11")

    logger = configure_logger(verbose)
    token = os.getenv('WB2K_TOKEN')
    slack = SlackClient(token=token)
    app = Layabout()

    try:
        channel_id = find_channel_id(slack, channel)
        logger.debug(f"Found channel ID {channel_id} for #{channel}")
    except ChannelNotFound as exc:
        raise click.ClickException(exc)

    kwargs = {'channel': channel_id, 'message': message, 'logger': logger}
    app.handle('member_joined_channel', kwargs=kwargs)(member_joined_channel)

    try:
        app.run(connector=slack, retries=retries)
    except LayaboutError as exc:
        raise click.ClickException(exc)
