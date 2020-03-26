import logging
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

    @commands.command(aliases=['create_tournament', 'createtournament', 'tournament', 'tourney'])
    @commands.has_any_role('Global Staff', 'Staff')
    async def add_team(self, ctx: commands.context.Context, game_name: str, emoji=':trophy:'):
        """Creates a new tournament with the provided game name
            creates a VC and TC for the team as well as an invite message
            Does not use firebase, because tournaments will be short and I'm lazy
            Does not add any players, they must add themselves or be manually added separately
        """
        logging.debug("Starting tournament creation...")
        # Creates a new channel for the tournament
        self.game_name = game_name
        self.emoji = emoji
        overwrites = {
            ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            ctx.guild.get_role(self.role_student): discord.PermissionOverwrite(read_messages=False),
            ctx.guild.me: discord.PermissionOverwrite(read_messages=True)
        }
        self.tc = await ctx.guild.create_text_channel(name=f"{game_name.replace(' ', '-')}-tournament-📋",
                                                      overwrites=overwrites,
                                                      category=ctx.guild.get_channel(self.category),
                                                      topic=f"A channel for the {game_name} tournament!")
        self.vc = await ctx.guild.create_voice_channel(name=f"{game_name.replace(' ', '-')}-tournament-🔊",
                                                       overwrites=overwrites,
                                                       category=ctx.guild.get_channel(self.category),
                                                       topic=f"A channel for the {game_name} tournament!")
        # Creates and sends the join message
        self.join_message: discord.Message = await ctx.channel.send(
            make_join_message(game_name,emoji,self.gamers)
)
        await self.join_message.add_reaction('🏆')

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if payload.event_type == "REACTION_ADD" and payload.emoji.name == '🏆' and payload.message_id == self.join_message.id:
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
        if payload.event_type == "REACTION_REMOVE" and payload.emoji.name == '🏆' and payload.message_id == self.join_message.id:
            self.gamers.remove(payload.user_id)
            guild = self.bot.get_guild(payload.guild_id)
            member = guild.get_member(payload.user_id)
            await guild.get_channel(self.tc.id).set_permissions(member, read_messages=False)
            await guild.get_channel(self.vc.id).set_permissions(member, read_messages=False)
            await self.join_message.edit(content=make_join_message(self.game_name,self.emoji,self.gamers))
def setup(bot):
    bot.add_cog(TournamentCog(bot))

def make_join_message(game, emoji, gamers):
    msg = '''{} tournament:
Please react to this message with {} to join the tournament!
'''.format(game,emoji)
    if len(gamers) > 0:
        msg += '''Currently participating:
'''
        for gamer in gamers:
            msg += '''<@{}>
'''.format(gamer)
    return msg