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
    members = relationship("Members", back_populates="team")

    def __str__(self):
        return f'''---
    {self.team_name} ({len(self.members)} members)
    Project: {self.project}
    Channel: <#{self.tc_id}>'''


class Members(Base):
    __tablename__ = "members"

    id = Column(Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey("team.id"))
    member_id = Column(String, nullable=False)
    team = relationship("Team", back_populates="members")


def session_creator() -> Session:
    session = sessionmaker(bind=engine)
    return session()

global_session: Session = session_creator()
