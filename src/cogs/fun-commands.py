import asyncio
import io
import os
import random
import re
import urllib
from glob import glob
from os import getenv
from random import choice
from urllib import parse, request
import urllib.request,json
import aiohttp
import discord
from discord.ext import commands

from utils.cms import get_sponsor_intro, get_sponsor_audio
from utils.commands import only_random, require_vc
import json


class FunCommands(commands.Cog, name="Fun"):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.random_channel = int(getenv("CHANNEL_RANDOM", 689534362760642676))
        self.mod_log = int(getenv("CHANNEL_MOD_LOG", 689216590297694211))
        # Downloads mp3 files
        urls = get_sponsor_audio()
        if not os.path.isdir("./cache/sponsorships/"):
            os.makedirs("./cache/sponsorships/")
        for url in urls:
            file_name = re.sub("(h.*\/)+", "", url)
            urllib.request.urlretrieve(url, f"./cache/sponsorships/{file_name}")

        file_name = re.sub("(h.*\/)+", "", get_sponsor_intro())
        urllib.request.urlretrieve(get_sponsor_intro(), f"./cache/{file_name}")

        self.sponsorships = []
        for file in glob("./cache/sponsorships/*.mp3"):
            print(file)
            self.sponsorships.append(file)

    @commands.command(name="cat",aliases=["kitten"])
    @only_random
    async def cat(self, ctx):
        with urllib.request.urlopen("https://aws.random.cat/meow") as url:
            data = json.loads(url.read().decode())
            await ctx.send(data.get('file'))
    
    @commands.command(name="doggo",aliases=["dog"])
    @only_random
    async def doggo(self,ctx):
        with urllib.request.urlopen("https://dog.ceo/api/breeds/image/random") as url:
            data = json.loads(url.read().decode())
            await ctx.send(data.get('message'))

    @commands.command(name="owo")
    @only_random
    async def owo(self, ctx):
        """owo"""
        await ctx.send(f"owo what's {ctx.author.mention}")

    @commands.command(
        name="up-down-up-down-left-right-left-right-b-a-start",
        hidden=True,
        aliases=["updownupdownleftrightleftrightbastart"],
    )
    @only_random
    async def updownupdownleftrightleftrightbastart(
        self, ctx,
    ):
        """A lot of typing for nothing."""
        await ctx.send("wow that's a long cheat code. You win 20 CodeCoin!!")

    @commands.command(pass_context=True, aliases=["disconnect"])
    async def disconnectvc(self, ctx):
        await ctx.message.delete()
        vc = ctx.message.guild.voice_client
        if vc is None:
            await ctx.send("You silly, I'm not in any VCs right now.")
        else:
            await vc.disconnect()

    @commands.command(
        name="sponsorship",
        aliases=[
            "sponsor",
            "sponsormessage",
            "sponsor-message",
            "sponsor_message",
            "sponsors",
        ],
    )
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
