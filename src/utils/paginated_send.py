from discord.ext.commands import context


async def paginated_send(ctx: context.Context, message: str):
    """
    Like normal discord message.send, but now paginated!
    """
    n = 1900

    split_message = [message[i:i + n] for i in range(0, len(message), n)]

    for i in split_message:
        await ctx.send(i)
