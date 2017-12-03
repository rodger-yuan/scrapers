
# coding: utf-8

# In[ ]:

from collections import defaultdict
import re

from bs4 import BeautifulSoup, Comment
from urllib.request import urlopen
import pandas as pd

base_url = 'http://www.basketball-reference.com/playoffs/NBA_'
year_start = 1985
year_end = 2016

def get_html(url): #inputs url and returns html
    page =  urlopen(url).read()
    return page

def get_all_playoff_url_dict(year_start, year_end): #gets playoff total url pages
    url_dict = defaultdict(dict)
    for year in range(year_start,year_end+1):
        year_url = base_url + str(year) + '_totals.html'
        url_dict[str(year)] = year_url
    return url_dict

def get_playoff_seedings(year_start, year_end):
    html = get_html('http://www.basketball-reference.com/playoffs/series.html')
    playoff_html_parser = BeautifulSoup(html, 'html.parser')
    team_id = [];
    seeding = [];
    for year in range(year_start, year_end+1):
        year = str(year)
        playoff_year = playoff_html_parser.find_all(string = year)
        for tag in playoff_year[0:8]:
            tag = tag.parent.parent.parent
            wteam = tag.find('td',{'data-stat':'winner'}).find('a').get('href')
            lteam = tag.find('td',{'data-stat':'loser'}).find('a').get('href')
            wteam = wteam[7:10]
            lteam = lteam[7:10]
            team_id.append(year+wteam)
            team_id.append(year+lteam)
            wseed = tag.find('td',{'data-stat':'winner'}).find('span').string
            lseed = tag.find('td',{'data-stat':'loser'}).find('span').string
            seeding.append(wseed[2])
            seeding.append(lseed[2])
    seedings_dict = dict(zip(team_id,seeding))
    return seedings_dict

def parse_all_playoff_url(url): #parses playoff html for year, series, team, player, points and returns dataframe of playoff values
    html = get_html(url)
    playoff_html_parser = BeautifulSoup(html, 'html.parser')
    year = playoff_html_parser.title.string[0:4]
    series_table = playoff_html_parser.find('table').find('tbody')
    player_list = [] #player list for team
    points_list = [] #points list, in same order as player_list
    games_list = [] #number of games played
    team_list = [] #team abbreviation
    team_url_list = [] #team url list
    playoff_ppg_list = [] #playoff ppg
    #regular_ppg_list = [] #regular season ppg
    #team_url_list = [] #url of team
    #seed_list = []
    for tag in series_table.find_all('td',{'data-stat':'player'}): #
        player_name_tag = tag.find('a')
        player_list.append(player_name_tag.string)
    for tag in series_table.find_all('td',{'data-stat':'pts'}): # 
        points_list.append(float(tag.string))
    for tag in series_table.find_all('td',{'data-stat':'g'}): #
        games_list.append(float(tag.string))
    for tag in series_table.find_all('td',{'data-stat':'team_id'}): #
        team_list.append(tag.string)
        link = tag.find('a')
        team_url_list.append(link.get('href'))
    for i in range(len(points_list)):
        playoff_ppg_list.append(points_list[i]/games_list[i])
    playoff_stats_all = pd.DataFrame({'Year' : year,
                                  'Team': team_list,
                                  'Player' : player_list,
                                  'Points' : points_list,
                                  'Games' : games_list,
                                  'Team Url' : team_url_list,
                                  'Playoff PPG' : playoff_ppg_list})
    playoff_stats = playoff_stats_all.sort_values('Points',ascending=False).head(20) #choose number players/year here
    return playoff_stats

def get_reg_season_stats(name_url): #list of [name, url]
    html = get_html(name_url[1])
    reg_season_html_parser = BeautifulSoup(html, 'html.parser')

playoff_stats = parse_all_playoff_url('http://www.basketball-reference.com/playoffs/NBA_1987_totals.html')
#%%

from bs4 import BeautifulSoup, Comment
html = get_html('http://www.basketball-reference.com/teams/LAL/1987.html')
reg_season_html_parser = BeautifulSoup(html, 'html.parser')
comments=reg_season_html_parser.find('div',{'id':'all_per_game'}).find(string=lambda text:isinstance(text,Comment))
table_parser = BeautifulSoup(comments,'html.parser')
table_parser.find('td',{'data-stat':'player'})
#reg_season_html_parser.find(string='Per Game').find_parents('td')

#%%
def parse_all_playoff_urls(html): #gets Series Stats url from All Playoffs url
    all_playoff_html_parser = BeautifulSoup(html, 'html.parser')
    all_playoff_html_tags = all_playoff_html_parser.find_all('a',string='Series Stats')
    all_playoff_html_links = []
    for tag in all_playoff_html_tags:
        all_playoff_html_links.append(tag.get('href'))
    return all_playoff_html_links

def get_all_series_urls(): #series_urls gets all series urls for every playoff year (key = year, value = list of urls)
    series_urls = defaultdict(list)
    for year, all_playoff_url in get_all_playoff_url_dict(year_start,year_end).items(): 
        all_playoff_html = get_html(all_playoff_url)
        series_urls[year] = parse_all_playoff_urls(all_playoff_html)
    return series_urls

def parse_series_url(series_url): #parses Series html for year, series, team, player, points and returns list of DataFrames to be concatenated
    url = 'http://www.basketball-reference.com' + series_url
    html = get_html(url)
    series_html_parser = BeautifulSoup(html, 'html.parser')
    year = series_html_parser.title.string[0:4]
    series = series_html_parser.title.string[5:-27]
    team_ids = [series_html_parser.find(class_='winner').find('a').string, series_html_parser.find(class_='loser').find('a').string]
    data_concat_list = []
    for team in team_ids:
        series_table = series_html_parser.find('table', {'class': 'stats_table','id': team}).find('tbody')
        player_list = [] #player list for team
        points_list = [] #points list, in same order as player_list
        rebounds_list = []
        assists_list = []
        steals_list = []
        blocks_list = []
        for tag in series_table.find_all('a'): #Only names have href links
            player_list.append(tag.string)
        for tag in series_table.find_all('td',{'data-stat':'pts'}): # 
            points_list.append(tag.string)
        for tag in series_table.find_all('td',{'data-stat':'trb'}): #
            rebounds_list.append(tag.string)
        for tag in series_table.find_all('td',{'data-stat':'ast'}): #
            assists_list.append(tag.string)
        for tag in series_table.find_all('td',{'data-stat':'stl'}): #
            steals_list.append(tag.string)
        for tag in series_table.find_all('td',{'data-stat':'blk'}): #
            blocks_list.append(tag.string)
        stats_table = pd.DataFrame({ 'Year' : year,
                                     'Series' : series,
                                     'Team': team,
                                     'Player' : player_list,
                                     'Points' : points_list,
                                     'Rebounds' : rebounds_list,
                                     'Assists' : assists_list,
                                     'Steals' : steals_list,
                                     'Blocks' : blocks_list,
                                     'SeriesID' : team_ids[0]+team_ids[1]+year})
        data_concat_list.append(stats_table)
    return data_concat_list 
                                      
def get_series_playoff_data():
    total_data_concat_list = []
    for year, url_list in get_all_series_urls().items():
        for url in url_list:
            total_data_concat_list += parse_series_url(url) #total_concat_list is a list of DataFrames
        print('Completed ' + year)
    all_data_dataframe = pd.concat(total_data_concat_list,ignore_index = True) #concatenate dataframes at the end
    return all_data_dataframe
    
get_series_playoff_data().to_csv('1984_2016.csv')

# In[ ]:



