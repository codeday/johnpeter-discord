import asyncio

from discord.ext import commands


async def confirm(
        confirmation: str,
        ctx: commands.context.Context,
        bot,
        abort_msg = 'Action Aborted',
        success_msg = 'Action Confirmed!',
        delete_msgs = True
):
    msgs = [await ctx.send(confirmation)]
    await msgs[0].add_reaction('🚫')
    await msgs[0].add_reaction('✅')
    def check(reaction, user):
        return user == ctx.author and (str(reaction.emoji) == '🚫' or str(reaction.emoji) == '✅')

    try:
        reaction, user = await bot.wait_for('reaction_add', timeout=60.0, check=check)
    except asyncio.TimeoutError:
        await msgs[0].delete()
    else:
        if str(reaction.emoji) == '🚫':
            msgs.append(await ctx.send(abort_msg))
            return False
        elif str(reaction.emoji) == '✅':
            msgs.append(await ctx.send(success_msg))
            return True
        if delete_msgs:
            for msg in msgs:
                await msg.delete(delay=5)
