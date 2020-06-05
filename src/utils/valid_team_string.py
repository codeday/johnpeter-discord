def valid_team_string(string):
    blacklist = [
        '<',
        '>'
    ]
    return any([char in string for char in blacklist])


def make_valid_team_string(string):
    blacklist = [
        '<',
        '>'
    ]
    for char in blacklist:
        string = string.replace(char,'')
    return string
