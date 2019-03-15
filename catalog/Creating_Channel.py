import sys
import os
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import create_engine
Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    email = Column(String(200), nullable=False)
    picture = Column(String(300))


class LanguageName(Base):
    __tablename__ = 'languagename'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User, backref="languagename")

    @property
    def serialize(self):
        """Return objects data in easily serializeable formats"""
        return {
            'name': self.name,
            'id': self.id
        }


class ChannelName(Base):
    __tablename__ = 'channelname'
    id = Column(Integer, primary_key=True)
    name = Column(String(350), nullable=False)
    owner = Column(String(1500))
    price = Column(String(150))
    rating = Column(String(150))
    date = Column(DateTime, nullable=False)
    languagenameid = Column(Integer, ForeignKey('languagename.id'))
    languagename = relationship(
        LanguageName, backref=backref('channelname', cascade='all, delete'))
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User, backref="channelname")

    @property
    def serialize(self):
        """Return objects data in easily serializeable formats"""
        return {
            'name': self. name,
            'owner': self. owner,
            'price': self. price,
            'rating': self. rating,
            'date': self. date,
            'id': self. id
        }


engin = create_engine('sqlite:///channel.db')
Base.metadata.create_all(engin)
print("database channel created")
