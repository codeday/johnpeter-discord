import discord
from discord.ext import commands
from main import client
from database_classes.teams import Team
from google.cloud.firestore import DocumentReference, CollectionReference, ArrayUnion


class DatabaseError(Exception):
    pass


class TeamBuilderCog(commands.Cog, name="Team Builder Commands"):
    """Creates Teams!"""

    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.command()
    @commands.has_role('Global Staff')
    async def add_team(self, ctx: commands.context.Context, team_name: str, team_emoji: discord.Emoji):
        """Adds a new team with the provided name and emoji.
            Checks for duplicate names, then creates a VC and TC for the team as well as an invite message, then
            adds the team to the firebase thing for future reference.
            Does not add any team members, they must add themselves or be manually added separately
        """
        await ctx.send("Starting team creation...")
        collection_ref: CollectionReference = client.collection("teams")

        duplicate_name = collection_ref.where("name", "==", team_name).stream()

        # Checks if any teams with this name already exist, and fails if they do
        if sum(1 for _ in duplicate_name) > 0:
            await ctx.send("A team with that name already exists! Please try again, human!")
            return

        # Creates a new channel for the new team
        overwrites = {
            ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            ctx.guild.get_role(689214914010808359): discord.PermissionOverwrite(read_messages=False),
            ctx.guild.me: discord.PermissionOverwrite(read_messages=True)
        }
        tc = await ctx.guild.create_text_channel(name=f"{team_name.replace(' ', '-')}-📋",
                                                 overwrites=overwrites,
                                                 category=ctx.guild.get_channel(689598417063772226),
                                                 topic=f"A channel for {team_name} to party! \nAnd maybe do some work too")
        vc = await ctx.guild.create_voice_channel(name=f"{team_name.replace(' ', '-')}-🔊",
                                                  overwrites=overwrites,
                                                  category=ctx.guild.get_channel(689598417063772226),
                                                  topic=f"A channel for {team_name} to party! \nAnd maybe do some work too")

        # Creates and sends the join message
        join_message: discord.Message = await ctx.guild.get_channel(689559218679840887).send(
            f"Who wants to join team {team_name}? If I were real, I know I would!\nReact with {team_emoji} if you "
            f"want to join!")
        await join_message.add_reaction(team_emoji)

        # Creates a new document for the new team
        document_ref: DocumentReference = client.collection("teams").document(team_name)

        result = document_ref.set(Team(team_name, team_emoji.__str__(), vc.id, tc.id, join_message.id).to_dict())
        if result:
            print("Successfully added!")
        else:
            raise DatabaseError

        await ctx.send("Team created successfully! Direct students to #team-gallery to join the team!")

    @commands.command()
    @commands.has_role('Global Staff')
    async def get_teams(self, ctx):
        """Prints out the teams, useful for debugging maybe? Locked to global staff only"""
        teams = client.collection("teams")
        long_message_string = "Teams:"
        for i in teams.stream():
            long_message_string = long_message_string + f"\n {i.to_dict()}"
        await ctx.send(long_message_string)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if payload.event_type == "REACTION_ADD" and payload.emoji.name == 'CODEDAY' and payload.channel_id == 689559218679840887:
            collection_ref: CollectionReference = client.collection("teams")
            team = list(collection_ref.where("join_message_id", "==", payload.message_id).stream())[0].reference
            team.update({"members": ArrayUnion([payload.user_id])})
            team_dict = team.get().to_dict()
            await payload.member.guild.get_channel(team_dict['tc_id']).set_permissions(payload.member, read_messages=True)
            await payload.member.guild.get_channel(team_dict['vc_id']).set_permissions(payload.member, read_messages=True)

def setup(bot):
    bot.add_cog(TeamBuilderCog(bot))
