import random


def chunk(list, n):
    """Breaks a list into chunks of size n."""
    return [list[i:i + n] for i in range(0, len(list), n)]


def balance_groups(groups):
    """Balances a list of lists, so they are roughly equally sized."""
    numPlayers = sum([len(group) for group in groups])
    minGroupSize = int(numPlayers / len(groups))
    groupsArr = list(enumerate(groups))
    for i, group in groupsArr:
        while (len(group) < minGroupSize):
            for j, groupSteal in groupsArr:
                if (i != j) and len(groupSteal) > minGroupSize:
                    group.append(groupSteal.pop())
    return [group for group in groups]


def make_groups(players, groupSize):
    """Makes even-ish groups of size groupSize and return an array of the players."""
    random.shuffle(players)
    if len(players) == 1:
        return []

    groups = chunk(players, groupSize)
    if len(groups) == 1:
        return groups

    return balance_groups(groups)
