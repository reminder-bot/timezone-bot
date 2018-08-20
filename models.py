from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, BigInteger, Text
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, relationship
import configparser

Base = declarative_base()


class Clock(Base):
    __tablename__ = 'clocks'

    id = Column(Integer, primary_key=True)
    channel_id = Column(BigInteger, unique=True)
    timezone = Column( Text )
    guild_id = Column( BigInteger )

    def __repr__(self):
        return '<Server {}>'.format(self.id)


engine = create_engine('sqlite:///app.db')
Base.metadata.create_all(bind=engine)

Session = sessionmaker(bind=engine)
session = Session()
