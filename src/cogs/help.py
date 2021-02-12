import discord
from discord.ext import commands


def create_embed(title=None, description=None, author=None, fields=None, image=None, thumbnail=None,
                 color=discord.Color.teal()):
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

class BotHelpCommand(commands.MinimalHelpCommand):
    async def send_pages(self):
        destination = self.get_destination()
        embed = create_embed("John Peter: Help", description="".join(self.paginator.pages))
        await destination.send(embed=embed)