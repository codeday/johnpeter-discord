import random

from src.cogs import tournament


def generate_gamers(count):
    gamers = []
    while len(gamers) < count:
        gamer = random.randint(9999,999999)
        if gamer not in gamers:
            gamers.append(gamer)
    return gamers

def test_bracket(size=4):
    gamers = generate_gamers(size)
    games = {}
    games = tournament.makeGroups(players=gamers, groupSize=4)
    smallestGroup = int(len(gamers)/len(games))
    for group in games:
        assert len(group) >= smallestGroup

def test_brackets(min=2,max=256):
    for size in range(min,max):
        test_bracket(size)