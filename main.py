import discord
from os import environ
from discord.ext import commands
import logging
import traceback
from google.cloud import firestore
import time

BOT_TOKEN = environ['BOT_TOKEN']

bot = commands.Bot(command_prefix='j!', command_not_found="Heck! That command doesn't exist!!",
                   description="I am 100% authentic object:human")
logging.basicConfig(level=logging.INFO)

client = firestore.Client()
collection = client.collection('teams')
# documents = list(collection.stream())
documents = collection.stream()
for doc in documents:
    print(u'{} => {}'.format(doc.id, doc.to_dict()))

initial_cogs = ['cogs.team-builder']

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
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send('That command doesn\'t seem to exist! Please try again, and type `'
                       'help` to view the help documentation.')
    else:
        raise error


@bot.event
async def on_message(message):
    # This is just here to exist in case I need it later. Should be moved out soon
    # Insures the other commands are still processed
    await bot.process_commands(message)


bot.run(BOT_TOKEN, bot=True, reconnect=True)
