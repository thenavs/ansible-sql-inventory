#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
""" hosts.py

    Usage:
       hosts.py --help
       hosts.py (--group-add <group> | --group-del <group> | --host-add <host> [--groups <groups>...]| --host-del <host> | --set <var> <val>| --list | --host <host>|--init)
       hosts.py --set <var> <value> (--group <group> | --host <host> )
"""

import os
import sys
from docopt import docopt
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
try:
    import json
except ImportError:
    import simplejson as json

from models import Host,Group,Variable,Base

class Inventory(object):
    def __init__(self, dbpath="./"):
        engine = create_engine('sqlite:///%s/hosts.sqlite' % dbpath)
        session_maker = sessionmaker()
        session_maker.configure(bind=engine)
        self.session = session_maker()
        self.engine = engine
    def init(self):
        Base.metadata.drop_all(self.engine)
        Base.metadata.create_all(self.engine)
    def list(self):
        x = {}
        for i in self.session.query(Group).all(): x[i.name] = i.serialize
        return json.dumps(x)
    def host(self, host):
        print self.session.query(Host).all()
    def host_add(self,name,groups=[]):
        # does this host exist?
        try:
            host = self.session.query(Host).filter(Host.name == name).one()
        except:
            host = Host(name = name)
            # if we have to make a host, add it to [all]
            host.groups.append(self.session.query(Group).filter(Group.name == 'all').one())
        if groups:
            for group in groups:
                # does the group exist? this throws an exception if the group wasnt found
                group = self.session.query(Group).filter(Group.name == group).one()
                if not group in host.groups: host.groups.append(group)
        self.session.add(host)
        self.session.commit()

    def group_add(self, name):
        try: # backwards exception logic, this raises if none is found, which is good
            self.session.query(Group).filter(Group.name == name).one()
        except:
            self.session.add(Group(name=name))
            self.session.commit()
    def set(self, name, value, group=None, host=None):
        if group:
            item = self.session.query(Group).filter(Group.name == group).one()
        elif host:
            item = self.session.query(Host).filter(Host.name == host).one()

        # find or create the variable
        found = False
        for var in item.variables:
            if var.name == name:
                var.value = value
                self.session.add(var)
                found = True
                break
        if not found:
            var = Variable(name=name,value=value)
            item.variables.append(var)
            self.session.add(item)
        self.session.commit()



if __name__ == "__main__":
    args = docopt(__doc__)
    inventory = Inventory(dbpath=os.path.dirname(os.path.realpath(__file__)))
    if args["--host-add"]:
        inventory.host_add(args['<host>'], args['<groups>'])
    elif args["--group-add"]:
        inventory.group_add(args['<group>'])
    elif args ['--set']:
        inventory.set(name  = args['<var>'],
                      value = args['<value>'],
                      group = args['<group>'],
                      host  = args['<host>'])
    elif args['--init']:
        inventory.init()
    elif args['--list']:
        print inventory.list()
    elif args['--host']:
        inventory(args['<host>'])
