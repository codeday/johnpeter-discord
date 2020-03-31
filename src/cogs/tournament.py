import asyncio
import logging

import discord
from discord.ext import commands

from database.tournaments import Tournament
from services.tournamentservice import TournamentService
from utils.person import id_from_mention


class TournamentCog(commands.Cog, name="Tournament Helper"):
    """Creates Tournament Brackets!"""
    # TODO: Make it support running multiple tournaments at the same time
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.category = int(692803392031948911)  # gaming tournament
        self.tournaments = TournamentService.load_tournaments()

    async def cog_after_invoke(self, ctx):
        TournamentService.store_tournaments(self.tournaments)

    @commands.group(name="tournament")
    async def tournament(self, ctx):
        """Contains tournament subcommands, do '~help tournament' for more info"""
        if ctx.invoked_subcommand is None:
            await ctx.send('Invalid tournament command passed...')

    @tournament.command(name="create")
    @commands.has_any_role('Tournament Master')
    async def tourney_create(self, ctx: commands.context.Context, game_name: str):
        """Creates a tournament with the given name."""
        await ctx.message.delete()
        logging.debug("Starting tournament creation...")
        t = Tournament(game_name=game_name,
                       tc_id=ctx.channel.id,
                       join_message_id=(await ctx.channel.send(Tournament.make_join_message(game_name))).id
                       )
        self.tournaments.append(t)
        await (await t.join_message(self.bot)).add_reaction('🏆')

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if (
                payload.event_type == 'REACTION_ADD'
                and payload.emoji.name == '🏆'
                and any(payload.message_id == t.join_message_id for t in self.tournaments)
                and payload.user_id != self.bot.user.id
        ):
            t = next((t for t in self.tournaments if t.join_message_id == payload.message_id))
            if not t.add_gamer(payload.user_id):
                user = self.bot.get_user(payload.user_id)
                while user.dm_channel is None:
                    await user.create_dm()
                await user.dm_channel.send(
                    'Sorry, but the tournament is already running, I am unable to add you'
                )
            await (await t.join_message(self.bot)).edit(content=t.update_join_message())
        TournamentService.store_tournaments(self.tournaments)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        if (
                payload.event_type == 'REACTION_REMOVE'
                and payload.emoji.name == '🏆'
                and any(payload.message_id == t.join_message_id for t in self.tournaments)
                and payload.user_id != self.bot.user.id
        ):
            t = next((t for t in self.tournaments if t.join_message_id == payload.message_id))
            if not t.remove_gamer(payload.user_id):
                user = self.bot.get_user(payload.user_id)
                while user.dm_channel is None:
                    await user.create_dm()
                await user.dm_channel.send(
                    '''Sorry, but the tournament has already started, so I am unable to remove you.
If you have to leave, please inform the @Tournament Master'''
                )
            await (await t.join_message(self.bot)).edit(content=t.update_join_message())
        TournamentService.store_tournaments(self.tournaments)

    @tournament.command(name="round")
    @commands.has_any_role('Tournament Master')
    async def tourney_round(self, ctx: commands.context.Context, idx=None):
        """Creates the next round"""
        t = self.tournaments[0]
        if await t.next_round(bot=self.bot):
            await ctx.message.delete()
            for game in t.rounds[-1].games:
                await game.create_channel(ctx=ctx, game_name=t.game_name, category=self.category)
        else:
            await ctx.send('Previous round not yet finished! Aborting')

    @tournament.command(name="winner-set", aliases=["winner_set", "round-winner-set", "round_winner_set", "set-winner",
                                                    "set-round-winner", "set_round_winner", "set_winner"])
    @commands.has_any_role('Tournament Master')
    async def round_winner_set(self, ctx: commands.context.Context, winner):
        """Sets the winner of a round."""
        t = self.tournaments[0]
        winner_id = id_from_mention(winner)
        game = t.rounds[-1].game_from_channel_id(ctx.channel.id)
        if winner_id in t.current_round.game_from_channel_id(ctx.channel.id).gamers:
            await game.set_winner(winner_id, self.bot)

    @tournament.command(name="winner",
                        aliases=["round-winner", "round_winner", 'votewinner', 'vote_winner', 'vote-winner',
                                 'roundwinner'])
    async def round_winner(self, ctx: commands.context.Context, winner=None):
        """Votes for the winner of a round."""
        t = self.tournaments[0]
        winner_id = id_from_mention(winner)
        game = t.rounds[-1].game_from_channel_id(ctx.channel.id)
        if game and winner_id:
            await game.vote(ctx.author.id, winner_id, self.bot)
            await (await self.bot.get_channel(t.tc_id).fetch_message(t.join_message_id)).edit(content=t.rounds[-1].generate_status_message())
        elif not game:
            await ctx.channel.send(
                "I'm sorry, but this is not a known channel.\
Please retry your command in a channel for a tournament match.")
        else:
            await ctx.channel.send('''I'm sorry, I don't know who you're talking about! Please use the command like so,\
mentioning the person who won:
~tournament winner <@689549152275005513>''')
            return

    @tournament.command(name="delete")
    @commands.has_any_role('Tournament Master')
    async def tourney_delete(self, ctx: commands.context.Context, idx):
        """Deletes the specified tournament."""
        idx = int(idx)
        if idx + 1 >= len(self.tournaments):
            t = self.tournaments[idx]
            msgs = [await ctx.send(f'Are you sure you would like to delete the {t.game_name} tournament?')]
            await msgs[0].add_reaction('🚫')
            await msgs[0].add_reaction('✅')

            def check(reaction, user):
                return user == ctx.author and (str(reaction.emoji) == '🚫' or str(reaction.emoji) == '✅')
            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
            except asyncio.TimeoutError:
                await msgs[0].delete()
            else:
                if str(reaction.emoji) == '🚫':
                    msgs.append(await ctx.send(f'Ok, I will not delete the {t.game_name} tournament'))
                elif str(reaction.emoji) == '✅':
                    msgs.append(await ctx.send(f'Ok, I am now deleting the {t.game_name} tournament.'))
                    await t.delete(self.bot)
                    self.tournaments.pop(idx)
                for msg in msgs:
                    await msg.delete(delay=5)
        else:
            await ctx.send(f'No tournament found with index {idx}')
            await self.tourney_list(ctx)

    @tournament.command(name="list")
    @commands.has_any_role('Tournament Master')
    async def tourney_list(self, ctx: commands.context.Context):
        out = f'```Running Tournaments ({len(self.tournaments)}):'
        for idx,tournament in enumerate(self.tournaments):
            out += f'\n {idx} - {tournament.game_name}'
        out += '```'
        await ctx.send(out)

    @tournament.command(name="broadcast")
    @commands.has_any_role('Tournament Master')
    async def tourney_broadcast(self, ctx: commands.context.Context, *message):
        """Sends the message to all in-progress games."""
        t = self.tournaments[0]
        message = ' '.join(list(message))
        msgs = [await ctx.send(f'Are you sure you would like to broadcast the message "{message}" to all running games?')]
        await msgs[0].add_reaction('🚫')
        await msgs[0].add_reaction('✅')

        def check(reaction, user):
            return user == ctx.author and (str(reaction.emoji) == '🚫' or str(reaction.emoji) == '✅')

        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
        except asyncio.TimeoutError:
            await msgs[0].delete()
        else:
            if str(reaction.emoji) == '🚫':
                msgs.append(await ctx.send('Ok, I will not send the message'))
            elif str(reaction.emoji) == '✅':
                msgs.append(await ctx.send('Ok, I am now sending the message'))
                await t.broadcast(message, self.bot)
            for msg in msgs:
                await msg.delete(delay=5)


def setup(bot):
    bot.add_cog(TournamentCog(bot))
