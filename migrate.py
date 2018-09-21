from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, BigInteger, Text
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, relationship
import configparser


url = 'sqlite:///app.db'

dest_url = 'mysql+pymysql://jude@localhost/timezone'
print(dest_url)


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

engine2 = create_engine(dest_url)
Base.metadata.create_all(bind=engine2)

Session = sessionmaker(bind=engine)
session = Session()

Session2 = sessionmaker(bind=engine2)
session_dest = Session2()


for x in session.query(Clock):
    session_dest.merge(x)

for x in session.query(User):
    session_dest.merge(x)

session_dest.commit()
