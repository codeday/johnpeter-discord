from random import choice

import discord


async def send_team_check_in(self, ctx):
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

async def send_team_submit_form(self, ctx):
    """Requests that all teams fill out the project submission form."""
    self.team_service.__update__()
    for team in self.team_service.get_teams():
        try:
            url = f"https://www.cognitoforms.com/Srnd1/VirtualCodeDaySubmission?entry=%7B%22TeamName%22:%22{parse.quote(team.name)}%22,%22ProjectName%22:%22{parse.quote(team.project)}%22%7D"
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
            embed = discord.Embed(title=f"Virtual CodeDay Project Submission Form",
                                  url=url,
                                  description=f"[Please submit your project!]({url})",
                                  color=0xff686b)
            embed.set_thumbnail(url=choice(thumbnail))
            embed.set_footer(text="John Peter - Professional Human")
            await ctx.guild.get_channel(team.tc_id).send(choice(title_options) + " " + choice(message_options),
                                                         embed=embed)
            # await ctx.send(choice(title_options) + " " + choice(message_options), embed=embed)
        except Exception as ex:
            print("I have an exception!" + ex.__str__())
