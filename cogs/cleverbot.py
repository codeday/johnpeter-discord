import json
import os
import re

import requests
from discord.ext import commands

API_KEY = os.getenv('CLEVERBOT_API_KEY')

class CleverbotCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.states = {}

    @commands.Cog.listener()
    async def on_message(self, message):
        if str(type(message.channel)) is 'TextChannel' and message.channel.name is 'random' and re.search('^john (.+)$', re.IGNORECASE, message.text):
            state_id = str(message.author.id) + str(
                message.channel.name)  # each user/channel combo has unique state

            if state_id not in self.states:
                self.states[state_id] = None

            r = requests.get(
                url='http://www.cleverbot.com/getreply?key={}&input={}&cs={}'.format(API_KEY, input, self.states[state_id]),
                verify=False)
            msg_out = json.loads(r.text)['output']
            self.states[state_id] = json.loads(r.text)['cs']
            await message.channel.send(content=str(msg_out))


def setup(bot):
    bot.add_cog(CleverbotCog(bot))