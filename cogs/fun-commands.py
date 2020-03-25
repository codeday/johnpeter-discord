import io
from os import getenv

import aiohttp
import discord
from discord.ext import commands
from urllib import parse


class FunCommands(commands.Cog, name="Fun Commands"):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.random_channel = int(getenv("CHANNEL_RANDOM", 689534362760642676))
        self.mod_log = int(getenv("CHANNEL_MOD_LOG", 689216590297694211))

    @commands.command(aliases=['crabrave', 'crab_rave', 'crab-rave'], hidden=True)
    async def crab(self, ctx, *, text):
        if ctx.channel.id == self.random_channel:
            await ctx.message.delete()
            url = f'https://adventurous-damselfly.glitch.me/video/{parse.quote(text)}.mp4?style=classic'
            async with ctx.channel.typing():
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as resp:
                        if resp.status != 200:
                            return await ctx.send('Could not download file...')
                        data = io.BytesIO(await resp.read())
                        await ctx.send(file=discord.File(data, f'{text}.mp4'))
            await self.bot.get_channel(self.mod_log).send(f"{ctx.author.mention} did crab rave with arguments '{text}'")
        else:
            await ctx.send("Sorry, please do that in #random")


def setup(bot):
    bot.add_cog(FunCommands(bot))
