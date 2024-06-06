from sqlalchemy import create_engine, ForeignKey, Boolean, MetaData, Table
from sqlalchemy.engine import URL
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, Integer, String, DateTime, BigInteger
from datetime import datetime, timedelta
from sqlalchemy.orm import relationship
from dotenv import load_dotenv
import os

import settings
from settings import *

load_dotenv()

url = URL.create(
    drivername="postgresql",
    username=os.getenv("DATABASE_USER"),
    password=os.getenv("DATABASE_PASSWORD"),
    host=os.getenv("DATABASE_HOST"),
    database=os.getenv("DATABASE_NAME")
)

Base = declarative_base()

engine = create_engine(url)


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer(), autoincrement=True, primary_key=True)
    telegramUserID = Column(Integer(), unique=True)
    username = Column(String(100), unique=True)
    points = Column(Integer(), nullable=False, default=0)
    fake_points = Column(Integer(), nullable=False, default=DEFAULT_FAKE_POINTS)
    level = Column(Integer(), default=0)
    experience = Column(Integer(), default=0)
    created_on = Column(DateTime(), default=datetime.now)
    updated_on = Column(DateTime(), default=datetime.now, onupdate=datetime.now)
    voice = relationship('Voice')
    cover = relationship('Cover')
    artist = relationship('Artist')
    isPremium = Column(Boolean(), default=False)
    cp = Column(Integer(), default=0)
    lang = Column(String())
    ratingPollID = Column(BigInteger(), unique=True)
    ratingPollMessageID = Column(BigInteger(), unique=True)

class Voice(Base):
    __tablename__ = 'voices'
    id = Column(Integer(), autoincrement=True, primary_key=True)
    telegramUserID = Column(Integer(), ForeignKey('users.telegramUserID'))
    telegramVoiceID = Column(String(), unique=True)
    telegramMessageID = Column(Integer(), unique=True)
    created_on = Column(DateTime(), default=datetime.now)
    updated_on = Column(DateTime(), default=datetime.now, onupdate=datetime.now)
    score = Column(Integer(), default=0)
    place = Column(Integer(), default=None)
    coverID = Column(Integer(), ForeignKey('covers.id'))
    recorded = Column(Boolean(), default=False)
    current = Column(Boolean(), default=False)
    points = Column(Integer(), nullable=False)

class Cover(Base):
    __tablename__ = 'covers'
    id = Column(Integer(), autoincrement=True, primary_key=True)
    artist = Column(String(100))
    song = Column(String(120))
    previewUrl = Column(String(120))
    creator = Column(Integer(), ForeignKey('users.telegramUserID'))
    level = Column(Integer())
    status = Column(String(15))
    wantingPollID = Column(BigInteger(), unique=True)
    ratingPollID = Column(BigInteger(), unique=True)
    ratingPollMessageID = Column(Integer(), unique=True)
    participationsCount = Column(Integer(), default=0)
    created_on = Column(DateTime(), default=datetime.now)
    updated_on = Column(DateTime(), default=datetime.now, onupdate=datetime.now)
    voice = relationship('Voice')
    winner = Column(Integer())
    targetDate = Column(DateTime(), default=datetime.now() + timedelta(seconds=SEC_WANTING))
    postID = Column(BigInteger(), unique=True)
    resultPostID = Column(BigInteger(), unique=True)
    votedCount = Column(Integer(), default=0)
    points = Column(Integer(), nullable=False, default=MIN_POINTS)

    @hybrid_property
    def full_name(self):
        return f'{self.artist}{settings.SPLITTER}{self.song}'


class Artist(Base):
    __tablename__ = 'artists'
    id = Column(Integer(), autoincrement=True, primary_key=True)
    telegramUserID = Column(Integer(), ForeignKey('users.telegramUserID'))
    artist_name = Column(String(120), nullable=False)
    spotifyID = Column(String(120), nullable=False)


class Settings(Base):
    __tablename__ = 'settings'
    id = Column(Integer(), autoincrement=True, primary_key=True)
    name = Column(String(50), nullable=False)
    value = Column(Integer(), nullable=False)

# Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(engine)


Session = sessionmaker(bind=engine)
session = Session()
