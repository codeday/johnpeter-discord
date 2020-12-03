from discord.ext.commands import context


async def paginated_send(ctx: context.Context, message: str, **kwargs):
    """
    Like normal discord message.send, but now paginated!
    """
    n = 1900

    split_message = [message[i:i + n] for i in range(0, len(message), n)]

    for i in split_message:
        await ctx.send(i, **kwargs)


async def paginated_send_multiline(ctx: context.Context, message: str, **kwargs):
    n = 1900

    lines = message.split("\n")
    messages = []
    current_message = ""

    for line in lines:
        if len(line) > n:
            messages.append(current_message[1])
            current_message = ""
            for sl in [line[i:i + n] for i in range(0, len(line), n)]:
                messages.append(sl)
        else:
            if len(current_message) + len(line) > n:
                messages.append(current_message[1:])
                current_message = "\n" + line
            else:
                current_message += "\n" + line

    messages.append(current_message[1:])

    for message in messages:
        await ctx.send(message, **kwargs)
