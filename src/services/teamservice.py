from database.teams import Team
from db.models import session_creator, Team
from main import client


class DatabaseError(Exception):
    pass


class TeamService:
    def __init__(self):
        self.collection = client.collection('teams')
        self.documents = self.collection.stream()
        self.teams = []
        for doc in self.documents:
            self.teams.append(Team.from_dict(doc.to_dict()))

    # updates local list
    def __update__(self):
        self.collection = client.collection('teams')
        self.documents = self.collection.stream()
        self.teams = []
        for doc in self.documents:
            self.teams.append(Team.from_dict(doc.to_dict()))

    # allows editing of specific attribute
    def edit_team(self, name="", attribute="", value=""):
        try:
            team = self.get_by_name(name)
            if team.name is not False:
                result = self.collection.document(name).set(team.to_dict())
                if result:
                    print("Successfully added!")
                else:
                    raise DatabaseError
                document = list(self.collection.where("name", "==", name).stream())[0].reference
                document.update({attribute: value})
                print("Team has been edited")
                self.__update__()
                return True
        except IndexError:
            # return false if attribute/team doesn't exist
            return False

    # returns team if team exists, if not returns False
    def get_by_name(self, name):
        to_return = False
        for team in self.teams:
            if team.name == name:
                to_return = team
                break
        return to_return

    # deletes team with given name
    def delete_team(self, name):
        document = list(self.collection.where("name", "==", name).stream())[0].reference
        document.delete()
        self.teams.remove(self.get_by_name(name))

    # returns list of team objects
    def get_teams(self):
        return self.teams

    # adds a team
    def add_team(self, team):
        session = session_creator()
        session.add(
            Team(
                discord_user_id=message.author.id,
                is_team_channel=team_channel.is_team_channel(message.channel),
            )
        )
        session.commit()
        session.close()
