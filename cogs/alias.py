from discord.ext.commands import Cog, Context, Bot


class Alias(Cog):
    """Aliases for commonly used commands."""

    def __init__(self, bot: Bot):
        self.bot = bot

    async def invoke(self, ctx: Context, cmd_name: str, *args, **kwargs) -> None:
        """Invokes a command with args and kwargs."""
        print(f"{cmd_name} was invoked through an alias")
        cmd = self.bot.get_command(cmd_name)
        await ctx.invoke(cmd, *args, **kwargs)
