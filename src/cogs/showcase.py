from discord.ext import commands, tasks
from os import getenv
from utils.gql import GQLService
from utils.subscriptions import subscribe

# noinspection PyPackageRequirements


class ShowcaseCog(commands.Cog, name="Showcase"):
    def __init__(self, bot):
        self.bot = bot
        self._gallery_channel = None
        self._team_log_channel = None
        self.on_member_added.start(self)
        self.on_member_removed.start(self)
        self.on_project_created.start(self)

    def cog_unload(self):
        self.on_member_added.cancel()
        self.on_member_removed.cancel()
        self.on_project_created.cancel()

    async def get_gallery_channel(self):
        if self._gallery_channel is None:
            self._gallery_channel = await self.bot.fetch_channel(int(getenv('CHANNEL_GALLERY')))
        return self._gallery_channel

    async def get_log_channel(self):
        if self._team_log_channel is None:
            self._team_log_channel = await self.bot.fetch_channel(int(getenv('CHANNEL_TEAM_LOG')))
        return self._team_log_channel

    def name(self, project):
        return f"**{project['name']}** ({project['pod']})"

    def link(self, project):
        return f"https://showcase.codeday.org/project/{project['id']}"

    @subscribe(GQLService.member_added_listener)
    async def on_member_added(self, member):
        await (await self.get_log_channel()).send(
            f"{self.name(member['project'])} `+` <@{member['account']['discordId']}> {self.link(member['project'])}"
        )
        if not member['account']['discordId'] or not member['project']['pod']:
            return

    @subscribe(GQLService.member_removed_listener)
    async def on_member_removed(self, member):
        await (await self.get_log_channel()).send(
            f"{self.name(member['project'])} `-` <@{member['account']['discordId']}> {self.link(member['project'])}"
        )

    @subscribe(GQLService.team_created_listener)
    async def on_project_created(self, project):
        member_tag = ""
        if ('members' in project and project['members'] is not None and len(project['members']) > 0 and
                'account' in project['members'][0] and 'discordId' in project['members'][0]['account']):
            member_tag = f"_To join, talk to: <@{project['members'][0]['account']['discordId']}>_\n"
        await (await self.get_gallery_channel()).send(
            f"**{project['name']}** ({project['type'].lower()})\n{member_tag}{self.link(project)}\n{project['description']}"
        )
        await (await self.get_log_channel()).send(
            f"{self.name(project)} `create` {self.link(project)}"
        )


def setup(bot):
    bot.add_cog(ShowcaseCog(bot))
