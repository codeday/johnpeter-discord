import logging
from os import getenv
from random import choice

import discord
from discord.ext import commands
from discord.utils import get

from db.models import session_creator
from services.teamservice import TeamService
from utils.confirmation import confirm
from utils.forms import (
    send_team_check_in,
    send_team_check_ins,
    send_team_submit_form,
    send_team_submit_forms,
)
from utils.paginated_send import paginated_send

teamCreateMessages = [
    "Yeehaw! Looks like team **{0}** has joined CodeDay!",
    "Team **{0}** has entered the chat!",
    "Hello, team **{0}**.",
    "Don't panic! team {0} is here!",
    "What's this? team **{0}** is here!",
]


class DatabaseError(Exception):
    pass


class TeamBuilderCog(commands.Cog, name="Team Builder"):
    """Creates Teams!"""

    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.channel_command = int(
            getenv("CHANNEL_COMMAND", 689601755406663711)
        )  # not used
        self.channel_gallery = int(
            getenv("CHANNEL_GALLERY", 743216998712082472)
        )  # channel to show teams
        self.role_staff = int(
            getenv("ROLE_STAFF", 689215241996730417)
        )  # staff role also not used
        self.role_student = int(
            getenv("ROLE_STUDENT", 714577449408659567)
        )  # student role
        self.category = int(getenv("CATEGORY", 743216842796957736))
        self.team_service = TeamService()
        self.forms = {
            "checkin": {
                "aliases": ["check-in", "check_in", "check in"],
                "func": send_team_check_ins,
                "func_i": send_team_check_in,
            },
            "submit": {
                "aliases": [
                    "submission",
                    "submit-project",
                    "submit_project",
                    "submit-form",
                    "submit_form",
                ],
                "func": send_team_submit_forms,
                "func_i": send_team_submit_form,
            },
        }

        for form in list(self.forms):
            for alias in self.forms[form]["aliases"]:
                self.forms[alias] = {"func": self.forms[form]["func"]}

    @commands.group(name="team")
    async def team(self, ctx):
        """Contains team subcommands, do '~help team' for more info"""
        if ctx.invoked_subcommand is None:
            await ctx.send("Invalid team command passed...")

    @team.group(name="broadcast")
    async def team_broadcast(self, ctx):
        """Contains broadcast subcommands, do '~help team broadcast' for more info"""
        if ctx.invoked_subcommand is None:
            await ctx.send("Invalid team broadcast command passed...")

    @team_broadcast.command(name="form")
    @commands.has_any_role("Employee", "Staff")
    async def team_broadcast_form(self, ctx: commands.context.Context, *form):
        form = " ".join(form)
        if form in self.forms:
            if await confirm(
                f'Are you sure you would like to send the "{form}" form to all teams?',
                bot=self.bot,
                ctx=ctx,
                success_msg="Ok, I am now sending the form",
                abort_msg="Ok, I will not send the form",
            ):
                await self.forms[form]["func"](self, ctx)
        else:
            await ctx.send("I'm sorry, but I don't know the form you are talking about")

    @team_broadcast.command(name="form-individual")
    @commands.has_any_role("Employee", "Staff")
    async def team_broadcast_form_individual(self, ctx, name=None, *form):
        if not name:
            await ctx.send("No team name provided!")
            return
        if not form:
            await ctx.send("No form provided!")
            return
        team = self.team_service.get_team_by_name(name)
        if not team:
            await ctx.send("Could not find a team with that name!")
            return
        form = " ".join(form)
        if form in self.forms:
            await self.forms[form]["func_i"](self, ctx, team)
        else:
            await ctx.send(
                "I'm sorry, but I do not know the form you are talking about"
            )

    @team_broadcast.command(name="message")
    @commands.has_any_role("Employee", "Staff")
    async def team_broadcast_message(self, ctx: commands.context.Context, *message):
        message = " ".join(message)
        if await confirm(
            f'Are you sure you would like to send the message "{message}" to all teams?',
            bot=self.bot,
            ctx=ctx,
            success_msg="Ok, I am will send the message",
            abort_msg="Ok, I will not send the message",
        ):
            for team in self.team_service.get_all_teams():
                try:
                    await ctx.guild.get_channel(team.tc_id).send(message)
                except Exception as ex:
                    print("I have an exception!" + ex.__str__())

    @team.command(name="add", aliases=["create"])
    @commands.has_any_role("Employee", "Staff")
    async def team_add(self, ctx: commands.context.Context, team_name: str):
        """Adds a new team with the provided name
            Checks for duplicate names, then creates a TC for the team as well as an invite message, then
            adds the team to the database.
            Does not add any team members, they must add themselves or be manually added separately
        """
        logging.debug("Starting team creation...")
        team_emoji = get(ctx.guild.emojis, name="CODEDAY")

        # Checks if any teams with this name already exist, and fails if they do
        if self.team_service.get_team_by_name(team_name) is not None:
            await ctx.send(
                "A team with that name already exists! Please try again, human!"
            )
            return

        # Creates a new channel for the new team
        overwrites = {
            ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            ctx.guild.get_role(self.role_student): discord.PermissionOverwrite(
                read_messages=False
            ),
            ctx.guild.me: discord.PermissionOverwrite(
                read_messages=True, read_message_history=True
            ),
        }
        tc = await ctx.guild.create_text_channel(
            name=f"{team_name.replace(' ', '-')}-📋",
            overwrites=overwrites,
            category=ctx.guild.get_channel(self.category),
            topic=f"A channel for {team_name} to party! \nAnd maybe do some work too",
        )
        await tc.send(
            f"Welcome to team `{team_name}`!! I'm excited to see what you can do!"
        )

        # Creates and sends the join message
        join_message: discord.Message = await ctx.guild.get_channel(
            self.channel_gallery
        ).send(
            choice(teamCreateMessages).format(team_name)
            + f"\nReact with {team_emoji} if you "
            f"want to join!"
        )
        await join_message.add_reaction(team_emoji)

        self.team_service.add_team(team_name, tc.id, join_message.id)

        await ctx.send(
            "Team created successfully! Direct students to #team-gallery to join the team!"
        )

    @team.command(name="project", aliases=["set-project", "setproject", "set_project"])
    @commands.has_any_role("Employee", "Staff")
    async def team_project(
        self, ctx, name=str, project=str
    ):  # TODO: Verify that the typecasting of string works right
        """Sets the team project description."""
        if not name:
            await ctx.send("No team name provided!")
            return
        if not project:
            await ctx.send("No project description provided!")
            return
        team = self.team_service.edit_team(name, project)
        if team:
            # if not valid_team_string(project):
            #     valid_string = make_valid_team_string(project)
            #     if await confirm(
            #             f'That team project was invalid.\
            #              Would you like to continue team creation with the project "{valid_string}" instead?',
            #             bot=self.bot, ctx=ctx):
            #         project = valid_string
            #     else:
            #         return
            # team_dict = self.team_service.get_by_name(name).to_dict()
            # message = await ctx.guild.get_channel(self.channel_gallery).fetch_message((team_dict["join_message_id"]))
            # message_content = message.content.split("\nProject:")
            # await message.edit(content=message_content[0] + "\nProject: " + project)
            # await ctx.guild.get_channel(team_dict['tc_id']).edit(topic=project)
            #
            # !! Should all be unnecessary now? Seems like it existed to remove certain characters, which shouldn't be
            #    an issue now.
            await ctx.send("Project updated!")
        else:
            await ctx.send("Could not find team with the name: " + str(name))

    @team.command(
        name="teams", aliases=["get_teams", "get-teams", "list_teams", "list-teams"]
    )
    @commands.has_any_role("Employee", "Staff")
    async def teams(self, ctx):
        """Prints out the current teams."""
        # TODO: Check on how this is parsed, might need to write something to clean up the team data
        session = session_creator()
        teams = self.team_service.get_all_teams(session=session)
        out = "------\n"
        for team in teams:
            out += str(team) + "\n"
        session.commit()
        session.close()
        await paginated_send(ctx, out)

    @team.command(name="delete")
    @commands.has_any_role("Employee", "Staff")
    async def team_delete(self, ctx, name):
        """Deletes the specified team."""
        team = self.team_service.get_team_by_name(name)
        if team is not False:
            try:
                await ctx.guild.get_channel(team.tc_id).delete()
            except:
                pass
            try:
                message = await ctx.guild.get_channel(
                    self.channel_gallery
                ).fetch_message(team.join_message_id)
                await message.delete()
            except:
                pass
            self.team_service.delete_team_by_id(name)
            # !! Pretty sure we should add delete_team_by_name for this use case
            await ctx.send("Deleted team: " + name)
        else:
            await ctx.send("Could not find team with the name: " + name)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if (
            payload.event_type == "REACTION_ADD"
            and payload.emoji.name == "CODEDAY"
            and payload.channel_id == self.channel_gallery
            and payload.member.id != self.bot.user.id
        ):
            session = session_creator()
            team = self.team_service.get_team_by_join_message_id(
                str(payload.message_id), session
            )
            await payload.member.guild.get_channel(int(team.tc_id)).set_permissions(
                payload.member, read_messages=True, manage_messages=True
            )
            self.team_service.add_member(team, str(payload.user_id), session)
            session.commit()
            session.close()

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        if (
            payload.event_type == "REACTION_REMOVE"
            and payload.emoji.name == "CODEDAY"
            and payload.channel_id == self.channel_gallery
        ):
            session = session_creator()
            team = self.team_service.get_team_by_join_message_id(
                str(payload.message_id), session
            )
            guild = self.bot.get_guild(payload.guild_id)
            member = guild.get_member(payload.user_id)
            await guild.get_channel(int(team.tc_id)).set_permissions(
                member, read_messages=False, manage_messages=False
            )
            self.team_service.remove_member(team, str(payload.user_id), session)
            session.commit()
            session.close()


def setup(bot):
    bot.add_cog(TeamBuilderCog(bot))
