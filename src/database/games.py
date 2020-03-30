import random
from os import getenv

import discord


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

    def vote(self, gamer, winner, bot):  # Vote for round winner
        if winner in self.gamers:
            self.votes[gamer] = winner
            if all(self.votes[vote] == winner for vote in self.votes):
                self.set_winner(winner)
            return True
        else:
            return False

    def set_winner(self, winner):
        self.winner = winner

    async def create_channel(self, ctx, game_name, category):
        overwrites = {
            ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            ctx.guild.get_role(int(getenv('ROLE_STUDENT', 689214914010808359))): discord.PermissionOverwrite(read_messages=False),
            ctx.guild.me: discord.PermissionOverwrite(read_messages=True)
        }
        tc = await ctx.guild.create_text_channel(name=f"game-{self.idx}📋",
                                                 overwrites=overwrites,
                                                 category=ctx.guild.get_channel(category),
                                                 topic=f"A channel for the {game_name} tournament!")
        vc = await ctx.guild.create_voice_channel(name=f"game-{self.idx}🔊",
                                                  overwrites=overwrites,
                                                  category=ctx.guild.get_channel(category),
                                                  topic=f"A channel for the {game_name} tournament!")
        for gamer in self.gamers:
            await tc.set_permissions(ctx.guild.get_member(gamer),
                                     read_messages=True,
                                     send_messages=True)
            await vc.set_permissions(ctx.guild.get_member(gamer),
                                     read_messages=True,
                                     send_messages=True)
        await tc.send(
            f'''Cowabunga, Gamers! :cowboy:
        Welcome to the Game Tournament! Please join the associated voice channel.\
         It is now time to fight your fellow comrades. When you are finished, \
         please use the command `~tournament winner`.
        Game on! {''.join([f'<@{gamer}> ' for gamer in self.gamers])}'''
        )
        await tc.send(
            f'''<@{random.choice(self.gamers)}> has been randomly selected as the game host.\
             Please send them a link to your steam profile to begin the HIGH OCTANE GAMING ACTION! :race_car:'''
        )
        self.tc_id = tc.id
        self.vc_id = vc.id
        return tc, vc

    async def delete_channel(self, bot):
        await bot.get_channel(self.tc_id).delete()
        await bot.get_channel(self.vc_id).delete()
