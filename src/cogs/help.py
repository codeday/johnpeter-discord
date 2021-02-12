from typing import Optional

from discord.ext import commands
from discord.utils import get
import discord

def create_embed(title=None, description=None, author=None, fields=None, image=None, thumbnail=None, color=discord.Color.teal()):
    if title:
        embed = discord.Embed(title=title, color=color)
    else:
        embed = discord.Embed(color=color)
    if description:
        embed.description = description
    if author:
        embed.set_author(name="For " + author.name, icon_url=author.avatar_url)
    if fields:
        for field in fields:
            embed.add_field(name=field[0], value=field[1], inline=field[2] if len(field) > 2 else False)
    if image:
        embed.set_image(url=image)
    if thumbnail:
        embed.set_thumbnail(url=thumbnail)
    return embed

def syntax(client, command):
    cmd_and_aliases = client.command_prefix[0] + "|".join([str(command), *command.aliases])
    params = []
    for key, value in command.params.items():
        if key not in ("self", "context"):
            params.append(f"[{key}]" if "NoneType" in str(value) else f"<{key}>")
    params = " ".join(params)
    return f"```{cmd_and_aliases} {params}```"


class Help(commands.Cog, name="help", description="Get info about the bot and how to use it"):
    def __init__(self, client):
        self.client = client
        self.client.remove_command("help")
        self.cogs = [c for c in self.client.cogs.keys()]

    async def help(self, context):
        fields = [[f"All `{cog}` Commands:", "".join([f" • `{cmd}`\n" for cmd in self.client.get_cog(cog).get_commands()]).rstrip()] for cog in self.cogs]
        embed = create_embed(
            "John \"Not a robot\" Peter: Help",
            description=self.client.description,
            fields=fields
        )
        await context.send(embed=embed)

    async def cmd_help(self, client, context, command):
        command = get(self.client.commands, name=command)
        embed = create_embed("John \"Not a robot\" Peter: Help", description=f"Help with the `{command}` command", fields=[
            ["Syntax", syntax(client, command)],
            ["Brief Description", command.brief if command.brief else "None"],
            ["Description", command.description if command.description else "None"],
            ["Aliases", ", ".join(command.aliases) if command.aliases else "None"]
        ])
        await context.send(embed=embed)

    async def cat_help(self, context, category):
        embed = create_embed(
            "John \"Not a robot\" Peter: Help",
            description=f"Help with the `{category}` category",
            fields=[
                ["Description:", self.client.get_cog(category).description if self.client.get_cog(category).description else None],
                ["Commands", "".join([f" • `{cmd}` - {cmd.brief}\n" for cmd in self.client.get_cog(category).get_commands()]).rstrip()]
            ]
        )
        await context.send(embed=embed)

    @commands.command(name="help", brief="Get help about the commands and categories of the bot", description="This will allow you to get the descriptions, aliases, and syntax of commands, and the description and list of commands in a category. This command can optionally be used with a command or category name.")
    async def show_help(self, context, name: Optional[str]):
        self.cogs = [c for c in self.client.cogs.keys()]
        if name is None:
            await self.help(context)
            return
        if name in self.cogs:
            await self.cat_help(context, name)
        if get(self.client.commands, name=name):
            await self.cmd_help(self.client, context, name)
        else:
            await context.send(embed=create_embed("John \"Not a robot\" Peter: Help", description=f"The command `{name}` does not exist!"))


def setup(client):
    client.add_cog(Help(client))