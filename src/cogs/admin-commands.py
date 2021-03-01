import sys

from discord.ext import commands
from utils import checks
from utils.confirmation import confirm

import discord


class AdminCommands(commands.Cog, name="Administration"):
    """A cog where all the server admin commands live"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='disconnect-vc', hidden=True)
    async def disconnect_vc(self, ctx):
        for vc in self.bot.voice_clients:
            if vc.guild == ctx.message.guild:
                return await vc.disconnect()

    @commands.command(hidden=True)
    @checks.requires_staff_role()
    async def kill(self, ctx):

        if await confirm(
                confirmation="Are you sure you want to kill me in cold blood?",
                ctx=ctx,
                bot=self.bot,
                abort_message="Thank you for sparing my life :)",
                success_message="goodbye :(",
                delete_messages=False
        ):
            await self.bot.logout()
            sys.exit()

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def status(self, ctx, *, message):
        if ctx.message.author.guild_permissions.administrator:
            await self.bot.change_presence(activity=discord.Game(name=message))

    @commands.command(name="throw_error")
    @checks.requires_staff_role()
    async def throw_error(self, ctx):
        raise Exception


def setup(bot):
    bot.add_cog(AdminCommands(bot))
