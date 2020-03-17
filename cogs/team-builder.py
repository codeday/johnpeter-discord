import discord
from discord.ext import commands
from main import client
from database_classes.teams import Team
from google.cloud.firestore import DocumentReference, CollectionReference


class DatabaseError(Exception):
    pass


class TeamBuilderCog(commands.Cog, name="Team Builder Commands"):
    """Creates Teams!"""

    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.command()
    @commands.has_role('Global Staff')
    async def add_team(self, ctx: commands.context.Context, team_name: str, team_emoji: discord.Emoji):
        """Adds a new team with the provided name and emoji. Checks for duplicate names"""
        await ctx.send("pong")
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

    @commands.command()
    async def get_teams(self, ctx):
        teams = client.collection("teams")
        for i in teams.stream():
            print(i)
        await ctx.send(f"{'lol'}")

    # @commands.Cog.listener()
    # async def on_message(self, message: discord.Message):
    #     print("test")


def setup(bot):
    bot.add_cog(TeamBuilderCog(bot))
