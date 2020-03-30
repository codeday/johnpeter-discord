from database.rounds import Round


class Tournament(object):
    def __init__(self, game_name, tc_id, join_message_id, players_per_game, gamers=[], rounds=[]):
        """
        :param game_name: The game name
        :param tc_id: The ID of the text channel the tournament was created in
        :param join_message_id: The ID of the message that users react to to participate in the tournament
        :param players_per_game: the maximum amount of players for each matchup
        :param gamers: A list of participants by member ID
        :param rounds: A list of Round objects
        """
        self.game_name = game_name
        self.tc_id = tc_id
        self.join_message_id = join_message_id
        self.players_per_game = players_per_game
        self.gamers = gamers
        self.rounds = rounds

    @staticmethod
    def from_dict(source):
        tournament = Tournament(game_name=source['game_name'], tc_id=source['tc_id'],
                                join_message_id=source['join_message_id'], players_per_game=source['players_per_game'],
                                gamers=source['gamers'], rounds=[Round.from_dict(round) for round in source['rounds']])
        return tournament

    def to_dict(self):
        dest = {
            'game_name': self.game_name,
            'tc_id': self.tc_id,
            'join_message_id': self.join_message_id,
            'players_per_game': self.players_per_game,
            'gamers': self.gamers,
            'rounds': [round.to_dict() for round in self.rounds]
        }

        return dest

    def next_round(self):
        if not self.rounds:  # If no round already exists create one
            self.rounds = [Round(0,self.gamers)]
        with round as self.rounds[-1]:  # Get latest round
            if round.round_complete():
                self.rounds.append(Round(len(self.rounds),round.winners()))
            else:
                return False
