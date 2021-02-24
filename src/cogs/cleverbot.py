# noinspection PyPackageRequirements
import json
import os

import discord
import requests

# noinspection PyPackageRequirements
from discord.ext import commands

API_KEY = os.getenv("CLEVERBOT_API_KEY")


class CleverbotCog(commands.Cog, name="Cleverbot"):
    def __init__(self, bot):
        self.bot = bot
        self.states = {}
        self.dmstates = {}
        self.dminit = []

    @commands.command(name="john", aliases=["John"], hidden=True)
    async def john(self, ctx, *, message=None):

        if message is None:
            await ctx.send("Sorry, what was that?")

        if (
            isinstance(ctx.channel,discord.channel.TextChannel)
            and ctx.channel.name == "random"
        ):
            # each channel has unique state
            state_id = ctx.channel.name

            if state_id not in self.states:
                self.states[state_id] = None
            r = requests.get(
                url=f"http://www.cleverbot.com/getreply?key={API_KEY}&input={message}&cs={self.states[state_id]}",
                verify=False,
            )
            msg_out = json.loads(r.text)["output"]
            self.states[state_id] = json.loads(r.text)["cs"]
            await ctx.reply(content=str(msg_out), replied_user=False)
        if (
            isinstance(ctx.channel, discord.channel.DMChannel)
            and ctx.author is not ctx.channel.me
        ):
            if not(ctx.author.id in self.dminit):
                await ctx.send(
                    "Hey, let me tell you a secret. ***I'm actually a robot.*** I respond to messages by AI.\n\n"
                    + "**If you need help, please message a staff member. (Someone with the Staff role.)**"
                )
                self.dminit.append(ctx.author.id)
                return
            state_id = str(ctx.channel.id)  # each channel has unique state

            if state_id not in self.dmstates:
                self.dmstates[state_id] = None
            r = requests.get(
                url=f"http://www.cleverbot.com/getreply?key={API_KEY}&input={message}&cs={self.dmstates[state_id]}",
                verify=False,
            )
            msg_out = json.loads(r.text)["output"]
            self.dmstates[state_id] = json.loads(r.text)["cs"]
            await ctx.send(content=str(msg_out))


def setup(bot):
    bot.add_cog(CleverbotCog(bot))
