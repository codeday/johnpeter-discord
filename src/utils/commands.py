from discord.ext.commands import Context, check
from functools import wraps
from os import getenv

def get_decorated_ctx(original_args):
    for arg in original_args:
        if type(arg) is Context:
            return arg
    return None

def check_in_channels(channels):
    def check(ctx):
        return (not (channels and len(channels) > 0)) or (ctx.channel.id in channels)
    return check

def safe_length(f):
    @wraps(f)
    async def wrap(*original_args, **original_kwargs):
        result = await f(*original_args, **original_kwargs)
        if (type(result) is str):
            return result[0:2000]
        return result
    return wrap

def only_channels(channels):
    def decorate(f):
        @wraps(f)
        @check(check_in_channels(channels))
        async def wrap(*original_args, **original_kwargs):
            ctx = get_decorated_ctx(original_args)
            if (ctx and not check_in_channels(channels)(ctx)):
                return await ctx.send(f"You can only do that in {'/'.join([f'<#{cid}>' for cid in channels])}")
            else:
                return await f(*original_args, **original_kwargs)

        return wrap
    return decorate

def only_channel(channel):
    return only_channels([channel])

def only_random(f):
    return only_channels([int(getenv("CHANNEL_RANDOM", 689534362760642676))])(f)

def require_vc(f):
    @wraps(f)
    async def wrap(*original_args, **original_kwargs):
        ctx = get_decorated_ctx(original_args)
        if (ctx and (ctx.message.author.voice is None)):
            return await ctx.send("You're not in a voice channel!")
        else:
            return await f(*original_args, **original_kwargs)
    return wrap
