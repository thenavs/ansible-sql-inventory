from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Table, ForeignKey
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship
from json import dumps
Base = declarative_base()
host_groups = Table('host_groups', Base.metadata,
    Column('host_id', Integer, ForeignKey('hosts.id')),
    Column('group_id', Integer, ForeignKey('groups.id')))

class Host(Base):
    __tablename__ = 'hosts'
    id     = Column(Integer, primary_key = True)
    name   = Column(String)
    groups = relationship('Group', secondary=host_groups, backref='hosts')
    variables = relationship("Variable")
    @property
    def group_serialize(self):
       return self.name
    @property
    def serialize(self):
       nvars = dict()
       for item in self.variables:
           nvars.update(item.serialize)
       return nvars
    def __repr__(self):
        return '<Host: %s>' % (self.name)

class Group(Base):
    __tablename__ = 'groups'
    id   = Column(Integer, primary_key = True)
    name = Column(String)
    variables = relationship("Variable")
    @property
    def serialize(self):
       return {
           'hosts' :self.serialize_hosts,
           'vars'  :self.serialize_vars
       }
    @property
    def serialize_hosts(self):
       return [ item.group_serialize for item in self.hosts]
    @property
    def serialize_vars(self):
       nvars = dict()
       for item in self.variables:
           nvars.update(item.serialize)
       return nvars

    def __repr__(self):
        return '<Group: %s>' % (self.name)

class Variable(Base):
    ''' Can be attached to either a Host or Group '''
    __tablename__ = 'variables'
    id    = Column(Integer, primary_key = True)
    name  = Column(String)
    value = Column(String)
    group_id = Column(Integer, ForeignKey('groups.id'))
    host_id  = Column(Integer, ForeignKey('hosts.id'))

    @property
    def serialize(self):
       return {
           self.name:self.value
       }
    def __repr__(self):
        return '<Variable: %s = %s>' % (self.name, self.value)


