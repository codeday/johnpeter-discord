import json
import logging
import sys
import traceback
from os import environ, getenv
from random import choice

import discord
import requests
from discord.ext import commands
from discord.ext.commands import MissingAnyRole, BadArgument, ExpectedClosingQuoteError
from raygun4py import raygunprovider

from utils.commands import OnlyAllowedInChannels, RequiresVoiceChannel
from utils.paginated_send import paginated_send
from utils.exceptions import BugReport

has_bot_started = False

BOT_TOKEN = environ["BOT_TOKEN"]
# Where errors go when reported
error_channel = int(getenv("CHANNEL_ERRORS", 693223559387938817))
raygun_key = getenv("RAYGUN_KEY", None)


def handle_exception(exc_type, exc_value, exc_traceback):
    cl = raygunprovider.RaygunSender(raygun_key)
    cl.send_exception(exc_info=(exc_type, exc_value, exc_traceback))
    sys.__excepthook__(type, exc_value, traceback)


sys.excepthook = handle_exception


def command_prefix(bot, message):
    if message.content.startswith("~~"):
        return "j!"
    if message.content.startswith("~"):
        return "~"
    else:
        return "j!"


bot = commands.Bot(
    command_prefix=command_prefix,
    command_not_found="Heck! That command doesn't exist!!",
    description="I am 100% authentic object:human",
)
logging.basicConfig(level=logging.INFO)

initial_cogs = [
    "cogs.team-builder",
    "cogs.cleverbot",
    "cogs.admin-commands",
    "cogs.tournament",
    "cogs.fun-commands",
    "cogs.reactions",
]

statuses = [
    discord.Game("the sweet, sweet music of CodeDay!"),
    discord.Game("Global Thermonuclear War"),
    discord.Game("Debugging Simulator 2020"),
    discord.Game("with fire"),
    discord.Activity(
        name="people forget to add .gitignores", type=discord.ActivityType.watching
    ),
    discord.Game("CodeCup"),
]

# Here we load our extensions(cogs) listed above in [initial_extensions].
for cog in initial_cogs:
    # noinspection PyBroadException
    try:
        bot.load_extension(cog)
        logging.info(f"Successfully loaded extension {cog}")
    except Exception as e:
        logging.exception(
            f"Failed to load extension {cog}.", exc_info=traceback.format_exc()
        )


@bot.command(name="bug_report", aliases=["bug", "bug-report", "issue"])
async def bug_report(ctx, *, issue):
    """Allows users to file a bug report straight through John.
    This will raise a new raygun issue and can be dealt with that way. """
    client = raygunprovider.RaygunSender(raygun_key)
    httpResult = client.send_exception(exception=BugReport(message=issue, context=ctx))
    if 200 <= httpResult[0] <= 299:
        await ctx.send("Report filed, thank you!")
    else:
        await ctx.send(
            "Hmm, that didn't work. If the bug report failed, something is probaly very wrong, please @ a staff member!"
        )


@bot.event
async def on_ready():
    global has_bot_started
    if has_bot_started:
        return
    has_bot_started = True
    version = getenv("IMAGE_TAG")
    if version:
        r = requests.get(
            f"https://api.github.com/repos/srnd/johnpeter-discord/commits/{version}"
        )
        if r.status_code == requests.codes.ok:
            commit = json.loads(r.text)["commit"]
            await bot.get_channel(error_channel).send(
                f"~~Started~~ woke up with version `{version[0:7]} - {commit['message']} ({commit['committer']['name']})`"
            )
        else:
            await bot.get_channel(error_channel).send(
                f"~~Started~~ woke up with version `{version}`"
            )
    else:
        await bot.get_channel(error_channel).send(f"~~Started~~ woke up")

    await bot.change_presence(activity=choice(statuses))

    # Counts servers the bot is on
    counter = 0
    for i in bot.guilds:
        counter += 1
        logging.info(f"We have logged in as {bot.user}")
    logging.info(f"We are in {counter} server!")


@bot.event
async def on_command_error(ctx, error: commands.CommandError):
    """Specially handles some errors, all others take the unhandled route"""
    if isinstance(error, commands.CommandNotFound):
        return await ctx.send(
            "That command doesn't seem to exist! Please try again, and type `"
            "help` to view the help documentation."
        )

    if type(error) is OnlyAllowedInChannels:
        return await ctx.send(
            f"You can only do that in {'/'.join([f'<#{cid}>' for cid in error.channels])}"
        )
        # TODO: See if this works

    if type(error) is RequiresVoiceChannel:
        return await ctx.send(f"You're not in a voice channel!")

    if type(error) is MissingAnyRole:
        return await ctx.send(
            "You are not in the sudoers file. This incident will be reported."
        )

    if type(error) is BadArgument:
        if "Emoji" in error.args[0]:
            return await ctx.send(
                "Hmm, did you miss some quotes or use an emoji from another server?"
            )

    if type(error) is ExpectedClosingQuoteError:
        return await ctx.send('Looks like you dropped something: "')

    else:
        await ctx.send(
            "Hmm, that's weird! You just hit an unhandled error! It has been reported."
        )

        await paginated_send(
            bot.get_channel(error_channel),
            f"New error! Yikes! \n\n Invoking message: ```{ctx.message.content}``` {ctx.message.jump_url} \n\n Traceback: ```{''.join(map(str, traceback.format_exception(type(error), error, error.__traceback__)))}```",
        )
        handle_exception(type(error), error, error.__traceback__)
    raise error


@bot.event
async def on_message(message):
    # This is just here to exist in case I need it later. Should be moved out soon
    # Insures the other commands are still processed
    await bot.process_commands(message)


bot.run(BOT_TOKEN, bot=True, reconnect=True)
