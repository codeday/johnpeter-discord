from discord import Embed
from discord.ext.commands import context

import asyncio

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

async def paginate_reaction(content, ctx, timeout=120, deleteMessage="This message was deleted to conserve bot resources."):

    right_arrow = "\N{BLACK RIGHT-POINTING DOUBLE TRIANGLE}"
    left_arrow = "\N{BLACK LEFT-POINTING DOUBLE TRIANGLE}"

    index = 0

    msg = await ctx.send(**content[index])
    if len(content) > 1:
        await msg.add_reaction(right_arrow)

    # only want reactions to paginated message by requester to trigger page changes
    check = lambda reaction, user: reaction.message.id == msg.id and user.id == ctx.author.id

    while True:
        try:
            # cancel after `timeout` seconds of inactivity
            reaction, _ = await ctx.bot.wait_for('reaction_add',timeout=timeout,check=check)

            if reaction.emoji == right_arrow and index < len(content)-1:
                index += 1
                await msg.edit(**content[index])
                await msg.clear_reactions()
                await msg.add_reaction(left_arrow)
                if index < len(content)-1:
                    await msg.add_reaction(right_arrow)
                
            elif reaction.emoji == left_arrow and index > 0:
                index -= 1
                await msg.edit(**content[index])
                await msg.clear_reactions()
                if index > 0:
                    await msg.add_reaction(left_arrow)
                await msg.add_reaction(right_arrow)

        # delete message after `timeout` seconds
        except asyncio.TimeoutError:
            try:
                await msg.clear_reactions()
            except:
                pass
            finally:
                break
