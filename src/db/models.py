from os import getenv

from sqlalchemy import *
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship

postgres_db = {
    "drivername": "postgres",
    "username": getenv("DB_USERNAME", "postgres"),
    "password": getenv("DB_PASSWORD"),
    "database": getenv("DB_DB", "johnpeter-discord"),
    "host": getenv("DB_HOST", "10.0.3.34"),
    "port": 5432,
}
postgres_url = URL(**postgres_db)
engine = create_engine(postgres_url)
metadata = MetaData()

Base = declarative_base(bind=engine, metadata=metadata)


class Team(Base):
    __tablename__ = "team"

    id = Column(Integer, primary_key=True)
    team_name = Column(String, nullable=False, unique=True)
    tc_id = Column(String, nullable=False)
    join_message_id = Column(String, nullable=False)
    project = Column(String)
    members = relationship("Members", back_populates="team", cascade="all, delete")

    def __str__(self):
        return f"""---
    {self.team_name} ({len(self.members)} members)
    Project: {self.project}
    Channel: <#{self.tc_id}>
    Members: {', '.join(f"<@{m.member_id}>" for m in self.members)}"""


class Members(Base):
    __tablename__ = "members"

    id = Column(Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey("team.id"))
    member_id = Column(String, nullable=False)
    team = relationship("Team", back_populates="members", cascade="all, delete")


class Reactions(Base):
    """ Stores a role id, and a corresponding message ID that it should look for.
    Allows for searching by a message ID and finding all corresponding role IDs
    """

    __tablename__ = "reactions"

    id = Column(Integer, primary_key=True)
    # TODO: These columns really should have been left as ints…
    role_id = Column(BigInteger, nullable=False)
    message_id = Column(BigInteger, nullable=False)
    channel_id = Column(BigInteger, nullable=False)
    # Currently, 0 for all, represents the reaction mode. 0 is the random selection mode, this is here in case we
    # want to do multiple modes.
    reaction_type = Column(BigInteger, nullable=False, default=0)

    @staticmethod
    def groupmsgs():
        """
        groupmsgs = {
            "<message_id>": {
                "channel_id": "<channel_id>",
                "role_ids": ["<role_id>", "<role_id>"]
            }
        }
        """
        session = session_creator()
        groupmsgs_db = session.query(Reactions).filter(Reactions.reaction_type == 0).all()
        groupmsgs = {}

        msg: Reactions
        for msg in groupmsgs_db:
            # We're not sure if message IDs are actually unique or not, this assumes they are, but even still it's
            # not likely there will be a conflict, so we're probably fine...
            if groupmsgs.get(msg.message_id):
                groupmsgs[msg.message_id]["role_ids"] = [*groupmsgs[msg.message_id]["role_ids"], msg.role_id]
            else:
                groupmsgs[msg.message_id] = {}
                groupmsgs[msg.message_id]["channel_id"] = msg.channel_id
                groupmsgs[msg.message_id]["role_ids"] = [msg.role_id]
        print(groupmsgs)
        session.close()
        return groupmsgs


def session_creator() -> Session:
    session = sessionmaker(bind=engine)
    return session()


global_session: Session = session_creator()
