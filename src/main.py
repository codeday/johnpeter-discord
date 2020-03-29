import logging
import traceback
from os import environ, getenv

import discord
from discord.ext import commands
from google.cloud import firestore
from services.randomservice import RandomFuncs
import sys
from raygun4py import raygunprovider

from utils.commands import OnlyAllowedInChannels, RequiresVoiceChannel

BOT_TOKEN = environ['BOT_TOKEN']
error_channel = int(getenv('CHANNEL_ERRORS', 693223559387938817))  # Where errors go when reported
raygun_key = getenv('RAYGUN_KEY', None)


def handle_exception(exc_type, exc_value, exc_traceback):
    cl = raygunprovider.RaygunSender(raygun_key)
    cl.send_exception(exc_info=(exc_type, exc_value, exc_traceback))
    sys.__excepthook__(type, exc_value, traceback)


sys.excepthook = handle_exception


def command_prefix(bot, message):
    if message.content.startswith('~~'):
        return 'j!'
    if message.content.startswith('~'):
        return '~'
    else:
        return 'j!'


bot = commands.Bot(command_prefix=command_prefix, command_not_found="Heck! That command doesn't exist!!",
                   description="I am 100% authentic object:human")
logging.basicConfig(level=logging.INFO)

client = firestore.Client()
collection = client.collection('teams')

initial_cogs = ['cogs.team-builder', 'cogs.cleverbot', 'cogs.admin-commands', 'cogs.tournament', 'cogs.fun-commands']

# Here we load our extensions(cogs) listed above in [initial_extensions].
for cog in initial_cogs:
    # noinspection PyBroadException
    try:
        bot.load_extension(cog)
        logging.info(f'Successfully loaded extension {cog}')
    except Exception as e:
        logging.exception(f'Failed to load extension {cog}.', exc_info=traceback.format_exc())


@bot.event
async def on_ready():
    """Sets up the bot's nicknames and the game it is streaming"""

    # Sets up the bot's "game"
    await bot.change_presence(activity=discord.CustomActivity(
        name='Hello, Human!', emoji=bot.get_emoji(689553120153698305)))
    # TODO: Fix the stupid activity because discord bad

    # Counts servers the bot is on
    counter = 0
    for i in bot.guilds:
        counter += 1
        print('We have logged in as {0.user}'.format(bot))
    logging.info("We are in {0} server!".format(counter))


@bot.event
async def on_command_error(ctx, error: commands.CommandError):
    """Specially handles some errors, all others take the unhandled route"""
    if isinstance(error, commands.CommandNotFound):
        await ctx.send('That command doesn\'t seem to exist! Please try again, and type `'
                       'help` to view the help documentation.')
    else:
        error_message_list = list(RandomFuncs.paginate(
            ''.join(map(str, traceback.format_exception(type(error), error, error.__traceback__))), 1900))
        await ctx.send("Hmm, that's weird! You just hit an unhandled error! It has been reported.")
        await bot.get_channel(error_channel).send(
            f"New error! Yikes! \n\n```{error_message_list[0]}```")
        if len(error_message_list) > 1:
            for i in error_message_list[1:]:
                await bot.get_channel(error_channel).send(f"```{i}```")
        handle_exception(type(error), error, error.__traceback__)
        raise error


@bot.event
async def on_message(message):
    # This is just here to exist in case I need it later. Should be moved out soon
    # Insures the other commands are still processed
    await bot.process_commands(message)

@bot.event
async def on_command_error(ctx, exception):
    if (type(exception) is OnlyAllowedInChannels):
        return await ctx.send(f"You can only do that in {'/'.join([f'<#{cid}>' for cid in exception.channels])}")

    if (type(exception) is RequiresVoiceChannel):
        return await ctx.send(f"You're not in a voice channel!")

bot.run(BOT_TOKEN, bot=True, reconnect=True)
