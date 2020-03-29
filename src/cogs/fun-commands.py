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
        self.people = []
        for file in glob.glob("*.mp3"):
            print(file)
            self.people.append(file)

    @commands.command(name="crab", aliases=['crabrave', 'crab_rave', 'crab-rave'])
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

    @commands.command(name="owo")
    async def owo(self, ctx):
        """owo"""
        if ctx.channel.id == self.random_channel:
            await ctx.send(f"owo what's {ctx.author.mention}")

    @commands.command(name="up-down-up-down-left-right-left-right-b-a-start", hidden=True, aliases=['updownupdownleftrightleftrightbastart'])
    async def updownupdownleftrightleftrightbastart(self, ctx):
        """A lot of typing for nothing."""
        if ctx.channel.id == self.random_channel:
            await ctx.send("wow that's a long cheat code")
        else:
            await ctx.send("Sorry, please do that in #random")

    @commands.command(name="pledge", aliases=['pledgeofsrnd', 'pledge-of-srnd'])
    async def pledge(self, ctx):
        """Recites the pledge in the currently-joined voice channel."""
        retval = os.getcwd()
        if ctx.message.author.voice is None:
            await ctx.send("Please join a voice channel")
        else:
            channel = ctx.message.author.voice.channel
            if channel != None:
                vc = await channel.connect()
                os.chdir("./cache/pledge")
                people = []
                for file in glob.glob("*.mp3"):
                    print(file)
                    people.append(file)
                person = choice(people)
                source = discord.FFmpegPCMAudio(f'{person}')
                player = vc.play(source)
                while vc.is_playing():
                    await asyncio.sleep(1)
                await vc.disconnect()
        os.chdir(retval)


    @commands.command()
    async def disconnectvc(self, ctx):
        for vc in self.bot.voice_clients:
            if vc.guild == ctx.message.guild:
                return await vc.disconnect()


def setup(bot):
    bot.add_cog(FunCommands(bot))
    names = {"zeke.mp3"}
    for name in names:
        url = f'https://f1.srnd.org/fun/pledge/{name}'
        urllib.request.urlretrieve(url, f'./cache/pledge/{name}')
