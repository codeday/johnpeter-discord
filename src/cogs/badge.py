import discord
from discord.ext import commands, tasks
import json
import requests
from math import ceil
from utils import checks
from utils.badges import grant
from utils.confirmation import confirm
from utils.paginated_send import paginated_send_multiline, paginate_reaction

BADGES_QUERY = """
{
  cms {
    badges {
      items {
        id
        name
        emoji
        description
        earnCriteria
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

    def get_badge(self, id):
        badges = [b for b in self.badges if (
            b['id'] == id or b['emoji'] == id)]
        if len(badges) > 0:
            return badges[0]
        return None

    async def send_list_badges(self, ctx, badges):
        # await paginated_send_multiline(
        #     ctx,
        #     "\n".join([f"{b['emoji']} **{b['name']}** (`{b['id']}`, {b['earnCriteria']}) {b['description']}"
        #                for b in badges]))
        all_badges = [f"{b['emoji']} **{b['name']}** (`{b['id']}`, {b['earnCriteria']}) {b['description']}"
                       for b in badges]
        

        def generate_badge_page_embed(badgelist, index, numPages, origlist):
            return discord.Embed.from_dict({
                "title": "Listing all badges",
                "description": "\n".join(badgelist),
                "footer": {
                    "icon_url": str(ctx.author.avatar_url),
                    "text": f"Page {1+index}/{numPages} | {len(origlist)} results | Searched by {ctx.author.name}#{ctx.author.discriminator}"
                }
            })
        
        perPage = 15
        pages = [{"content":"","embed":generate_badge_page_embed(
            badgelist=all_badges[i:i+perPage], 
            index=n,
            numPages=ceil(len(all_badges)/perPage),
            origlist=all_badges)
        } for n,i in enumerate(range(0, len(all_badges), perPage))]

        await paginate_reaction(pages, ctx)
        

    @tasks.loop(minutes=10)
    async def update_badges(self):
        print("updating badges")
        self.badges = self.gql(BADGES_QUERY)["cms"]["badges"]["items"]

    @commands.group(name="badge")
    async def snippet(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('Invalid badge command passed...')

    @snippet.command(name="refresh")
    @checks.requires_staff_role()
    async def refresh(self, ctx):
        self.badges = self.gql(BADGES_QUERY)["cms"]["badges"]["items"]

    @snippet.command(name='give')
    @checks.requires_staff_role()
    async def give(self, ctx, member: discord.Member, id):
        b = self.get_badge(id)
        if not b:
            await ctx.send("I haven't heard of that one.")
            await ctx.message.add_reaction('\N{THUMBS DOWN SIGN}')
        if b["earnCriteria"] != "bestowed":
            await ctx.send("I'm not giving those away for free!")
            await ctx.message.add_reaction('\N{THUMBS DOWN SIGN}')
            return
        if await grant(self.bot, member, id):
            await ctx.message.add_reaction('\N{THUMBS UP SIGN}')
        else:
            await ctx.message.add_reaction('\N{THUMBS DOWN SIGN}')

    @snippet.command(name='give_role')
    @checks.requires_staff_role()
    async def give_role(self, ctx, role: discord.Role, id):
        print(role)
        print(role.members)
        b = self.get_badge(id)
        if not b:
            await ctx.send("I haven't heard of that one.")
            await ctx.message.add_reaction('\N{THUMBS DOWN SIGN}')
        elif b["earnCriteria"] != "bestowed":
            await ctx.send("I'm not giving those away for free!")
            await ctx.message.add_reaction('\N{THUMBS DOWN SIGN}')
        elif await confirm(f'Are you sure, this will add a badge to {len(role.members)} person(s)', ctx, self.bot, ):
            await ctx.message.add_reaction('\N{THUMBS UP SIGN}')
            for member in role.members:
                if not (await grant(self.bot, member, id)):
                    await ctx.message.remove_reaction('\N{THUMBS UP SIGN}', self.bot.user)
                    await ctx.message.add_reaction('\N{THUMBS DOWN SIGN}')
        else:
            await ctx.message.add_reaction('\N{THUMBS DOWN SIGN}')

    @snippet.command(name='list')
    async def list(self, ctx):
        await self.send_list_badges(ctx, self.badges)

    @snippet.command(name='info')
    async def info(self, ctx, id):
        b = self.get_badge(id)
        if not b:
            await ctx.send("Never heard of it!")
            return
        await ctx.send(f"{b['emoji']} **{b['name']}**: {b['description']}")

    @snippet.command(name='inspect')
    async def inspect(self, ctx, member: discord.Member):
        query = f"""{{
            account {{
                getUser(where: {{ discordId: "{member.id}"}}, fresh: true) {{
                    badges {{
                        details {{
                            id
                            name
                            emoji
                            description
                            earnCriteria
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

        await self.send_list_badges(ctx, [b['details'] for b in badges])


def setup(bot):
    bot.add_cog(BadgeCog(bot))
