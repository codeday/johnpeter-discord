import sys

from discord.ext import commands


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
    @commands.has_any_role('Employee')
    async def kill(self, ctx):
        await \
            ctx.send("goodbye :(")
        sys.exit()

    @commands.command(name="throw_error")
    @commands.has_any_role('Employee')
    async def throw_error(self, ctx):
        raise Exception


def setup(bot):
    bot.add_cog(AdminCommands(bot))
