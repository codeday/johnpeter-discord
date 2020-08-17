from random import choice
from urllib import parse
from db.models import session_creator, Team

import discord


def generate_embed(title, description, url):
    thumbnails = [
        "https://f1.srnd.org/codeday/virtual-s20/tropical1.png",
        "https://f1.srnd.org/codeday/virtual-s20/tropical2.png",
        "https://f1.srnd.org/codeday/virtual-s20/tropical3.png",
        "https://f1.srnd.org/codeday/virtual-s20/tropical4.png",
        "https://f1.srnd.org/codeday/virtual-s20/tropical5.png",
        "https://f1.srnd.org/codeday/virtual-s20/tropical6.png",
        "https://f1.srnd.org/codeday/virtual-s20/tropical7.png",
    ]
    embed = discord.Embed(
        title=f"{title}", url=url, description=f"[{description}]({url})", color=0xFF686B
    )
    embed.set_thumbnail(url=choice(thumbnails))
    embed.set_footer(text="John Peter - Professional Human")
    return embed


def generate_message(team_name):
    title_options = [
        f"How's life {team_name}?",
        "Hello, living organism! How do you do this fine [weather:city] day?",
        "Howdy do!?!",
    ]
    message_options = [
        f"Good? I hope so! Please, go to the link down there and tell me so we can keep tabs on how you're doing. Thanks!",
        f"Hope you're programming is going swell! I have orders to have you fill out the form down there so my fellow staff can keep up to date. Thanks!",
        f"I'm feeling pretty [john:emotion]! Please, tell me how you are feeling about your project down there. Bye for now!",
    ]
    return choice(title_options) + " " + choice(message_options)


async def send_team_check_in(self, ctx, team):
    """Requests that a specific team fills out the check-in form."""
    try:
        if team.project is not None:
            url = f"https://www.cognitoforms.com/Srnd1/VirtualCodeDayCheckInForm?entry=%7B%22TeamName%22:%22{parse.quote(team.team_name)}%22,%22ProjectName%22:%22{parse.quote(team.project)}%22%7D"
        else:
            url = f"https://www.cognitoforms.com/Srnd1/VirtualCodeDayCheckInForm?entry=%7B%22TeamName%22:%22{parse.quote(team.team_name)}%22,%22ProjectName%22:%22{parse.quote('A game or an app')}%22%7D"
        embed = generate_embed(
            title="Virtual CodeDay Check-In Form",
            description="Let us know how your project is doing!",
            url=url,
        )
        await ctx.guild.get_channel(int(team.tc_id)).send(
            generate_message(team_name=team.team_name), embed=embed
        )
    except Exception as ex:
        raise ex


async def send_team_check_ins(self, ctx):
    """Requests that all teams fill out the check-in form."""
    session = session_creator()
    for team in self.team_service.get_all_teams(session):
        await send_team_check_in(self, ctx, team)
    session.commit()
    session.close()


async def send_team_submit_form(self, ctx, team):
    """Requests that a specific team fills out the project submission form."""
    try:
        if team.project is not None:
            url = f"https://www.cognitoforms.com/Srnd1/VirtualCodeDaySubmission?entry=%7B%22TeamName%22:%22{parse.quote(team.team_name)}%22,%22ProjectName%22:%22{parse.quote(team.project)}%22%7D"
        else:
            url = f"https://www.cognitoforms.com/Srnd1/VirtualCodeDaySubmission?entry=%7B%22TeamName%22:%22{parse.quote(team.team_name)}%22,%22ProjectName%22:%22{parse.quote('A game or an app')}%22%7D"

        embed = generate_embed(
            title="Virtual CodeDay Submission Form",
            description="Please submit your project!",
            url=url,
        )
        await ctx.guild.get_channel(int(team.tc_id)).send(
            generate_message(team_name=team.team_name), embed=embed
        )
    except Exception as ex:
        raise ex


async def send_team_submit_forms(self, ctx):
    """Requests that all teams fill out the project submission form."""
    session = session_creator()
    for team in session.query(Team).all():
        await send_team_submit_form(self, ctx, team)
