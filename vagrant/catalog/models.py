import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String, Text, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref, sessionmaker
from sqlalchemy import create_engine
from datetime import datetime

Base = declarative_base()
    

class Category(Base):
    """Category has a name and is backreffed to items"""
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True)
    name = Column(String(80))

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Category %r>' % self.name
    def serialize(self):
       """Return object data in easily serializeable format"""
       return {
           'name'         : self.name,
           'id'         : self.id,
       }


class Item(Base):
    """this class holds an item with a body and a url to link to"""
    __tablename__ = 'item'
    id = Column(Integer, primary_key=True)
    title = Column(String(80))
    url = Column(String(200))
    body = Column(Text)
    pub_date = Column(DateTime)

    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship('Category',
    backref=backref('Items'))

    def __init__(self, title, body, url, category, pub_date=None):
        self.title = title
        self.body = body
        self.url = url
        if pub_date is None:
            pub_date = datetime.utcnow()
        self.pub_date = pub_date
        self.category = category

    def __repr__(self):
        return '<Item %r>' % self.title

    def serialize(self):
       """Return object data in easily serializeable format"""
       return {
           'title'         : self.title,
           'body'         : self.body,
           'id'         : self.id,
           'url'         : self.url,
           'pub_date'         : self.pub_date,
           'categoryID'         : self.category.id,
       }

engine = create_engine('sqlite:///catalog.db')
 

Base.metadata.create_all(engine)

# if run directly init data
if __name__ == '__main__':
    print("Wiping Existing catalog DB and creating sample data")
    engine = create_engine('sqlite:///catalog.db') 
    Base.metadata.bind = engine
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    session.query(Category).delete()
    session.query(Item).delete()
    session.commit()
    category = Category("Snakes")
    session.add(category)
    session.commit()
    items = [Item("Python","Pythons are snakes","http://en.wikipedia.org/wiki/Python", category),Item("Anaconda","Anaconda are snakes","http://en.wikipedia.org/wiki/Anaconda",category),
             Item("Vipers","Vipers are snakes","http://en.wikipedia.org/wiki/Viperidae",category)]
    for item in items:
        session.add(item)
    session.commit()
    category = Category("Pens")
    session.add(category)
    session.commit()
    items = [Item("Fountain","Fountain pens are pens","http://en.wikipedia.org/wiki/Fountain_pen",category),Item("Ballpoint","Ballpoint pens are pens","http://en.wikipedia.org/wiki/Ballpoint_pen",category),
             Item("Felt","Felt pens are pens","http://en.wikipedia.org/wiki/Marker_pen",category)]
    for item in items:
        session.add(item)
    session.commit()
    print("Sample Data Done")
