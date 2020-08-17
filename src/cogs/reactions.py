import random

import discord
from discord.ext import commands

from utils.confirmation import confirm


class ReactionCommands(commands.Cog, name="Reactions"):
    """A cog where all the reaction commands live"""
    # TODO: better docs for this

    def __init__(self, bot):
        self.bot = bot
        self.groupmsgs = {}


    @commands.command()
    @commands.has_any_role('Employee')
    async def reaction_groups(self, ctx: commands.Context, message_channel_id, message_id):
        message_channel_id = int(message_channel_id)
        message_id = int(message_id)
        channel = ctx.guild.get_channel(message_channel_id)
        message = await channel.fetch_message(message_id)
        roles = ctx.message.role_mentions
        if await confirm(f'Users reacting to message "{message.content}" will be randomly assigned to one of {len(roles)} groups', ctx, self.bot):
            self.groupmsgs[message_id] = roles

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if (
                payload.event_type == 'REACTION_ADD'
                and payload.message_id in self.groupmsgs
                and payload.user_id != self.bot.user.id
        ):
            guild = self.bot.get_guild(payload.guild_id)
            member = guild.get_member(payload.user_id)
            if not any(role in self.groupmsgs[payload.message_id] for role in member.roles):
                await member.add_roles(random.choice(self.groupmsgs[payload.message_id]))


def setup(bot):
    bot.add_cog(ReactionCommands(bot))
