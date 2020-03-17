import discord
from discord.ext import commands


class TeamBuilderCog(commands.Cog, name="Team Builder Commands"):
    """Creates Teams!"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="Create a Team")
    def add_team(self, ctx, *, team_name, team_emoji):



def setup(bot):
    bot.add_cog(TeamBuilderCog(bot))
