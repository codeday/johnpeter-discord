from discord.ext import commands
import discord
from service_classes.teamservice import TeamService
from urllib import parse
from random import choice


class AdminCommands(commands.Cog):
    """A cog where all the server admin commands live"""

    def __init__(self, bot):
        self.bot = bot
        self.teamservice = TeamService()

    @commands.command(alias=["check_in", "checkin"])
    @commands.has_any_role('Global Staff', 'Staff')
    async def CheckIn(self, ctx):
        self.teamservice.__update__()
        for team in self.teamservice.get_teams():
            url = f"https://www.cognitoforms.com/Srnd1/VirtualCodeDayCheckInForm?entry=%7B%22TeamName%22:%{parse.quote(team.name)}%22,%22ProjectName%22:%22{parse.quote(team.project)}%22%7D"
            title_options = ["How's life?", "Hello, living organism! How do you do this fine [weather:city] day?", "Howdy do!?!"]
            message_options = [
                f"Good? I hope so! Please, go to [this here link]({url}) and tell me so we can keep tabs on how you're doing. Thanks!",
                f"Hope you're programming is going swell! I have orders to have you fill out [this form]({url}) so my fellow staff can keep up to date. Thanks!",
                f"I'm feeling pretty [john:emotion]! Please, tell me how you are feeling about your project [here]({url}). Bye for now!"
            ]
            embed = discord.Embed(title=choice(title_options),
                                  url=url,
                                  description=choice(message_options),
                                  color=0xff686b)
            embed.set_footer(text="John Peter - Professional Human")
            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(AdminCommands(bot))
