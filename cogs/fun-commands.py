import io
import aiohttp
import discord
from discord.ext import commands
from urllib import parse


class FunCommands(commands.Cog, name="Fun Commands"):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.command(aliases=['crabrave', 'crab_rave', 'crab-rave'], hidden=True)
    async def crab(self, ctx, *, text):
        url = f'https://adventurous-damselfly.glitch.me/video/{parse.quote(text)}.mp4?style=classic'
        async with ctx.channel.typing():
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status != 200:
                        return await ctx.send('Could not download file...')
                    data = io.BytesIO(await resp.read())
                    await ctx.send(file=discord.File(data, f'{text}.mp4'))


def setup(bot):
    bot.add_cog(FunCommands(bot))
