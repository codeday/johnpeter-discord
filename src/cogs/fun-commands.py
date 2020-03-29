import aiohttp
import asyncio
import discord
import io
import os
import urllib

from discord.ext import commands
from glob import glob
from os import getenv, path, makedirs
from random import choice
from urllib import parse

from utils.commands import only_random, require_vc


class FunCommands(commands.Cog, name="Fun"):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.random_channel = int(getenv("CHANNEL_RANDOM", 689534362760642676))
        self.mod_log = int(getenv("CHANNEL_MOD_LOG", 689216590297694211))
        self.people = []
        for file in glob("*.mp3"):
            print(file)
            self.people.append(file)

    @commands.command(name="crab", aliases=['crabrave', 'crab_rave', 'crab-rave'])
    @only_random
    async def crab(self, ctx, *, text = None):
        """Turns the text into a crab rave."""
        await ctx.message.delete()
        async with ctx.channel.typing():
            print("Downloading...")
            url = f'https://adventurous-damselfly.glitch.me/video/{parse.quote(text)}.mp4?style=classic'
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status != 200:
                        return False
                    resp = io.BytesIO(await resp.read())
            await ctx.send(file=discord.File(resp, f'{text}.mp4'))

    @commands.command(name="owo")
    @only_random
    async def owo(self, ctx):
        """owo"""
        await ctx.send(f"owo what's {ctx.author.mention}")

    @commands.command(name="up-down-up-down-left-right-left-right-b-a-start", hidden=True, aliases=['updownupdownleftrightleftrightbastart'])
    @only_random
    async def updownupdownleftrightleftrightbastart(self, ctx):
        """A lot of typing for nothing."""
        await ctx.send("wow that's a long cheat code")

    @commands.command(name="pledge", aliases=['pledgeofsrnd', 'pledge-of-srnd'])
    @require_vc
    async def pledge(self, ctx):
        """Recites the pledge in the currently-joined voice channel."""
        retval = os.getcwd()
        vc = await ctx.message.author.voice.channel.connect()
        try:
            people = []
            for file in glob("./cache/pledge/*.mp3"):
                people.append(file)
            person = choice(people)
            source = discord.FFmpegPCMAudio(f'{person}')
            player = vc.play(source)
            while vc.is_playing():
                await asyncio.sleep(1)
        finally:
            await vc.disconnect()



def setup(bot):
    bot.add_cog(FunCommands(bot))
    names = {"zeke.mp3"}
    for name in names:
        url = f'https://f1.srnd.org/fun/pledge/{name}'
        urllib.request.urlretrieve(url, f'./cache/pledge/{name}')
