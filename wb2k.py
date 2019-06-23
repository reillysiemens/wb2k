import click

__author__ = "Reilly Tucker Siemens"
__email__ = "reilly@tuckersiemens.com"
__version__ = "0.2.0-what-did-you-expect"


@click.command()
@click.option(
    "-c",
    "--channel",
    envvar="WB2K_CHANNEL",
    default="general",
    show_default=True,
    metavar="CHANNEL",
    help="The channel to welcome users to.",
)
@click.option(
    "-m",
    "--message",
    envvar="WB2K_MESSAGE",
    default="Welcome, {user}! :wave:",
    show_default=True,
    metavar="MESSAGE",
    help=(
        "The message to use when welcoming users. If present "
        "{user} will be replaced by a user mention."
    ),
)
@click.option("-v", "--verbose", count=True, help="It goes to 11.")
@click.option(
    "-r",
    "--retries",
    envvar="WB2K_RETRIES",
    default=8,
    type=(int),
    metavar="max_retries",
    help=(
        "The maximum number of times to attempt to reconnect on "
        "websocket connection errors"
    ),
)
@click.version_option()
def cli(channel: str, message: str, verbose: int, retries: int) -> None:
    raise click.ClickException(click.style("It doesn't work.", fg="red"))
