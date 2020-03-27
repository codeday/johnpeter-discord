import asyncio
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
        self.games = {}
        self.status_message = None


    @commands.command(hidden=True, aliases=['createtournament', 'tournament', 'tourney'])
    @commands.has_any_role('Tournament Master')
    async def create_tournament(self, ctx: commands.context.Context, game_name: str, emoji=':trophy:'):
        await ctx.message.delete()
        self.gamers = []
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

    @commands.command(hidden=True)
    @commands.has_any_role('Tournament Master')
    async def start_round(self, ctx: commands.context.Context, groupSize = 4):
        await ctx.message.delete()
        self.enabled = False
        groups = makeGroups(self.gamers, groupSize)
        self.games = await create_games(groups=groups, ctx=ctx, game_name=self.game_name, overwrites=self.overwrites, category=self.category)
        for game in self.games:
            for gamer in self.games[game]['gamers']:
                if gamer is not None:
                    await self.games[game]['tc'].set_permissions(ctx.guild.get_member(gamer),
                                                                 read_messages=True,
                                                                 manage_messages=True)
                    await self.games[game]['tc'].set_permissions(ctx.guild.get_member(gamer),
                                                                 read_messages=True)

            await ctx.guild.get_channel(self.games[game]['tc'].id).send(
                f'''Cowabunga, Gamers! :cowboy:
Welcome to the Game Tournament! Please join the associated voice channel. It is now time to fight your fellow comrades. When you are finished, please use the command j!report_winner with who won.
Game on! {''.join([f'<@{gamer}> 'for gamer in self.games[game]['gamers'] if gamer != None])}'''
            )
            await ctx.guild.get_channel(self.games[game]['tc'].id).send(
                f'''<@{random.choice(self.games[game]['gamers'])}> has been randomly selected as the game host. Please send them a link to your steam profile so y'all can begin the HIGH OCTANE GAMING ACTION! :race_car:'''
            )
            await self.join_message.edit(content=make_running_message(self.game_name, self.games))

            await self.join_message.clear_reactions()
            self.status_message = await self.tc.send(make_running_message(self.game_name, self.games))
            await self.status_message.pin()
            self.gamers = []


    @commands.command(hidden=True)
    @commands.has_any_role('Tournament Master')
    async def announce_winner(self, ctx: commands.context.Context, winner):
        winner_id = int(winner.replace('<','').replace('!','').replace('>','').replace('@',''))
        if winner_id in self.games[ctx.channel.id]['gamers']:
            self.gamers.append(winner_id)
            self.games[ctx.channel.id]['winner'] = winner_id
            await self.join_message.edit(content=make_running_message(self.game_name, self.games))
            await self.status_message.edit(content=make_running_message(self.game_name,self.games))
            await self.tc.send(f'Congratulations to <@{winner_id}> for winning game {self.games[ctx.channel.id]["idx"]}!')
            await ctx.channel.send('Thank you for playing!')
            await asyncio.sleep(5)
            await self.games[ctx.channel.id]['tc'].delete()
            await self.games[ctx.channel.id]['vc'].delete()


    @commands.command(hidden=True)
    async def report_winner(self, ctx: commands.context.Context, winner=None):
        if ctx.channel.id in self.games:
            game = self.games[ctx.channel.id]
        else:
            await ctx.channel.send('''I'm sorry, but this is not a known channel for a round. Please retry your command in a channel for a tournament match.''')
            return
        try:
            winner_id = int(winner.replace('<','').replace('!','').replace('>','').replace('@',''))
        except:
            await ctx.channel.send('''I'm sorry, I don't know who you're talking about! Please use the command as follows, mentioning the person who won:
            j!report_winner <@689549152275005513>''')
            return
        if winner_id in game['gamers']:
            self.games[ctx.channel.id]['votes'][ctx.author.id] = winner_id
            game = self.games[ctx.channel.id]
            if game['voting_message'] is None:
                self.games[ctx.channel.id]['voting_message'] = await ctx.channel.send(make_voting_message(game))
            else:
                await self.games[ctx.channel.id]['voting_message'].edit(content=make_voting_message(game))
            if all(vote == game['votes'][ctx.author.id] for vote in game['votes'].values()):
                await self.announce_winner(ctx=ctx, winner=winner)
        else:
            await ctx.channel.send('''I'm sorry, I don't know who you're talking about! Please use the command as follows, mentioning the person who won:
j!report_winner <@689549152275005513>''')


    @commands.command(hidden=True)
    @commands.has_any_role('Tournament Master')
    async def delete_tournament(self, ctx: commands.context.Context):
        await ctx.message.delete()
        await (await ctx.send('Ok, I deleted the tournament')).delete(delay=5)
        await self.tc.delete()
        await self.vc.delete()
        for game in self.games:
            try:
                await self.games[game]['tc'].delete()
            except:
                pass
            try:
                await self.games[game]['vc'].delete()
            except:
                pass


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


async def create_games(groups, ctx, game_name='Gaming', overwrites=None, category=None):
    games = {}
    for idx, group in enumerate(groups):
        tc = await ctx.guild.create_text_channel(name=f"{game_name.replace(' ', '-')}-tournament-{idx}📋",
                                                 overwrites=overwrites,
                                                 category=ctx.guild.get_channel(category),
                                                 topic=f"A channel for the {game_name} tournament!")
        vc = await ctx.guild.create_voice_channel(name=f"{game_name.replace(' ', '-')}-tournament-{idx}🔊",
                                                  overwrites=overwrites,
                                                  category=ctx.guild.get_channel(category),
                                                  topic=f"A channel for the {game_name} tournament!")
        games[tc.id] = {
            'gamers': group,
            'tc': tc,
            'vc': vc,
            'winner': None,
            'idx': idx,
            'voting_message': None,
            'votes': {gamer: None for gamer in group}
        }
    return games


def chunk(list, n):
    """Breaks a list into chunks of size n."""
    return [ list[i:i+n] for i in range(0, len(list), n)]

def balanceGroups(groups):
    """Balances a list of lists, so they are roughly equally sized."""
    numPlayers = sum([len(group) for group in groups])
    minGroupSize = int(numPlayers/len(groups))
    groupsArr = list(enumerate(groups))
    for i, group in groupsArr:
        while(len(group) < minGroupSize):
            for j, groupSteal in groupsArr:
                if (i != j) and len(groupSteal) > minGroupSize:
                    group.append(groupSteal.pop())
    return [group for group in groups]

def makeGroups(players, groupSize):
    """Makes even-ish groups of size groupSize and return an array of the players."""
    if len(players) == 1:
        return []

    groups = chunk(players, groupSize)
    if len(groups) == 1:
        return groups

    return balanceGroups(groups)


def make_voting_message(game):
    out = f'''Winner for round {game['idx']}:
'''
    for gamer in game['gamers']:
        out += f'''
<@{gamer}> - '''
        if game['votes'][gamer] is None:
            out += 'Not yet voted'
        else:
            out += f'<@{game["votes"][gamer]}>'

    return out
