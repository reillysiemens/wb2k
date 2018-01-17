import os
import logging

import click
from slackclient import SlackClient

from layabout import setup_logging, run

__author__ = 'Reilly Tucker Siemens'
__email__ = 'reilly@tuckersiemens.com'
__version__ = '0.2.0-what-did-you-expect'


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
    # Due to some unfortunate limitations in the Slack RTM API
    # (https://api.slack.com/rtm#formatting_messages) message formatting is
    # limited to basic formatting.

    if verbose > 11:
        sys.exit(bail('fatal', 'red', "It doesn't go beyond 11"))

    # Get our logging in order.
    logger = logging.getLogger(__name__)
    setup_logging(verbose)

    # Make sure we have an API token.
    api_token = os.environ.get('WB2K_TOKEN')
    if not api_token:
        sys.exit(bail('fatal', 'red', 'WB2K_TOKEN envvar undefined'))

    sc = SlackClient(api_token)

    run(
        sc=sc,
        channel=channel,
        message=message,
        retries=retries,
        logger=logger
    )

if __name__ == '__main__':
    cli()
