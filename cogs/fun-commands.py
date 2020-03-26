import io
from os import getenv, path, makedirs

import aiohttp
import discord
from discord.ext import commands
from urllib import parse
import json
import typing


class FunCommands(commands.Cog, name="Fun Commands"):
    def __init__(self, bot):
        self.cache_folder = "./cacherave/"
        self.cache_index = "./cacherave.json"
        self.bot: commands.Bot = bot
        self.random_channel = int(getenv("CHANNEL_RANDOM", 689534362760642676))
        self.mod_log = int(getenv("CHANNEL_MOD_LOG", 689216590297694211))
        try:
            with open(self.cache_index) as file:
                self.cache_data = json.load(file)
                print("Cache Found!")
        except:
            self.cache_data = {}
            print("Cache data not found!")

    @commands.command(aliases=['crabrave', 'crab_rave', 'crab-rave'], hidden=True)
    async def crab(self, ctx, *, text):
        if ctx.channel.id == self.random_channel:
            await ctx.message.delete()

            async with ctx.channel.typing():
                resp = await self.get_with_cache(text)
                if not resp:
                    return await ctx.send('Could not download file...')
                await ctx.send(file=discord.File(resp, f'{text}.mp4'))
            # await self.bot.get_channel(self.mod_log).send(f"{ctx.author.mention} did crab rave with arguments '{text}'")
        else:
            await ctx.send("Sorry, please do that in #random")

        with open(self.cache_index, 'w') as fp:
            json.dump(self.cache_data, fp)

    async def get_with_cache(self, string) -> typing.Union[io.BytesIO, bool]:
        """
            Will take a requests string and return a file from cache if it exists, or from the interent if not.
            Also saves new files to disk, keeping last 1000
        """
        if not path.exists(self.cache_folder):
            makedirs(self.cache_folder)

        if string in self.cache_data:
            print("Using from cache")
            with open(self.cache_data[string]["file"], "rb") as output_file:
                self.cache_data[string]["usages"] += 1
                return io.BytesIO(output_file.read())
        else:
            print("Downloading...")
            url = f'https://adventurous-damselfly.glitch.me/video/{parse.quote(string)}.mp4?style=classic'
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status != 200:
                        return False
                    with open(f"{self.cache_folder}{string}.mp4", "bw+") as output_file:
                        output_file.write(await resp.read())
                        self.cache_data[string] = {
                            "file": f"{self.cache_folder}{string}.mp4",
                            "usages": 1
                        }
                    return io.BytesIO(await resp.read())


def setup(bot):
    bot.add_cog(FunCommands(bot))
