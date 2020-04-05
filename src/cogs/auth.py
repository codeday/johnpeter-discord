import os

from discord.ext import commands

from database.users import User
from services.userservice import UserDatabase


class AuthCommands(commands.Cog, name="Authentication"):
    """A cog where all the authentication commands live"""

    def __init__(self, bot):
        self.bot = bot
        self.db = UserDatabase(user=os.getenv("MYSQL_USER"),
                               password=os.getenv("MYSQL_PASS"),
                               host=os.getenv("MYSQL_HOST"),
                               database=os.getenv("MYSQL_DB"))

    @commands.command(name='link-clear', hidden=True)
    async def link_clear(self, ctx, username):
        user = User(discord_id=ctx.author.id, clear_username=username)
        self.db.create_user(user)

    @commands.command(name='update-clear', hidden=True)
    async def update_clear(self, ctx, username):
        user = User(discord_id=ctx.author.id, clear_username=username)
        self.db.update_user(user)

def setup(bot):
    bot.add_cog(AuthCommands(bot))
