import random

from discord.ext import commands


class IdeaCog(commands.Cog, name="Idea Generator"):
    """A cog where all the idea generator commands live"""

    def __init__(self, bot):
        self.bot = bot

    def generate_idea(self):
        base = ['An app', 'A website', 'A game', 'A button', 'A company', 'A Chrome Extension', 'An educational video',
                'A TV remote', 'A to-do list', 'A computer virus']
        game_genres = ['dungeon crawler', 'platformer', 'tic-tac-toe', 'first-person shooter', 'battle royale', 'co-op',
                       'puzzle', 'rhythm', 'bullet hell', 'choose your own adventure', 'survival', 'simulation',
                       'Tetris', 'Fortnite']
        existing_product = ['Facebook', 'Google Maps', 'YouTube', 'MySpace', 'The New York Stock Exchange', 'CodeDay',
                            'Tinder', 'GitHub', 'Twitter', 'VSCode', 'Bitcoin', 'Figma', 'Google Docs', 'StackOverflow']
        group_of_people = ['geologists', 'accountants', 'influencers', 'gamer girls', 'cats', 'catboys',
                           'conspiracy theorists', 'actors', 'AI researchers', 'nerds', 'Americans', 'the proletariat',
                           'software engineers', 'java developers', 'twitch mods', 'CodeDay volunteers',
                           'environmentalists', 'weebs', 'muiscians', 'chefs', 'doctors', 'baristas']
        twist_leadin = ['except', 'but', 'only', 'however']
        twist = ['everything is purple tinted', 'nobody has any feet', 'to speed up commuting',
                 'it uses procedural generation', 'it makes people win the lottery', 'built with blockchain',
                 'triangles don\'t exist', 'it validates credit cards', 'with machine learning', 'in zero gravity',
                 'the floor is lava', 'nobody speaks the same language', 'based off folklore', 'it\'s a podcast']
        extras = ['robots', 'martians', 'time travel', 'machine learning', 'anime', 'breathing rubber ducks',
                  'superheroes', 'pottery experts']
        suffixes = ['Beat that, Zuckerberg!', 'funded by ads', 'using socket.io']
        adjectives = ['A fun', 'An unparallelled', 'An innovative', 'A']
        templates = [f'{random.choice(base)}, {random.choice(twist_leadin)} {random.choice(twist)}',
                     f'{random.choice(existing_product)}, but only for {random.choice(group_of_people)}',
                     f'{random.choice(existing_product)}, {random.choice(twist_leadin)} {random.choice(twist)}',
                     f'{random.choice(adjectives)} {random.choice(game_genres)} game, with {random.choice(extras)}!',
                     f'{random.choice(extras)}, {random.choice(twist_leadin)} {random.choice(twist)}, for {random.choice(group_of_people)}',
                     f'{random.choice(existing_product)}, only it\'s a {random.choice(game_genres)} game']
        if random.randint(1,25) == 1:
            return random.choice(templates) + ' - ' + random.choice(suffixes)
        else:
            return random.choice(templates)

    @commands.command()
    async def idea(self, ctx):
        """comes up with an idea for your next amazing project!"""
        await ctx.send(self.generate_idea())


def setup(bot):
    bot.add_cog(IdeaCog(bot))
