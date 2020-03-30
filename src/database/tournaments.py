from database.rounds import Round


class Tournament(object):
    def __init__(self, game_name, tc_id, join_message_id, players_per_game=4, gamers=[], rounds=[]):
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
        self.current_round = None

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

    def next_round(self, bot=None):
        if not self.rounds:  # If no round already exists create one
            self.rounds = [Round(0,self.gamers)]
        elif bot:
            for game in self.rounds[-1].games:
                game.delete_channel(bot)
        self.current_round = self.rounds[-1]
        with self.current_round as r:  # Get latest round
            if r.round_complete():
                self.rounds.append(Round(len(self.rounds),r.winners()))
                if bot:
                    bot.get_channel(self.tc_id).send(f'Round {len(self.rounds)} has begun!')
                return True
            else:
                return False

    @staticmethod
    def make_join_message(game_name):
        return f'Please react to this message with :trophy: to join the {game_name} Tournament!'

    def update_join_message(self):
        out = self.make_join_message(self.game_name)
        out += f'\n{len(self.gamers)} gamers currently registered'
        if len(self.gamers) < 50:
            out += ':'
            for gamer in self.gamers:
                out += f'\n <@{gamer}>'
        return out

    def add_gamer(self,gamer):
        if not self.rounds:  # don't add someone if tourney already started
            self.gamers.append(gamer)
            return True
        else:
            return False

    def remove_gamer(self,gamer):
        if not self.rounds:  # don't remove someone if tourney already started
            self.gamers.remove(gamer)
            return True
        else:
            return False

    async def join_message(self, bot):
        return await bot.get_channel(self.tc_id).fetch_message(self.join_message_id)
