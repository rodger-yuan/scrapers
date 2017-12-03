
# coding: utf-8

# In[ ]:

from collections import defaultdict
import re

from bs4 import BeautifulSoup
from urllib import urlopen
import pandas as pd

base_url = 'http://www.basketball-reference.com/leagues/NBA_'
year_start = 1985
year_end = 2017

def get_html(url): #inputs url and returns html
    page =  urlopen(url).read()
    return page

def get_all_name_url_dict(year_start, year_end): #gets dict of all player-stat year urls
    url_dict = defaultdict(dict)
    for year in range(year_start,year_end+1):
        year_url = base_url + str(year) + '_per_game.html'
        url_dict[str(year)] = year_url
    return url_dict

def parse_player_stats_html(html): #
    player_stats_parser = BeautifulSoup(html, 'html.parser')
    player_list = []
    player_list_temp = []
    player_id_list = []
    player_id_list_temp = []             
    for tag in player_stats_parser.find_all('td',{'data-stat':'player'}): #
        player_name_tag = tag.find('a')
        player_list_temp.append(player_name_tag.string)
        player_id_attr = tag["data-append-csv"]
        player_id_list_temp.append(player_id_attr)
    for index in range(len(player_id_list_temp)): #remove duplicates
        if player_id_list_temp[index] not in player_id_list:
            player_id_list.append(player_id_list_temp[index])
            player_list.append(player_list_temp[index])
    return [player_id_list,player_list]

def combine_player_lists(year_start,year_end): #combining player and player_id lists while removing duplicates
    player_id_list_all = []
    player_name_list_all = []              
    for year, url in get_all_name_url_dict(year_start,year_end).items():
        html = get_html(url)
        player_list = parse_player_stats_html(html)
        player_id_temp = player_list[0]
        player_name_temp = player_list[1]
        for index in range(len(player_id_temp)): #remove duplicates
            if player_id_temp[index] not in player_id_list_all:
                player_id_list_all.append(player_id_temp[index])
                player_name_list_all.append(player_name_temp[index])
    return [player_id_list_all, player_name_list_all]
    
player_list = combine_player_lists(year_start,year_end)
player_list_id = player_list[0]
player_list_name = player_list[1]

player_ids_all = pd.DataFrame({'player id' : player_list[0],
                               'player name': player_list[1]})
    
player_ids_all.to_csv('player_id_1984_2017.csv')

# In[ ]:



