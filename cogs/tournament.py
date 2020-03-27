import logging
import random
from os import getenv

import discord
from discord.ext import commands


class TournamentCog(commands.Cog, name="Tournament Helper"):
    """Creates Tournament Brackets!"""

    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.category = int(689585702350225435)  # off topic
        self.gamers = []  # initialize the epic people
        self.role_student = int(getenv('ROLE_STUDENT', 689214914010808359))  # student role
        self.join_message = None
        self.enabled = True

    @commands.command(aliases=['createtournament', 'tournament', 'tourney'])
    @commands.has_any_role('Global Staff')
    async def create_tournament(self, ctx: commands.context.Context, game_name: str, emoji=':trophy:'):
        """Creates a new tournament with the provided game name
            creates a VC and TC for the team as well as an invite message
            Does not use firebase, because tournaments will be short and I'm lazy
            Does not add any players, they must add themselves or be manually added separately
        """
        logging.debug("Starting tournament creation...")
        # Creates a new channel for the tournament
        self.game_name = game_name
        self.emoji = emoji
        self.overwrites = {
            ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            ctx.guild.get_role(self.role_student): discord.PermissionOverwrite(read_messages=False),
            ctx.guild.me: discord.PermissionOverwrite(read_messages=True)
        }
        self.tc = await ctx.guild.create_text_channel(name=f"{game_name.replace(' ', '-')}-tournament-📋",
                                                      overwrites=self.overwrites,
                                                      category=ctx.guild.get_channel(self.category),
                                                      topic=f"A channel for the {game_name} tournament!")
        self.vc = await ctx.guild.create_voice_channel(name=f"{game_name.replace(' ', '-')}-tournament-🔊",
                                                       overwrites=self.overwrites,
                                                       category=ctx.guild.get_channel(self.category),
                                                       topic=f"A channel for the {game_name} tournament!")
        # Creates and sends the join message
        self.join_message: discord.Message = await ctx.channel.send(
            make_join_message(game_name,emoji,self.gamers)
)
        await self.join_message.add_reaction('🏆')

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if payload.event_type == "REACTION_ADD" and payload.emoji.name == '🏆' and payload.message_id == self.join_message.id and self.enabled is True:
            if payload.user_id != self.bot.user.id:  # John must not become gamer
                self.gamers.append(payload.user_id)
            await payload.member.guild.get_channel(self.tc.id).set_permissions(payload.member,
                                                                               read_messages=True,
                                                                               manage_messages=True)
            await payload.member.guild.get_channel(self.vc.id).set_permissions(payload.member,
                                                                               read_messages=True)
            await self.join_message.edit(content=make_join_message(self.game_name, self.emoji, self.gamers))

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        if payload.event_type == "REACTION_REMOVE" and payload.emoji.name == '🏆' and payload.message_id == self.join_message.id and self.enabled is True:
            self.gamers.remove(payload.user_id)
            guild = self.bot.get_guild(payload.guild_id)
            member = guild.get_member(payload.user_id)
            await guild.get_channel(self.tc.id).set_permissions(member, read_messages=False)
            await guild.get_channel(self.vc.id).set_permissions(member, read_messages=False)
            await self.join_message.edit(content=make_join_message(self.game_name,self.emoji,self.gamers))

    @commands.command()
    @commands.has_any_role('Global Staff')
    async def start_round(self, ctx: commands.context.Context):
        self.enabled = False
        self.games = {}
        if len(self.gamers) % 4 != 0:
            for i in range(4 - (len(self.gamers) % 4)):  # Make sure it's a multiple of 4
                self.gamers.append(None)
        for tournament in range(int(len(self.gamers)/4)):
            rand_gamers = []
            for i in range(4):
                rand_gamer = random.choice(self.gamers)
                rand_gamers.append(rand_gamer)
                self.gamers.remove(rand_gamer)
            tc = await ctx.guild.create_text_channel(name=f"{self.game_name.replace(' ', '-')}-tournament-{tournament}📋",
                                                     overwrites=self.overwrites,
                                                     category=ctx.guild.get_channel(self.category),
                                                     topic=f"A channel for the {self.game_name} tournament!")
            vc = await ctx.guild.create_voice_channel(name=f"{self.game_name.replace(' ', '-')}-tournament-{tournament}🔊",
                                                      overwrites=self.overwrites,
                                                      category=ctx.guild.get_channel(self.category),
                                                      topic=f"A channel for the {self.game_name} tournament!")

            self.games[tc.id] = {
                'gamers': rand_gamers,
                'tc': tc,
                'vc': vc,
                'winner': None,
                'idx': tournament
            }

        for game in self.games:
            for gamer in self.games[game]['gamers']:
                if gamer != None:
                    await self.games[game]['tc'].set_permissions(ctx.guild.get_member(gamer),
                                                                 read_messages=True,
                                                                 manage_messages=True)
                    await self.games[game]['tc'].set_permissions(ctx.guild.get_member(gamer),
                                                                 read_messages=True)

            await ctx.guild.get_channel(self.games[game]['tc'].id).send(
                f'''Cowabunga, Gamers! :cowboy:
Welcome to the Game Tournament! Please join the associated voice channel. It is now time to fight your fellow comrades. When you are finished, please ping @/Global Staff in this channel with your final scores.
Game on! {''.join([f'<@{gamer}> 'for gamer in self.games[game]['gamers'] if gamer != None])}'''
            )
            await self.join_message.edit(content=make_running_message(self.game_name, self.games))
            await self.join_message.clear_reactions()

    @commands.command(hidden=True)
    @commands.has_any_role('Global Staff')
    async def report_winner(self, ctx: commands.context.Context, winner):
        winner_id = int(winner.replace('<','').replace('!','').replace('>','').replace('@',''))
        if winner_id in self.games[ctx.channel.id]['gamers']:
            self.gamers.append(winner_id)
            self.games[ctx.channel.id]['winner'] = winner_id
            await self.join_message.edit(content=make_running_message(self.game_name, self.games))


def setup(bot):
    bot.add_cog(TournamentCog(bot))

def make_join_message(game, emoji, gamers):
    msg = '''{} tournament:
Please react to this message with {} to join the tournament!
'''.format(game,emoji)
    if len(gamers) > 0:
        msg += f'''Currently participating - {len(gamers)}:
'''
        for gamer in gamers:
            msg += '''<@{}>
'''.format(gamer)
    return msg

def make_running_message(game,games):
    msg = f'''{game} Tournament:
Current matches:
'''
    for g in games:
        out = f'''Match {games[g]['idx']} - '''
        if games[g]['winner']:
            out += f'''Winner: <@{games[g]['winner']}>
'''
        else:
            out += '''In progress
'''
        msg += out
    return msg
#
# class Game:
#     def __init__(self,gamers, channel):
#         self.gamers = []
#         self.winner = None
#
#     def add_gamer(self, gamer):
#         self.gamers.append(gamer)
#
#     def set_winner(self, winner):
#         if winner in self.gamers:
#             self.winner = winner
#         else:
#             print('Improper gamer set to winner!')
#             return False