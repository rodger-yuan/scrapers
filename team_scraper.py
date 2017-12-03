#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Jun  2 17:12:02 2017

@author: rodgeryuan
"""

from collections import defaultdict

from bs4 import BeautifulSoup
from urllib import urlopen
import pandas as pd

import MySQLdb
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine

url = 'http://www.basketball-reference.com/teams/'

def get_html(url): #inputs url and returns html
    page =  urlopen(url).read()
    return page

def get_all_team_names(url):
    html = get_html(url)
    parser = BeautifulSoup(html,'html.parser')
    team_id = []
    team_name = []
    for tag in parser.find(text = 'Active Franchises').parent.parent.parent.find_all('a'):
        team_id.append(tag['href'][-4:-1])
        team_name.append(tag.string)
    return [team_id,team_name]

team_names = get_all_team_names(url)
#%%
Base = declarative_base()
 
class Teams(Base):
    __tablename__ = 'teams'
    # Here we define columns for the table person
    # Notice that each column is also a normal Python instance attribute.
    team_id = Column(String(3), primary_key=True)
    name = Column(String(250), nullable=False)
    
# Create an engine that stores data in the local directory's
# sqlalchemy_example.db file.
engine = create_engine('mysql+mysqldb://root:rodgera@localhost/basketball')
 
# Create all tables in the engine. This is equivalent to "Create Table"
# statements in raw SQL.
session = sessionmaker()
session.configure(bind=engine)
Base.metadata.create_all(engine)

for team_id in range(len(team_names[0])):
    team = Teams(team_id = team_names[0][team_id],
                   name = team_names[1][team_id])
    s = session()
    s.add(team)
    s.commit()