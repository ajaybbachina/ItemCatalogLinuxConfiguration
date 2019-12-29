import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
    """Class to create the table 'user'."""

    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))
    is_authenticated = Column(String(250), unique=False, default=True)


class Category(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)

    @property
    def serialize(self):

        return {
            'id': self.id,
            'name': self.name,
        }


class CategoryItem(Base):
    __tablename__ = 'category_items'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    description = Column(String(250))
    category_id = Column(Integer, ForeignKey('categories.id'))
    category = relationship(Category)


# We added this serialize function to be able to send JSON objects in a serializable format
    @property
    def serialize(self):

        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
        }


engine = create_engine('sqlite:///categoryitems.db')


Base.metadata.create_all(engine)
