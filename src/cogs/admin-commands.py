import sys

from discord.ext import commands
from utils import checks
import discord

from asyncio import TimeoutError

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

        msg = await ctx.send(f"Are you sure you want to kill me in cold blood? React with \N{WHITE HEAVY CHECK MARK} to confirm!")

        while True:
            try:
                check = lambda reaction, user: reaction.message.id == msg.id and user.id == ctx.author.id

                reaction, _ = await self.bot.wait_for('reaction_add', timeout=60, check=check)

                if reaction.emoji == "\N{WHITE HEAVY CHECK MARK}":
                    break
            except TimeoutError:
                await msg.edit("Kill cancelled :)")
                return

        await ctx.send("goodbye :(")
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
