import discord
import logging

from discord.ext import commands
from google.cloud.firestore import CollectionReference, ArrayUnion, ArrayRemove
from main import client
from os import getenv
from random import choice
from urllib import parse

from database.teams import Team
from services.teamservice import TeamService

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
        self.channel_command = int(getenv("CHANNEL_COMMAND", 689601755406663711))  # not used
        self.channel_gallery = int(getenv("CHANNEL_GALLERY", 689559218679840887))  # channel to show teams
        self.role_staff = int(getenv('ROLE_STAFF', 689215241996730417))  # staff role also not used
        self.role_student = int(getenv('ROLE_STUDENT', 689214914010808359))  # student role
        self.category = int(getenv("CATEGORY", 689598417063772226))
        self.team_service = TeamService()

    @commands.command(name="team-checkin", alias=["team-check-in", "team_check_in", "team_checkin"])
    @commands.has_any_role('Global Staff', 'Staff')
    async def team_check_in(self, ctx):
        """Requests that all teams fill out the check-in form."""
        self.team_service.__update__()
        for team in self.team_service.get_teams():
            try:
                url = f"https://www.cognitoforms.com/Srnd1/VirtualCodeDayCheckInForm?entry=%7B%22TeamName%22:%22{parse.quote(team.name)}%22,%22ProjectName%22:%22{parse.quote(team.project)}%22%7D"
                title_options = [f"How's life {team.name}?",
                                 "Hello, living organism! How do you do this fine [weather:city] day?", "Howdy do!?!"]
                message_options = [
                    f"Good? I hope so! Please, go to the link down there and tell me so we can keep tabs on how you're doing. Thanks!",
                    f"Hope you're programming is going swell! I have orders to have you fill out the form down there so my fellow staff can keep up to date. Thanks!",
                    f"I'm feeling pretty [john:emotion]! Please, tell me how you are feeling about your project down there. Bye for now!"
                ]
                thumbnail = ["https://f1.srnd.org/codeday/virtual-s20/tropical1.png",
                             "https://f1.srnd.org/codeday/virtual-s20/tropical2.png",
                             "https://f1.srnd.org/codeday/virtual-s20/tropical3.png",
                             "https://f1.srnd.org/codeday/virtual-s20/tropical4.png",
                             "https://f1.srnd.org/codeday/virtual-s20/tropical5.png",
                             "https://f1.srnd.org/codeday/virtual-s20/tropical6.png",
                             "https://f1.srnd.org/codeday/virtual-s20/tropical7.png",
                             ]
                embed = discord.Embed(title=f"Virtual CodeDay Checkin Form",
                                      url=url,
                                      description=f"[Let us know how your project is doing!]({url})",
                                      color=0xff686b)
                embed.set_thumbnail(url=choice(thumbnail))
                embed.set_footer(text="John Peter - Professional Human")
                await ctx.guild.get_channel(team.tc_id).send(choice(title_options) + " " + choice(message_options),
                                                             embed=embed)
                # await ctx.send(choice(title_options) + " " + choice(message_options), embed=embed)
            except Exception as ex:
                print("I have an exception!" + ex.__str__())

    @commands.command(name="team-add", aliases=['team_add', 'team-create', 'team_create'])
    @commands.has_any_role('Global Staff', 'Staff')
    async def team_add(self, ctx: commands.context.Context, team_name: str, team_emoji: discord.Emoji = None):
        """Adds a new team with the provided name and emoji.
            Checks for duplicate names, then creates a VC and TC for the team as well as an invite message, then
            adds the team to the firebase thing for future reference.
            Does not add any team members, they must add themselves or be manually added separately
        """

        if team_emoji is None:
            logging.debug("Starting team creation...")
            await ctx.send("Please add an emoji!")
        else:
            logging.debug("Starting team creation...")
            collection_ref: CollectionReference = client.collection("teams")

            duplicate_name = collection_ref.where("name", "==", team_name).stream()

            # Checks if any teams with this name already exist, and fails if they do
            if sum(1 for _ in duplicate_name) > 0:
                await ctx.send("A team with that name already exists! Please try again, human!")
                return

            # Creates a new channel for the new team
            overwrites = {
                ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                ctx.guild.get_role(self.role_student): discord.PermissionOverwrite(read_messages=False),
                ctx.guild.me: discord.PermissionOverwrite(read_messages=True)
            }
            tc = await ctx.guild.create_text_channel(name=f"{team_name.replace(' ', '-')}-📋",
                                                     overwrites=overwrites,
                                                     category=ctx.guild.get_channel(self.category),
                                                     topic=f"A channel for {team_name} to party! \nAnd maybe do some work too")
            vc = await ctx.guild.create_voice_channel(name=f"{team_name.replace(' ', '-')}-🔊",
                                                      overwrites=overwrites,
                                                      category=ctx.guild.get_channel(self.category),
                                                      topic=f"A channel for {team_name} to party! \nAnd maybe do some work too")
            await tc.send(f"Welcome to team `{team_name}`!! I'm excited to see what you can do!")

            # Creates and sends the join message
            join_message: discord.Message = await ctx.guild.get_channel(self.channel_gallery).send(
                choice(teamCreateMessages).format(team_name) +
                f"\nReact with {team_emoji} if you "
                f"want to join!")
            await join_message.add_reaction(team_emoji)

            team = Team(team_name, team_emoji.__str__(), vc.id, tc.id, join_message.id)
            self.team_service.add_team(team)

            await ctx.send("Team created successfully! Direct students to #team-gallery to join the team!")

    @commands.command(name="team-project", aliases=['team_project'])
    @commands.has_any_role('Global Staff', 'Staff')
    async def team_project(self, ctx, name, project):
        """Sets the team description."""
        # Sets team project
        team = self.team_service.edit_team(name, "project", project)
        if team is True:
            team_dict = self.team_service.get_by_name(name).to_dict()
            message = await ctx.guild.get_channel(self.channel_gallery).fetch_message((team_dict["join_message_id"]))
            message_content = message.content.split("\nProject:")
            await message.edit(content=message_content[0] + "\nProject: " + project)
            await ctx.guild.get_channel(team_dict['tc_id']).edit(topic=project)
            await ctx.send("Project updated!")
        else:
            await ctx.send("Could not find guild with the name: " + name)

    @commands.command(name="teams")
    @commands.has_any_role('Global Staff', 'Staff')
    async def teams(self, ctx):
        """Prints out the current teams."""
        teams = client.collection("teams")
        long_message_string = "Teams:"
        for i in teams.stream():
            long_message_string = long_message_string + f"\n {i.to_dict()}"
        await ctx.send(long_message_string)

    @commands.command(name="team-delete", aliases=['team_delete'], pass_context=True)
    @commands.has_any_role('Global Staff', 'Staff')
    async def team_delete(self, ctx, name):
        """Deletes the specified team."""
        team = self.team_service.get_by_name(name)
        if team is not False:
            await ctx.guild.get_channel(team.vc_id).delete()
            await ctx.guild.get_channel(team.tc_id).delete()
            message = await ctx.guild.get_channel(self.channel_gallery).fetch_message(team.join_message_id)
            await message.delete()
            self.team_service.delete_team(name)
            await ctx.send("Deleted team: " + name)
        else:
            await ctx.send("Could not find team with the name: " + name)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if payload.event_type == "REACTION_ADD" and payload.emoji.name == 'CODEDAY' and payload.channel_id == self.channel_gallery:
            collection_ref: CollectionReference = client.collection("teams")
            team = list(collection_ref.where("join_message_id", "==", payload.message_id).stream())[0].reference
            team.update({"members": ArrayUnion([payload.user_id])})
            team_dict = team.get().to_dict()
            await payload.member.guild.get_channel(team_dict['tc_id']).set_permissions(payload.member,
                                                                                       read_messages=True,
                                                                                       manage_messages=True)
            await payload.member.guild.get_channel(team_dict['vc_id']).set_permissions(payload.member,
                                                                                       read_messages=True)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        if payload.event_type == "REACTION_REMOVE" and payload.emoji.name == 'CODEDAY' and payload.channel_id == self.channel_gallery:
            collection_ref: CollectionReference = client.collection("teams")
            team = list(collection_ref.where("join_message_id", "==", payload.message_id).stream())[0].reference
            team.update({"members": ArrayRemove([payload.user_id])})
            team_dict = team.get().to_dict()
            guild = self.bot.get_guild(payload.guild_id)
            member = guild.get_member(payload.user_id)
            await guild.get_channel(team_dict['tc_id']).set_permissions(member, read_messages=False)
            await guild.get_channel(team_dict['vc_id']).set_permissions(member, read_messages=False)


def setup(bot):
    bot.add_cog(TeamBuilderCog(bot))
