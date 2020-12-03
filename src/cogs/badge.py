import discord
from discord.ext import commands, tasks
import json
from jwt import encode
import time
import requests
from os import getenv
from utils import checks

BADGES_QUERY = """
{
  cms {
    badges {
      items {
        id
        name
        emoji
        description
      }
    }
  }
}
"""

# noinspection PyPackageRequirements


class BadgeCog(commands.Cog, name="Guide"):
    def __init__(self, bot):
        self.bot = bot
        self.update_badges.start()
        self.badges = []

    def cog_unload(self):
        self.update_badges.cancel()

    def gql_token(self):
        secret = getenv("GQL_ACCOUNT_SECRET")
        message = {
            "scopes": "write:users",
            "exp": int(time.time()) + (60*60*24)
        }
        return encode(message, secret, algorithm='HS256').decode("utf-8")

    def gql(self, query):
        result = requests.post("https://graph.codeday.org/",
                               json={"query": query},
                               headers={"Authorization": f"Bearer {self.gql_token()}"})
        data = json.loads(result.text)
        if "errors" in data:
            print(data["errors"])
        return data["data"]

    def get_username(self, member):
        query = f"""{{
            account {{
                getUser(where: {{ discordId: "{member.id}" }}) {{
                    username
                }}
            }}
        }}"""
        user = self.gql(query)["account"]["getUser"]
        if user:
            return user["username"]
        return None

    def grant_badge(self, username, id):
        query = f"""mutation {{
            account {{
                grantBadge(username: "{username}", badge: {{ id: "{id}" }})
            }}
        }}"""

        self.gql(query)

    async def a_update(self, member):
        channel = await self.bot.fetch_channel(int(getenv("CHANNEL_A_UPDATE")))
        await channel.send(f"a~update <@{member.id}>")

    @tasks.loop(minutes=10)
    async def update_badges(self):
        print("updating badges")
        self.badges = self.gql(BADGES_QUERY)["cms"]["badges"]["items"]

    @commands.group(name="badge")
    async def snippet(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('Invalid badge command passed...')

    @snippet.command(name='give')
    @checks.requires_staff_role()
    async def give(self, ctx, member: discord.Member, id):
        username = self.get_username(member)
        if not username:
            ctx.channel.send(
                f"<@{member.id}> hasn't linked their CodeDay account O:<")
            return

        self.grant_badge(username, id)
        await self.a_update(member)
        await ctx.message.add_reaction('\N{THUMBS UP SIGN}')

    @snippet.command(name='list')
    async def list(self, ctx):
        await ctx.send("\n".join([f"{b['emoji']} **{b['name']}** (`{b['id']}``)" for b in self.badges]))

    @snippet.command(name='info')
    async def info(self, ctx, id):
        badges = [b for b in self.badges if (
            b['id'] == id or b['emoji'] == id)]
        if len(badges) == 0:
            await ctx.send("Never heard of it!")
            return
        b = badges[0]
        await ctx.send(f"{b['emoji']} **{b['name']}**: {b['description']}")


def setup(bot):
    bot.add_cog(BadgeCog(bot))
