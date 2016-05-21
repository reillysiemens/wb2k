# `wb2k`

Welcoming new folks to `#general` since `<insert-UNIX-timestamp-here>`.

## What's in the Box?

- Free Software: ISC License
- A bot
- A pony
- Just enough snark

## Features

- Utter disregard for the gravity of this situation.
- Basically no error handling of consequence.
- ~~One big, ugly function that does everything.~~ Some smaller functions that
  have a bunch of side effects.
- Silly help text.

## Quickstart

### Getting a Token
Stop. I know you're eager to run a `wb2k` of your very own, but you're gonna
need to [create a new bot]. Go ahead. Get yourself one. I'll wait.

Once you've got that bot (and its associated API token) you can install a
shiny, new `wb2k` with
```shell
pip install git+git://github.com/reillysiemens/wb2k.git
```

If you're not in a [virtualenv] you may need to use `pip` with `sudo`.

### Running the Darn Thing

To begin, set the `WB2K_TOKEN` environment variable with
```shell
export WB2K_TOKEN=xoxb-33323571738-Ssl8s5tYZtniftyVfNQQG5x3
```
No, that's not a real token. Yes, this environment variable **MUST** be set to
a valid token in order for `wb2k` to work.

Once `wb2k` is installed and the token is in place you can run it from the
command line like so
```shell
wb2k
```

### It Goes to 11
If you want to crank up the verbosity you could do something wild like
```shell
wb2k -v # -vv, -vvv, etc.
```

### There Are... Other Options?
Maybe you're a real daredevil and you want to welcome folks to a channel that
isn't `#general`. In that case just
```shell
wb2k -c some_random_channel
```

You can also define a `WB2K_CHANNEL` environment variable like
```shell
export WB2K_CHANNEL=some_random_channel
```
and that will work as well.

Do keep in mind that `wb2k` actually has to have access to
`#some_random_channel`. You can't just use it to snoop on previously
unknown or private channels.

### This Isn't What I Wanted

Still confused? Consult
```shell
wb2k --help
```
If `wb2k` can't help you, then ¯\\\_(ツ)_/¯

## Credits

This package was created with help from [Cookiecutter].

[create a new bot]: https://my.slack.com/services/new/bot
[virtualenv]: https://virtualenv.pypa.io/en/stable
[Cookiecutter]: https://github.com/audreyr/cookiecutter
