import re

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
from utils.cms import get_sponsor_intro, get_sponsor_audio


class FunCommands(commands.Cog, name="Fun"):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.random_channel = int(getenv("CHANNEL_RANDOM", 689534362760642676))
        self.mod_log = int(getenv("CHANNEL_MOD_LOG", 689216590297694211))
        # Downloads mp3 files
        names = {"zeke.mp3"}
        for name in names:
            url = f'https://f1.srnd.org/fun/pledge/{name}'
            urllib.request.urlretrieve(url, f'./cache/pledge/{name}')
        urls = get_sponsor_audio()
        for url in urls:
            file_name = re.sub('(h.*\/)+', "", url)
            urllib.request.urlretrieve(url, f"./cache/sponsorships/{file_name}")
        file_name = re.sub('(h.*\/)+', "", get_sponsor_intro())
        urllib.request.urlretrieve(get_sponsor_intro(), f"./cache/{file_name}")

        self.people = []
        for file in glob("./cache/pledge/*.mp3"):
            print(file)
            self.people.append(file)
        self.sponsorships = []
        for file in glob("./cache/sponsorships/*.mp3"):
            print(file)
            self.sponsorships.append(file)

    @commands.command(name="crab", aliases=['crabrave', 'crab_rave', 'crab-rave'])
    @only_random
    async def crab(self, ctx, *, text=None):
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

    @commands.command(name="up-down-up-down-left-right-left-right-b-a-start", hidden=True,
                      aliases=['updownupdownleftrightleftrightbastart'])
    @only_random
    async def updownupdownleftrightleftrightbastart(self, ctx):
        """A lot of typing for nothing."""
        await ctx.send("wow that's a long cheat code")

    @commands.command(name="pledge", aliases=['pledgeofsrnd', 'pledge-of-srnd'])
    @require_vc
    async def pledge(self, ctx):
        """Recites the pledge in the currently-joined voice channel."""
        await ctx.message.delete()
        retval = os.getcwd()
        vc = await ctx.message.author.voice.channel.connect()
        try:
            file = choice(self.people)
            source = discord.FFmpegPCMAudio(f"{file}")
            player = vc.play(source)
            while vc.is_playing():
                await asyncio.sleep(1)
        finally:
            await vc.disconnect()

    @commands.command(pass_context=True)
    async def disconnectvc(self, ctx):
        await ctx.message.delete()
        server = ctx.message.guild.voice_client
        await server.disconnect()

    @commands.command(name="sponsorship", aliases=['sponsor', 'sponsormessage', 'sponsor-message', 'sponsor_message'])
    @require_vc
    async def sponsorship(self, ctx):
        """Says a message from a sponsor."""
        await ctx.message.delete()
        retval = os.getcwd()
        vc = await ctx.message.author.voice.channel.connect()
        try:
            file = choice(self.sponsorships)
            intro = discord.FFmpegPCMAudio(f"./cache/sponsor-intro.mp3")
            sponsor = discord.FFmpegPCMAudio(f"{file}")
            player = vc.play(intro)
            while vc.is_playing():
                await asyncio.sleep(1)
            player = vc.play(sponsor)
            while vc.is_playing():
                await asyncio.sleep(1)
        finally:
            await vc.disconnect()


def setup(bot):
    bot.add_cog(FunCommands(bot))
