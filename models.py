from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, BigInteger, Text
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, relationship
import configparser


c = configparser.SafeConfigParser()
c.read('alembic.ini')
url = c.get('alembic', 'sqlalchemy.url')
print(url)


Base = declarative_base()

class Clock(Base):
    __tablename__ = 'clocks'

    id = Column(Integer, primary_key=True)
    channel_id = Column(BigInteger)
    timezone = Column( Text )
    channel_name = Column( Text )
    guild_id = Column( BigInteger )
    message_id = Column( BigInteger, nullable=True )

    def __repr__(self):
        return '<Server {}>'.format(self.id)

class User(Base):
    __tablename__ = 'users'

    map_id = Column(Integer, primary_key=True)
    id = Column(BigInteger)
    timezone = Column( Text )

engine = create_engine(url)
Base.metadata.create_all(bind=engine)

Session = sessionmaker(bind=engine)
session = Session()
