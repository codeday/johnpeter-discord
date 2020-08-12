from functools import wraps
from os import getenv

from discord.ext.commands import Context, check, CheckFailure


def get_decorated_ctx(original_args):
    for arg in original_args:
        if type(arg) is Context:
            return arg
    return None


def safe_length(f):
    @wraps(f)
    async def wrap(*original_args, **original_kwargs):
        result = await f(*original_args, **original_kwargs)
        if type(result) is str:
            return result[0:2000]
        return result

    return wrap


class OnlyAllowedInChannels(CheckFailure):
    def __init__(self, channels):
        self.channels = channels


def check_in_channels(channels):
    def check(ctx):
        if (channels and len(channels) > 0) and not (ctx.channel.id in channels):
            raise OnlyAllowedInChannels(channels)
        return True

    return check


def only_channels(channels):
    def decorate(f):
        @wraps(f)
        @check(check_in_channels(channels))
        async def wrap(*original_args, **original_kwargs):
            return await f(*original_args, **original_kwargs)

        return wrap

    return decorate


def only_channel(channel):
    return only_channels([channel])


def only_random(f):
    return only_channels([int(getenv("CHANNEL_RANDOM", 689534362760642676))])(f)


class RequiresVoiceChannel(CheckFailure):
    pass


def check_vc(ctx):
    if ctx and (ctx.message.author.voice is None):
        raise RequiresVoiceChannel()
    return True


def require_vc(f):
    @wraps(f)
    @check(check_vc)
    async def wrap(*original_args, **original_kwargs):
        return await f(*original_args, **original_kwargs)

    return wrap
