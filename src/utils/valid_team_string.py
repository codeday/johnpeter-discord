def valid_team_string(string):
    blacklist = [
        '<',
        '>'
    ]
    return any([char in string for char in blacklist])