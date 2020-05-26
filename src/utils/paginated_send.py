from discord.ext.commands import context
from textwrap import wrap


async def paginated_send(ctx: context.Context, message: str):
    """
    Like normal discord message.send, but now paginated!
    """

    split_message = wrap(str, 1900)
    for i in split_message:
        await ctx.send(i)
