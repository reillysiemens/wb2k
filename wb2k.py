import click

__author__ = "Reilly Tucker Siemens"
__email__ = "reilly@tuckersiemens.com"
__version__ = "0.2.0-what-did-you-expect"


@click.command()
@click.option("-v", "--verbose", count=True, help="It goes to 11.")
@click.version_option()
def cli(verbose: int) -> None:
    """ TODO """
    if verbose > 11:
        raise click.ClickException("It doesn't go beyond 11")
