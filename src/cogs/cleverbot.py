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

    @commands.Cog.listener()
    async def on_message(self, message):
        if (
            type(message.channel) == discord.channel.TextChannel
            and message.channel.name == "random"
            and message.content.lower().startswith("john ")
        ):
            # each channel has unique state
            state_id = str(message.channel.name)

            if state_id not in self.states:
                self.states[state_id] = None
            input = message.content.split(" ", 1)[1]
            r = requests.get(
                url=f"http://www.cleverbot.com/getreply?key={API_KEY}&input={input}&cs={self.states[state_id]}",
                verify=False,
            )
            msg_out = json.loads(r.text)["output"]
            self.states[state_id] = json.loads(r.text)["cs"]
            await message.channel.send(content=str(msg_out))
        if (
            type(message.channel) == discord.channel.DMChannel
            and message.author is not message.channel.me
        ):
            if not(message.author.id in self.dminit):
                await message.channel.send(
                    "Hey, let me tell you a secret. ***I'm actually a robot.*** I respond to messages by AI.\n\n"
                    + "**If you need help, please message a staff member. (Someone with a red name.)**"
                )
                self.dminit.append(message.author.id)
                return
            state_id = str(message.channel.id)  # each channel has unique state

            if state_id not in self.dmstates:
                self.dmstates[state_id] = None
            # input = message.content.split(' ', 1)[1]
            input = message.content
            r = requests.get(
                url="http://www.cleverbot.com/getreply?key={}&input={}&cs={}".format(
                    API_KEY, input, self.dmstates[state_id]
                ),
                verify=False,
            )
            msg_out = json.loads(r.text)["output"]
            self.dmstates[state_id] = json.loads(r.text)["cs"]
            await message.channel.send(content=str(msg_out))


def setup(bot):
    bot.add_cog(CleverbotCog(bot))
