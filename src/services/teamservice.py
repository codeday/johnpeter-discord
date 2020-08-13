from typing import Optional

from sqlalchemy.exc import IntegrityError

from db.models import session_creator, Team, Members


class TeamService:
    @staticmethod
    def edit_team(name, project) -> bool:
        """Takes a name, and a project description"""
        # TODO: does this need a try/catch??
        session = session_creator()
        team = session.query(Team).filter(Team.team_name==name).first()
        if team is not None:
            team.project = project
            session.commit()
            session.close()
            return True
        else:
            session.commit()
            session.close()
            return False

    @staticmethod
    def get_team_by_name(name) -> Optional[Team]:
        """Returns the team with the given name, or none if it doesn't exist"""
        session = session_creator()
        team = session.query(Team).filter(Team.team_name == name).first()
        session.commit()
        session.close()
        return team

    @staticmethod
    def get_team_by_join_message_id(id, session=None) -> Optional[Team]:
        """Returns the team with the given join message id, or none if it doesn't exist"""
        team = session.query(Team).filter(Team.join_message_id == id).first()

        return team

    @staticmethod
    def delete_team_by_name(name) -> bool:
        # TODO: Confirm that member references are deleted as well
        """Deletes team with given id"""
        session = session_creator()
        team = session.query(Team).filter(Team.team_name == name)
        if team is not None:
            team.delete()
            session.commit()
            session.close()
            return True
        else:
            session.commit()
            session.close()
            return False

    @staticmethod
    def get_all_teams() -> list:
        """Returns a list of team objects"""
        session = session_creator()
        teams = session.query(Team).all()
        session.commit()
        session.close()
        return teams

    @staticmethod
    def add_team(name, tc, join_message, project=None) -> bool:
        """Add a new team"""
        try:
            session = session_creator()
            session.add(
                Team(
                    team_name=name,
                    tc_id=tc,
                    join_message_id=join_message,
                    project=project,
                )
            )
            session.commit()
            session.close()
            return True
        except IntegrityError:
            return False

    @staticmethod
    def add_member(team, user_id, session=None):
        sess_flag = False
        if session is None:
            session = session_creator()
            sess_flag = True
        session.add(team)
        team.members.append(Members(member_id=user_id))
        if sess_flag:
            session.commit()
            session.close()

    @staticmethod
    def remove_member(team, user_id, session=None):
        sess_flag = False
        if session is None:
            session = session_creator()
            sess_flag = True
        session.add(team)
        session.query(Members).filter(
            Members.member_id == user_id, Members.team_id == team.id
        ).delete()
        if sess_flag:
            session.commit()
            session.close()
