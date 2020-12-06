import discord
from discord.ext import commands, tasks
import json
import requests
from utils import checks
from utils.badges import grant
from os import getenv

# noinspection PyPackageRequirements


class BadgeCog(commands.Cog, name="Guide"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='gold')
    @checks.requires_gold_role()
    async def give(self, ctx, member: discord.Member):
        role = ctx.guild.get_role(int(getenv("ROLE_GOLD")))
        if not role:
            await ctx.message.add_reaction('\N{THUMBS DOWN SIGN}')
            await ctx.send("I can't find the gold role!")
            return

        if await grant(self.bot, member, "gold"):
            await ctx.message.add_reaction('\N{THUMBS UP SIGN}')
            await member.add_roles(role)
        else:
            await ctx.message.add_reaction('\N{THUMBS DOWN SIGN}')
            await ctx.send("I can't! (Have they linked their account?)")


def setup(bot):
    bot.add_cog(BadgeCog(bot))
