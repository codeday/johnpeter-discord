import discord
from discord.ext import commands, tasks
import json
import requests
from utils import checks
from utils.badges import grant

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

    def gql(self, query):
        result = requests.post("https://graph.codeday.org/",
                               json={"query": query})
        data = json.loads(result.text)
        if "errors" in data:
            print(data["errors"])
        return data["data"]

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
        if (await grant(self.bot, member, id)):
            await ctx.message.add_reaction('\N{THUMBS UP SIGN}')
        else:
            await ctx.message.add_reaction('\N{THUMBS DOWN SIGN}')

    @snippet.command(name='list')
    async def list(self, ctx):
        await ctx.send("\n".join([f"{b['emoji']} **{b['name']}** (`{b['id']}`)" for b in self.badges]))

    @snippet.command(name='info')
    async def info(self, ctx, id):
        badges = [b for b in self.badges if (
            b['id'] == id or b['emoji'] == id)]
        if len(badges) == 0:
            await ctx.send("Never heard of it!")
            return
        b = badges[0]
        await ctx.send(f"{b['emoji']} **{b['name']}**: {b['description']}")

    @snippet.command(name='inspect')
    async def inspect(self, ctx, member: discord.Member):
        query = f"""{{
            account {{
                getUser(where: {{ discordId: "{member.id}"}}) {{
                    badges {{
                        details {{
                            id
                            name
                            emoji
                            description
                        }}
                    }}
                }}
            }}
        }}
        """
        result = self.gql(query)
        if not result["account"]["getUser"]:
            await ctx.send("This user hasn't linked their CodeDay account.")
            return

        badges = result["account"]["getUser"]["badges"]

        await ctx.send("\n".join([f"{b['details']['emoji']} **{b['details']['name']}** (`{b['details']['id']}`)"
                                  for b in badges]))


def setup(bot):
    bot.add_cog(BadgeCog(bot))
