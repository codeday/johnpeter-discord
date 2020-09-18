import random
from typing import Union

import discord
from discord.ext import commands

from utils.confirmation import confirm
from utils import checks
from db.models import session_creator, Reactions


class ReactionCommands(commands.Cog, name="Reactions"):
    """A cog where all the reaction commands live"""

    # TODO: better docs for this

    def __init__(self, bot):
        self.bot = bot
        """
        groupmsgs = {
            "<message_id>": {
                "channel_id": "<channel_id>",
                "role_ids": ["<role_id>", "<role_id>"]
            }
        }
        """

    @commands.command()
    @checks.requires_staff_role()
    async def update_reaction_roles(self, ctx):
        """Makes sure that all users who have reacted to the message have a role. Does not remove roles from anyone."""
        groupmsgs = Reactions.groupmsgs()
        for msg_id, values in groupmsgs.items():
            message = await ctx.guild.get_channel(values["channel_id"]).fetch_message(
                msg_id
            )
            user: Union[discord.User, discord.Member]
            async for user in message.reactions.users():
                if not any(
                    role.id in groupmsgs.get(msg_id)["role_ids"] for role in user.roles
                ):
                    await user.add_roles(
                        message.guild.get_role(
                            random.choice(groupmsgs[msg_id]["role_ids"])
                        )
                    )

    async def clear(self):
        # TODO: Lola you need to write this function to unlink a message, should just be database stuff
        pass

    @commands.command()
    @checks.requires_staff_role()
    async def reaction_groups(
        self, ctx: commands.Context, message_channel_id, message_id
    ):
        """ Takes the students who have reacted to a message (and those who react later) and assigns them a random role
        from the corresponding roles in the command or database

        Gets role information from the message itself, you must @ the roles you want to add. Wowza!

        TODO: Process existing reactions
        """
        message_channel_id = int(message_channel_id)
        message_id = int(message_id)
        channel = ctx.guild.get_channel(message_channel_id)
        message = await channel.fetch_message(message_id)
        roles = ctx.message.role_mentions
        if len(roles) == 0:
            await ctx.send(
                "Looks like you did not specify any roles for this message! "
                "Please @ the roles you want to add in this message. Thanks!"
            )
            return
        if await confirm(
            f'Users reacting to message "{message.content}" will be randomly assigned to one of {len(roles)} groups',
            ctx,
            self.bot,
        ):
            session = session_creator()
            for role in roles:
                session.add(
                    Reactions(
                        role_id=role.id,
                        message_id=message_id,
                        channel_id=message_channel_id,
                    )
                )
            session.commit()
            session.close()

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        groupmsgs = Reactions.groupmsgs()
        if (
            payload.event_type == "REACTION_ADD"
            and payload.message_id in groupmsgs
            and payload.user_id != self.bot.user.id
        ):
            guild = self.bot.get_guild(payload.guild_id)
            member = guild.get_member(payload.user_id)

            if not any(
                role.id in groupmsgs.get(payload.message_id)["role_ids"]
                for role in member.roles
            ):
                await member.add_roles(
                    guild.get_role(
                        random.choice(groupmsgs[payload.message_id]["role_ids"])
                    )
                )


def setup(bot):
    bot.add_cog(ReactionCommands(bot))
