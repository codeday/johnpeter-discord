import asyncio
import json
import os
import random
import re
import urllib
import urllib.request
from glob import glob
from os import getenv
from random import choice

import discord
from discord.ext import commands

from utils.cms import get_sponsor_intro, get_sponsor_audio
from utils.commands import only_random, require_vc, OnlyAllowedInChannels


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
    
    @commands.Cog.listener()
    async def on_message(self, message):

        msg = message.content

        manyAnimalsRegex = re.compile(f"{await self.bot.get_prefix(message)}(cat|dog)((?:n't)+)")
        match = manyAnimalsRegex.match(msg)
        if match:

            if message.channel.id != int(getenv("CHANNEL_RANDOM", 689534362760642676)): # hacky @only_random replacement
                await message.channel.send(f"You can only do that in <#{getenv('CHANNEL_RANDOM', 689534362760642676)}>")
                return

            animal,nts = match.group(1,2)

            animal_commands = ["cat","dog"]
            command_to_call = animal_commands[(animal_commands.index(animal) + nts.count("n't"))%2]
            await self.bot.get_command(command_to_call)(message.channel)

    @commands.command(name="cat",aliases=["kitten", "kitty", "catto"])
    @only_random
    async def cat(self, ctx):
        with urllib.request.urlopen("https://aws.random.cat/meow") as url:
            data = json.loads(url.read().decode())
            await ctx.send(data.get('file'))
    
    
    @commands.command(name="doggo",aliases=["dog", "puppy", "pupper"])
    @only_random
    async def doggo(self,ctx):
        with urllib.request.urlopen("https://dog.ceo/api/breeds/image/random") as url:
            data = json.loads(url.read().decode())
            await ctx.send(data.get('message'))

    @commands.command(name="floof", aliases=["floofer","floofo"])
    @only_random
    async def floof(self, ctx):
        await ctx.invoke(self.bot.get_command(random.choice(['doggo', 'cat'])))

    @commands.command(name="bird", aliases=["birb","birdy","birdie"])
    @only_random
    async def bird(self, ctx):
        with urllib.request.urlopen("https://some-random-api.ml/img/birb") as url:
            data = json.loads(url.read().decode())
            await ctx.send(data.get('link'))
                                           
    @commands.command(name ="fish", aliases=["cod", "codday", "phish"])
    @only_random
    async def fish(self, ctx):
        fish = ["https://tinyurl.com/s8zadryh", "https://tinyurl.com/v2xsewah", "https://tinyurl.com/hnmdr2we", "https://tinyurl.com/ypbcsa3u"]
        await ctx.send(random.choice(fish))

    @commands.command(name="triggered", aliases=["mad","angry"])
    @only_random
    async def triggered(self, ctx, arg):
    if arg:
        await ctx.send("https://some-random-api.ml/canvas/triggered?avatar={}".format(arg))
    else:
        await ctx.send("<:revoltLola:829824598178529311> Hey you didn't tell me an image URL!")

    @commands.command(name="owo")
    @only_random
    async def owo(self, ctx):
        """owo"""
        await ctx.send(f"owo what's {ctx.author.mention}?")

    @commands.command(name="uwu")
    @only_random
    async def uwu(self, ctx):
        """uwu"""
        await ctx.send(f"uwu what's {ctx.author.mention}?")

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
