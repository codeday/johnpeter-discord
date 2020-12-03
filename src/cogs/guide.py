from discord.ext import commands, tasks
import json
import requests
from dateutil import parser
from pytz import timezone
from utils.badges import grant

from db.models import session_creator, ReadGuide

GUIDES_QUERY = """
{
  cms {
    strings(where:{key_contains:"bot.guide"}) {
      items {
        key
        value
      }
    }
  }
}
"""

# noinspection PyPackageRequirements


class GuideCog(commands.Cog, name="Guide"):
    def __init__(self, bot):
        self.bot = bot
        self.update_guides.start()
        self.already_notified_cache = {}
        self.guides = {}

    def cog_unload(self):
        self.update_guides.cancel()

    @commands.Cog.listener()
    async def on_message(self, message):
        if not(self.was_notified(message.channel, message.author)) and str(message.channel.id) in self.guides:
            await message.author.send(self.guides[str(message.channel.id)])
            self.set_notified(message.channel, message.author)
            # TODO(@tylermenezes) improve this
            if message.channel.id == "689541918178279589":
                await grant(self.bot, message.author, "help-desk")

    @tasks.loop(minutes=30)
    async def update_guides(self):
        print("updating guides")
        result = requests.post("https://graph.codeday.org/",
                               json={"query": GUIDES_QUERY})
        data = json.loads(result.text)
        items = data["data"]["cms"]["strings"]["items"]
        self.guides = {item["key"].split(".")[-1]: item["value"]
                       for item in items}

    def was_notified(self, channel, user):
        if channel.id in self.already_notified_cache and user.id in self.already_notified_cache[channel.id]:
            return True

        session = session_creator()
        query = session.query(ReadGuide).filter_by(
            channel_id=str(channel.id),
            user_id=str(user.id),
        )
        resp = query.all()
        if len(resp) > 0:
            self.cache_notified(channel, user)
            return True

        return False

    def cache_notified(self, channel, user):
        if not (channel.id in self.already_notified_cache):
            self.already_notified_cache[channel.id] = []
        self.already_notified_cache[channel.id].append(user.id)

    def set_notified(self, channel, user):
        session = session_creator()
        session.add(
            ReadGuide(
                channel_id=str(channel.id),
                user_id=str(user.id),
            )
        )
        session.commit()
        session.close()
        self.cache_notified(channel, user)
        pass


def setup(bot):
    bot.add_cog(GuideCog(bot))
