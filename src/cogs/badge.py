import asyncio
import json
from math import ceil

import discord
import requests
from discord.ext import commands, tasks

from utils import checks
from utils.badges import grant, choose_cult
from utils.commands import only_random
from utils.confirmation import confirm
from utils.paginated_send import paginate_reaction

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
        grantPermissionOverrideIDs
      }
    }
  }
}
"""


# noinspection PyPackageRequirements


class BadgeCog(commands.Cog, name="Badge"):
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

    async def send_list_badges(self, ctx, badges, **kwargs):

        if kwargs.get("filter", "") == "":
            all_badges = [f"{b['emoji']} **{b['name']}** (`{b['id']}`, {b['earnCriteria']}) {b['description']}"
                    for b in badges]
        else:
            fexpr = kwargs.get("filter", "")

            filter_lambda = lambda fexpr, badge: any([fexpr in badge[attr] for attr in ("emoji", "name", "id")])
            all_badges = [f"{b['emoji']} **{b['name']}** (`{b['id']}`, {b['earnCriteria']}) {b['description']}"
                    for b in badges if filter_lambda(fexpr, b)]

        # await paginated_send_multiline(
        #     ctx,
        #     "\n".join([f"{b['emoji']} **{b['name']}** (`{b['id']}`, {b['earnCriteria']}) {b['description']}"
        #                for b in badges]))
        

        def generate_badge_page_embed(badgelist, index, numPages, origlist, title):
            return discord.Embed.from_dict({
                "title": title,
                "description": "\n".join(badgelist),
                "footer": {
                    "icon_url": str(ctx.author.avatar_url),
                    "text": f"Page {1 + index}/{numPages} | {len(origlist)} results | Searched by {ctx.author.name}#{ctx.author.discriminator}"
                }
            })

        perPage = 15
        
        title = kwargs.get("title", "Listing all badges")

        pages = [{"content": "", "embed": generate_badge_page_embed(
            badgelist=all_badges[i:i + perPage],
            index=n,
            numPages=ceil(len(all_badges) / perPage),
            origlist=all_badges,
            title=title)
                  } for n, i in enumerate(range(0, len(all_badges), perPage))]

        await paginate_reaction(pages, ctx)

    @tasks.loop(minutes=10)
    async def update_badges(self):
        print("updating badges")
        self.badges = self.gql(BADGES_QUERY)["cms"]["badges"]["items"]

    @commands.group(name="badge")
    async def badge(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('Invalid badge command passed...')

    @badge.command(name="refresh")
    @checks.requires_staff_role()
    async def refresh(self, ctx):
        self.badges = self.gql(BADGES_QUERY)["cms"]["badges"]["items"]

    @badge.command(name='give')
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
        if await grant(member, id):
            await ctx.message.add_reaction('\N{THUMBS UP SIGN}')
        else:
            await ctx.message.add_reaction('\N{THUMBS DOWN SIGN}')

    @badge.command(name='give_role')
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
                if not (await grant(member, id)):
                    await ctx.message.remove_reaction('\N{THUMBS UP SIGN}', self.bot.user)
                    await ctx.message.add_reaction('\N{THUMBS DOWN SIGN}')
        else:
            await ctx.message.add_reaction('\N{THUMBS DOWN SIGN}')

    @badge.command(name='list')
    async def list(self, ctx):
        await self.send_list_badges(ctx, self.badges)
    
    @badge.command(name='search')
    async def search(self, ctx, fexpr):
        await self.send_list_badges(ctx, self.badges, filter=fexpr)

    @badge.command(name='info')
    async def info(self, ctx, id):
        b = self.get_badge(id)
        if not b:
            await ctx.send("Never heard of it!")
            return
        await ctx.send(f"{b['emoji']} **{b['name']}**: {b['description']}")

    @badge.command(name='inspect')
    async def inspect(self, ctx, member: discord.Member = None):

        if member is None: member = ctx.author

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

        await self.send_list_badges(ctx, [b['details'] for b in badges], title=f"Listing {member.name}'s badges")

    @badge.command()
    @only_random
    async def cult(self, ctx):
        query = f"""{{
            account {{
                getUser(where: {{ discordId: "{ctx.author.id}"}}, fresh: true) {{
                    badges {{
                        id
                    }}
                }}
            }}
        }}
        """
        result = self.gql(query)
        if not result["account"]["getUser"]:
            await ctx.send("You haven't linked your CodeDay account.")
            return
        badges = result["account"]["getUser"]["badges"]
        if any((badge['id'] == 'pizza') for badge in badges):
            await ctx.send("You cannot forsake your blood vow to :pizza:")
            return
        if any((badge['id'] == 'turtle') for badge in badges):
            await ctx.send("You cannot forsake your blood vow to :turtle:")
            return

        initiation_message = await ctx.send("Welcome to the CodeDay Badge Cult Initiation.\nChoose which cult to which will you pledge your life: :turtle: "
                                            "or :pizza:.")

        reaction1 = await initiation_message.add_reaction('\N{TURTLE}')
        reaction2 = await initiation_message.add_reaction('\N{Slice of Pizza}')

        def check(reaction, user):
            return user == ctx.author and reaction.message.id == initiation_message.id

        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
            badge_id = ""
            if reaction.emoji == '\N{TURTLE}':
                badge_id = "turtle"
            if reaction.emoji == '\N{Slice of Pizza}':
                badge_id = "pizza"
            response = await choose_cult(ctx, ctx.author, badge_id)
            if not response:
                await initiation_message.delete()
            else:
                await initiation_message.clear_reactions()
                await initiation_message.edit(content=f"Welcome to the :{badge_id}: cult! We accept your blood offering!")
        except asyncio.TimeoutError:
            await initiation_message.delete()
        else:
            await ctx.message.add_reaction('👍')


def setup(bot):
    bot.add_cog(BadgeCog(bot))
