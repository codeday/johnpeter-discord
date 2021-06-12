# noinspection PyPackageRequirements
import datetime
import json
import os

import re

import requests
from dateutil import parser
from discord import AllowedMentions
# noinspection PyPackageRequirements
from discord.ext import commands, tasks
from pytz import timezone

ROLE_NOTIFY_EVENT = os.getenv("ROLE_NOTIFY_EVENT")
CHANNEL_EVENT_ANNOUNCE = int(os.getenv("CHANNEL_EVENT_ANNOUNCE"))
TZ = timezone("America/Los_Angeles")
TZNAME = "Pacific"
TZ2 = timezone("America/New_York")
TZ2NAME = "Eastern"


class EventsCog(commands.Cog, name="Events"):
    def __init__(self, bot):
        self.events = []
        self.already_notified = []
        self.bot = bot
        self.update_events.start()
        self.check_daily.start()
        self.event_check.start()

    def cog_unload(self):
        self.update_events.cancel()
        self.check_daily.cancel()
        self.event_check.cancel()

    def make_query(self):
        after = datetime.datetime.now(tz=TZ).replace(
            hour=3, minute=0, second=0)
        before = after + datetime.timedelta(days=1)
        return f"""
            query {{
                calendar {{
                    events(after: "{after.isoformat()}", before: "{before.isoformat()}", format: DISCORD) {{
                        id
                        start
                        title
                        description
                        location
                    }}
                }}
            }}
        """

    def format_start(self, start, short=False):
        start_1 = f"{start.astimezone(TZ).strftime('%-I:%M %p')} {TZNAME}"
        start_2 = f"{start.astimezone(TZ2).strftime('%-I:%M %p')} {TZ2NAME}"
        start_3 = f"{start.strftime('%H:%M')} GMT"
        if short:
            return f"{start_1} / {start_3}"
        else:
            return f"{start_1} / {start_2} / {start_3}"

    @tasks.loop(minutes=30)
    async def update_events(self):
        print("updating events")
        result = requests.post("https://graph.codeday.org/",
                               json={"query": self.make_query()})
        data = json.loads(result.text)
        self.events = data["data"]["calendar"]["events"]
        for event in self.events:
            event["start"] = parser.parse(
                event["start"]).replace(tzinfo=timezone('UTC'))

    @tasks.loop(seconds=60.0)
    async def check_daily(self):
        print("checking for daily post")
        now = datetime.datetime.now(tz=TZ)
        if now.hour == 9 and now.minute == 0:
            event_strs = [
                f"· {self.format_start(e['start'], True)} — **{e['title']}** <{e['location']}>"
                for e in self.events]
            event_list = "\n".join(event_strs)
            if (len(event_strs) > 0):
                msg = f":date: **__Events today__**:\n<@&{ROLE_NOTIFY_EVENT}>\n\n{event_list}"
                channel = await self.bot.fetch_channel(CHANNEL_EVENT_ANNOUNCE)
                await channel.send(msg[0:2000], allowed_mentions=AllowedMentions(roles=True))

    @tasks.loop(seconds=60.0)
    async def event_check(self):
        print("checking for event")
        now = datetime.datetime.now(tz=timezone('UTC'))
        soon = now + datetime.timedelta(minutes=10)
        events_soon = [event for event in self.events
                       if event["start"] > now and event["start"] < soon and not(event["id"] in self.already_notified)]
        for event in events_soon:
            self.already_notified.append(event["id"])
            description = event['description']

            msg = f"**Starting soon: {event['title']}** ({self.format_start(event['start'])})"
            if event['location']:
                msg += f"\n<{event['location']}>"
            msg += f"\n<@&{ROLE_NOTIFY_EVENT}>"
            if description and len(description) > 0:
                msg += f"\n{description}"
            channel = await self.bot.fetch_channel(CHANNEL_EVENT_ANNOUNCE)
            await channel.send(msg, allowed_mentions=AllowedMentions(roles=True))


def setup(bot):
    bot.add_cog(EventsCog(bot))
