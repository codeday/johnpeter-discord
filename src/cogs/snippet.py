import discord
from discord.ext import commands, tasks
import json
import requests
from utils import checks

GUIDES_QUERY = """
{
  cms {
    strings(where:{key_contains:"bot.snippet"}) {
      items {
        key
        value
      }
    }
  }
}
"""

# noinspection PyPackageRequirements


class SnippetCog(commands.Cog, name="Snippet"):
    def __init__(self, bot):
        self.bot = bot
        self.update_snippets.start()
        self.snippets = {}

    def cog_unload(self):
        self.update_snippets.cancel()

    @tasks.loop(minutes=10)
    async def update_snippets(self):
        print("updating snippets")
        result = requests.post("https://graph.codeday.org/",
                               json={"query": GUIDES_QUERY})
        data = json.loads(result.text)
        items = data["data"]["cms"]["strings"]["items"]
        self.snippets = {item["key"].split(".")[-1]: item["value"]
                         for item in items}

    @commands.group(name="snippet")
    @checks.requires_staff_role()
    async def snippet(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('Invalid snippet command passed...')

    @snippet.command(name='send')
    @checks.requires_staff_role()
    async def send(self, ctx, member: discord.Member, id):
        if not(id in self.snippets):
            await ctx.send('No such snippet!')
            return
        await member.send(self.snippets[id])
        await ctx.message.add_reaction('\N{THUMBS UP SIGN}')

    @snippet.command(name='preview')
    @checks.requires_staff_role()
    async def preview(self, ctx, id):
        if not(id in self.snippets):
            await ctx.send('No such snippet!')
            return
        await ctx.send(self.snippets[id])

    @snippet.command(name='list')
    @checks.requires_staff_role()
    async def list(self, ctx):
        await ctx.send("```" + "\n".join([f"- {k}" for k in self.snippets.keys()]) + "```")


def setup(bot):
    bot.add_cog(SnippetCog(bot))
