
# coding: utf-8

# In[ ]:

from collections import defaultdict

from bs4 import BeautifulSoup
from urllib import urlopen
import pandas as pd

import MySQLdb
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine

base_url = 'http://www.basketball-reference.com/players/'
alphabet_list = list('abcdefghijklmnopqrstuvwxyz')

def get_html(url): #inputs url and returns html
    page =  urlopen(url).read()
    return page

def get_all_name_url_dict(alphabet_list): #gets urls for all last names
    url_dict = defaultdict(dict)
    for letter in alphabet_list:
        letter_url = base_url + letter + '/'
        url_dict[letter] = letter_url
    return url_dict

def parse_letter_page_url(url): #takes website url and outputs list of stat lists
    html = get_html(url)                     
    parser = BeautifulSoup(html, 'html.parser')
    player_list = [] #player name
    from_list = [] #player start year
    to_list = [] #player end year
    pos_list = [] #player position
    ht_list = [] #player height
    wt_list = [] #player weight
    birth_date_list = [] #player birth date
    player_id_list = [] #player id
    college_list = [] #player college                 
    for tag in parser.find_all('th',{'data-stat':'player'}): #
        if tag['class'][0] == 'left' :                    
            player_name_tag = tag.find('a')
            player_list.append(player_name_tag.string)
            player_id_attr = tag["data-append-csv"]
            player_id_list.append(player_id_attr)
    for tag in parser.find_all('td',{'data-stat':'year_min'}): #
        from_list.append(tag.string)
    for tag in parser.find_all('td',{'data-stat':'year_max'}): #
        to_list.append(tag.string)  
    for tag in parser.find_all('td',{'data-stat':'pos'}): #
        pos_list.append(tag.string)     
    for tag in parser.find_all('td',{'data-stat':'height'}): #
        ht_list.append(tag.string)
    for tag in parser.find_all('td',{'data-stat':'weight'}): #
        wt_list.append(tag.string) 
    for tag in parser.find_all('td',{'data-stat':'birth_date'}): #
        print tag.string
        if tag.string == None:
            birth_date_list.append(tag.string)
        else:
            birth_date_list.append(tag['csk'])  
    for tag in parser.find_all('td',{'data-stat':'college_name'}): #
        college_list.append(tag.string)  
#    for index in range(len(player_id_list_temp)): #remove duplicates
#        if player_id_list_temp[index] not in player_id_list:
#            player_id_list.append(player_id_list_temp[index])
#            player_list.append(player_list_temp[index])
    return [player_id_list,player_list,from_list, to_list, pos_list, ht_list, wt_list, birth_date_list, college_list]

def combine_player_lists(alphabet_list): #combining player and player_id lists while removing duplicates
    player_id_list_all = []
    player_name_list_all = []
    from_list_all = [] #player start year
    to_list_all = [] #player end year
    pos_list_all = [] #player position
    ht_list_all = [] #player height
    wt_list_all = [] #player weight
    birth_date_list_all = [] #player birth date  
    college_list_all = []                  
    for letter, url in get_all_name_url_dict(alphabet_list).items():
        player_list = parse_letter_page_url(url)
        player_id_list_all += player_list[0]
        player_name_list_all += player_list[1]
        from_list_all += player_list[2]
        to_list_all += player_list[3]
        pos_list_all += player_list[4]
        ht_list_all += player_list[5]
        wt_list_all += player_list[6]
        birth_date_list_all += player_list[7]
        college_list_all += player_list[8]
    return [player_id_list_all,player_name_list_all,from_list_all, to_list_all, pos_list_all, ht_list_all, wt_list_all, birth_date_list_all, college_list_all]

    
player_list = combine_player_lists(alphabet_list)
#player_ids_all = pd.DataFrame({'player id' : player_list[0],
#                               'player name': player_list[1],
#                               'start_year' : player_list[2],
#                               'end_year' : player_list[3],
#                               'position' : player_list[4],
#                               'height' : player_list[5],
#                               'weight' : player_list[6],
#                               'birth_date' : player_list[7],
#                               'college' : player_list[8]})                          
#player_ids_all.to_csv('player_id_1984_2017.csv')

##########################################################
#MySQL
#%%

Base = declarative_base()

def string_to_int(string):
    if string == None:
        return None
    else:
        return int(string)
    
def height_string_to_int(string):
    if string == None:
        return None
    else:
        height_list = string.split('-')
        return 12*int(height_list[0]) + int(height_list[1])
 
class Players(Base):
    __tablename__ = 'players'
    # Here we define columns for the table person
    # Notice that each column is also a normal Python instance attribute.
    player_id = Column(String(9), primary_key=True)
    name = Column(String(250), nullable=False)
    start_year = Column(Integer)
    end_year = Column(Integer)
    position = Column(String(250))
    height = Column(Integer)
    weight = Column(Integer)
    birth_date = Column(String(250))
    college = Column(String(250))
    
# Create an engine that stores data in the local directory's
# sqlalchemy_example.db file.
engine = create_engine('mysql+mysqldb://root:rodgera@localhost/basketball')
 
# Create all tables in the engine. This is equivalent to "Create Table"
# statements in raw SQL.
session = sessionmaker()
session.configure(bind=engine)
Base.metadata.create_all(engine)

for player_id in range(len(player_list[0])):
    player = Players(player_id = player_list[0][player_id], 
                     name = player_list[1][player_id], 
                     start_year = string_to_int(player_list[2][player_id]), 
                     end_year = string_to_int(player_list[3][player_id]), 
                     position = player_list[4][player_id], 
                     height = height_string_to_int(player_list[5][player_id]), 
                     weight = string_to_int(player_list[6][player_id]), 
                     birth_date = player_list[7][player_id], 
                     college = player_list[8][player_id])
    s = session()
    s.add(player)
    s.commit()
# In[ ]:



