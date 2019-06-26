import pytest
from click.testing import CliRunner

from wb2k import cli


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.mark.parametrize("verbosity", ["-" + "v" * n for n in range(1, 12)])
def test_it_goes_up_to_11(runner, verbosity):
    """ wb2k's verbose option can be repeated up to 11 times. """
    result = runner.invoke(cli, [verbosity])
    assert result.exit_code == 0


def test_it_doesnt_go_beyond_11(runner):
    """ wb2k's verbose option cannot be repeated more than 11 times. """
    result = runner.invoke(cli, ["-vvvvvvvvvvvv"])
    assert result.output == "Error: It doesn't go beyond 11\n"
    assert result.exit_code == 1
