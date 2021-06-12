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
        self._pod_channels = {}
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

    async def get_pod_channel(self, pod_id):
        pod_id_to_channel = {
            '610': '853011526335463484',
            '611': '853011528634990642',
            '615': '853011545550225418',
            '616': '853011550380752977',
            '617': '853011554625650739',
            '618': '853011556736040960',
            '619': '853011558745767936',
        }
        if not (pod_id in self._pod_channels):
            self._pod_channels[pod_id] = await self.bot.fetch_channel(int(pod_id_to_channel[pod_id]))
        return self._pod_channels[pod_id]

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

        guild = await self.bot.get_guild('689213562740277361');
        pod_channel = await self.get_pod_channel(member['project']['pod'])
        await pod_channel.send(f"<@{member['account']['discordId']}> joined!")

        discord_member = await guild.fetch_member(member['account']['discordId'])
        if pod_channel:
            await pod_channel.set_permissions(discord_member, send_messages=True, read_messages=True, add_reactions=True, read_message_history=True)

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
