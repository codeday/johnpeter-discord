class Game(object):
    def __init__(self, idx, gamers, tc_id=None, vc_id=None, votes=None, voting_message_id=None, winner=None):
        """
        :param idx: The index number of the game
        :param gamers: a list of all the participants, by user ID
        :param tc_id: The ID of the text channel for the game
        :param vc_id: The ID of the voice channel for the game
        :param votes: a dictionary of who voted for who
        :param voting_message_id: the ID of the message used to display votes
        :param winner: the ID of the voted (or set) winner of the game
        """
        self.idx = idx
        self.gamers = gamers
        self.tc_id = tc_id
        self.vc_id = vc_id
        self.votes = votes
        self.voting_message_id = voting_message_id
        self.winner = winner

        if self.votes is None:
            self.votes = {gamer: None for gamer in gamers}

    @staticmethod
    def from_dict(source):
        game = Game(idx=source['idx'], gamers=source['gamers'], tc_id=source['tc_id'], vc_id=source['vc_id'])

        if 'votes' in source:
            game.votes = source['votes']

        if 'voting_message' in source:
            game.voting_message_id = source['voting_message_id']

        if 'winner' in source:
            game.winner = source['winner']

        return game

    def to_dict(self):
        dest = {
            'idx': self.idx,
            'gamers': self.gamers,
            'tc_id': self.tc_id,
            'vc_id': self.vc_id
        }

        if self.votes:
            dest['votes'] = self.votes

        if self.voting_message_id:
            dest['voting_message_id'] = self.voting_message_id

        if self.winner:
            dest['winner'] = self.winner

        return dest

    def generate_voting_message(self):
        out = f'''Please use `~tournament winner @username` to report the winner for this round.
Winner will not be finalized until unanimous agreement from participants.
Votes cast:
'''
        for gamer in self.votes:
            out += f'''
        <@{gamer}> - '''
            if self.votes[gamer] is None:
                out += 'Not yet voted'
            else:
                out += f'<@{self.votes[gamer]}>'

        return out[:1999]  # Just in case, discord limits message to 2,000 characters

    def vote(self, gamer, winner):  # Vote for round winner
        if winner in self.gamers:
            self.votes[gamer] = winner
            return True
        else:
            return False

    def create_channel(self, ctx, game_name, category, overwrites):
        tc = await ctx.guild.create_text_channel(name=f"game-{self.idx}📋",
                                                 overwrites=overwrites,
                                                 category=ctx.guild.get_channel(category),
                                                 topic=f"A channel for the {game_name} tournament!")
        vc = await ctx.guild.create_voice_channel(name=f"game-{self.idx}🔊",
                                                  overwrites=overwrites,
                                                  category=ctx.guild.get_channel(category),
                                                  topic=f"A channel for the {game_name} tournament!")
        self.tc_id = tc.id
        self.vc_id = vc.id
        return tc, vc
