class Team(object):
    def __init__(self, name, emoji, vc_id, tc_id, join_message_id, members=[], project=""):
        """
        :param name: The team name
        :param emoji: The team's emoji
        :param vc_id: The ID of the team's voice channel
        :param tc_id: The ID of the team's text channel
        :param join_message_id: The ID of the join message that users react to to join the team
        :param members: A list of team members by member ID
        :param project: A description of the team's project
        """
        self.name = name
        self.emoji = emoji
        self.members = members
        self.vc_id = vc_id
        self.tc_id = tc_id
        self.join_message_id = join_message_id
        self.project = project

    @staticmethod
    def from_dict(source):
        team = Team(source['name'], source['emoji'], source["vc_id"], source["tc_id"], source["join_message_id"])

        if 'members' in source:
            team.members = source["members"]

        if 'project' in source:
            team.project = source["project"]

        return team

    def to_dict(self):
        dest = {
            'name': self.name,
            'emoji': self.emoji,
            'vc_id': self.vc_id,
            'tc_id': self.tc_id,
            'join_message_id': self.join_message_id
        }

        if self.members:
            dest['members'] = self.members

        if self.project:
            dest["project"] = self.project

        return dest

    def __repr__(self):
        return (
            f"City(name={self.name}, country={self.emoji}, vc_id={self.vc_id}, vc_id={self.tc_id}, join_message_id={self.join_message_id}, members={self.members}, project={self.project})"
        )
