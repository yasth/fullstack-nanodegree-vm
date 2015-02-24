import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref, sessionmaker
from sqlalchemy import create_engine
from datetime import datetime

Base = declarative_base()
    

class Category(Base):
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True)
    name = Column(String(80))

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Category %r>' % self.name

class Item(Base):
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

class Client(Base):
    """stores client details"""
    __tablename__= "client"
    # human readable name, not required
    name = Column(String(40))

    # human readable description, not required
    description = Column(String(400))

    # creator of the client, not required
    user_id = Column(ForeignKey('user.id'))
    # required if you need to support client credential
    user = relationship('User')

    client_id = Column(String(40), primary_key=True)
    client_secret = Column(String(55), unique=True, index=True,
                              nullable=False)

    # public or confidential
    is_confidential = Column(Boolean)

    _redirect_uris = Column(Text)
    _default_scopes = Column(Text)

    @property
    def client_type(self):
        if self.is_confidential:
            return 'confidential'
        return 'public'

    @property
    def redirect_uris(self):
        if self._redirect_uris:
            return self._redirect_uris.split()
        return []

    @property
    def default_redirect_uri(self):
        return self.redirect_uris[0]

    @property
    def default_scopes(self):
        if self._default_scopes:
            return self._default_scopes.split()
        return []

class Grant(Base):
    """stores grant token temporarily"""
    __tablename__="grant"
    id = Column(Integer, primary_key=True)

    user_id = Column(
        Integer, ForeignKey('user.id', ondelete='CASCADE')
    )
    user = relationship('User')

    client_id = Column(
        String(40), ForeignKey('client.client_id'),
        nullable=False,
    )
    client = relationship('Client')

    code = Column(String(255), index=True, nullable=False)

    redirect_uri = Column(String(255))
    expires = Column(DateTime)

    _scopes = Column(Text)

    def delete(self):
        session.delete(self)
        session.commit()
        return self

    @property
    def scopes(self):
        if self._scopes:
            return self._scopes.split()
        return []

class Token(Base):
    """Stores Bearer token for Oauth"""
    __tablename__='token'
    id = Column(Integer, primary_key=True)
    client_id = Column(
        String(40), ForeignKey('client.client_id'),
        nullable=False,
    )
    client = relationship('Client')

    user_id = Column(
        Integer, ForeignKey('user.id')
    )
    user = relationship('User')

    # currently only bearer is supported
    token_type = Column(String(40))

    access_token = Column(String(255), unique=True)
    refresh_token = Column(String(255), unique=True)
    expires = Column(DateTime)
    _scopes = Column(Text)

    def delete(self):
        session.delete(self)
        session.commit()
        return self

    @property
    def scopes(self):
        if self._scopes:
            return self
engine = create_engine('sqlite:///catalog.db')
 

Base.metadata.create_all(engine)

if __name__ == '__main__':
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
