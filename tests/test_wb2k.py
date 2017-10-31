from wb2k.__main__ import bail


def test_bail():
    msg_type = 'fatal'
    color = 'red'
    text = "It doesn't go beyond 11."

    given = bail(msg_type, color, text)
    expected = "\x1b[31mfatal\x1b[0m: It doesn't go beyond 11."

    assert given == expected
