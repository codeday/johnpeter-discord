import asyncio
import glob
import io
import os
import urllib
from os import getenv, path, makedirs
from random import choice

import aiohttp
import discord
from discord.ext import commands
from urllib import parse


class FunCommands(commands.Cog, name="Fun"):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.random_channel = int(getenv("CHANNEL_RANDOM", 689534362760642676))
        self.mod_log = int(getenv("CHANNEL_MOD_LOG", 689216590297694211))
        names = {"zeke.mp3"}
        for name in names:
            url = f'https://f1.srnd.org/fun/pledge/{name}'
            urllib.request.urlretrieve(url, f'./audiofiles/{name}')

    @commands.command(name="crab", aliases=['crabrave', 'crab_rave', 'crab-rave'], hidden=True)
    async def crab(self, ctx, *, text = None):
        """Turns the text into a crab rave."""
        if ctx.channel.id == self.random_channel:
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
            # await self.bot.get_channel(self.mod_log).send(f"{ctx.author.mention} did crab rave with arguments '{text}'")
        else:
            await ctx.send("Sorry, please do that in #random")

    @commands.command(name="owo", hidden=True)
    async def owo(self, ctx):
        """owo"""
        if ctx.channel.id == self.random_channel:
            await ctx.send(f"owo what's {ctx.author.mention}")

    @commands.command(name="up-up-down-down-left-right-left-right-b-a-start", hidden=True)
    async def updownupdownleftrightleftrightbastart(self, ctx):
        """A lot of typing for nothing."""
        if ctx.channel.id == self.random_channel:
            await ctx.send("wow that's a long cheat code")

    @commands.command(name="pledge")
    async def pledge(self, ctx):
        """Recites the pledge in the currently-joined voice channel."""
        if ctx.message.author.voice is None:
            await ctx.send("Please join a voice channel")
        else:
            voice_channel = ctx.message.author.voice.channel
            channel = None
            if voice_channel != None:
                channel = voice_channel
                vc = await channel.connect()
                os.chdir("./audiofiles")
                people = []
                for file in glob.glob("*.mp3"):
                    people.append(file)
                person = choice(people)
                source = discord.FFmpegPCMAudio(f'{person}')
                player = vc.play(source)
                while vc.is_playing():
                    await asyncio.sleep(1)
                await vc.disconnect()


def setup(bot):
    bot.add_cog(FunCommands(bot))
