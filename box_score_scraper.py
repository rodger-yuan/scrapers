#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon May 29 13:42:44 2017

@author: rodgeryuan
"""

from collections import defaultdict

from bs4 import BeautifulSoup, Comment
from urllib import urlopen
import pandas as pd
import re

import MySQLdb
from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, or_, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine

from database_tables import *
from basketball_functions import *
#%%
#base_url = 'http://www.basketball-reference.com/leagues/NBA_'
#months_list = ['october','november','december','january','february','march','april']
#year = 2017

def get_html(url): #inputs url and returns html
    page =  urlopen(url).read()
    return page

def get_games_url_list(url): #gets the bballref_id of every game in a url page
    html = get_html(url)
    parser = BeautifulSoup(html, 'html.parser')
    csk_list = []
    
    for tag in parser.find_all('th'):
        if tag.string == 'Playoffs':
            return csk_list
        else:
            if tag['class'][0] == 'left':
                csk_list.append(tag['csk'])
    return csk_list

def get_all_games_url(year): #outputs dictionary of all games in year with corresponding url for box score, play-by-play, and shot chart
    url_dict = defaultdict(dict)
    for month in months_list:
       url = base_url + str(year) + '_games-' + month + '.html'
       csk_list = get_games_url_list(url)
       for csk in csk_list:
           url_dict[csk] = [
                   'http://www.basketball-reference.com/boxscores/' + csk + '.html',
                   'http://www.basketball-reference.com/boxscores/pbp/' + csk + '.html',
                   'http://www.basketball-reference.com/boxscores/shot-chart/' + csk + '.html',
                   'http://www.basketball-reference.com/boxscores/plus-minus/' + csk + '.html']
    return url_dict

#url_dict = get_all_games_url(year)

#test_url = 'http://www.basketball-reference.com/boxscores/201704120CHI.html'
#html = get_html(test_url)

#PLAYER BOX SCORE STATS: Outputs all box_score stats

def player_box_score_data(url): #outputs list of lists: 
                                #game_id, player_id, starter, minutes, FG, FGA, 
                                #3P, 3PA, FT, FTA, ORB, DRB, TRB, AST, STL, BLK, 
                                #TOV, PF PTS, plus_minus                            
    html = get_html(url)
    parser = BeautifulSoup(html, 'html.parser')
    game_id = []
    player_id = []
    team_id = []
    starter = []
    minutes = []
    fg = []
    fga = []
    fg3 = []
    fg3a = []
    ft = []
    fta = []
    orb = []
    drb = []
    trb = []
    ast = []
    stl = []
    blk = []
    tov = []
    pf = []
    pts = []
    plus_minus = []
    basic_boxscore_tag = parser.find_all(id = re.compile('all_box_[a-z]*_basic')) #use only basic box scores
    teams = parser.find(class_ = 'scorebox').find_all('a',{'itemprop':'name'})
    counter = 0
    for tag_team in basic_boxscore_tag:
        starters_marker = True
        team = teams[counter]['href'][7:10]
        for tag_player in tag_team.find_all(attrs={'data-stat' : 'player'}):#get player_id and starter information
            if tag_player.string == 'Reserves':
                starters_marker = False
            if tag_player.has_attr('data-append-csv') and tag_player.parent.find('td').has_attr('csk'):
                player_id.append(tag_player['data-append-csv'])
                team_id.append(team)
                if starters_marker == True: #determine iplayer is starter
                    starter.append(True)
                else:
                    starter.append(False)
                tag_player_parent = tag_player.parent
                minutes.append(int(tag_player_parent.find('td',{'data-stat':'mp'})['csk'])) #minutes
                fg.append(int(tag_player_parent.find('td',{'data-stat':'fg'}).string)) #fg
                fga.append(int(tag_player_parent.find('td',{'data-stat':'fga'}).string)) #fga
                fg3.append(int(tag_player_parent.find('td',{'data-stat':'fg3'}).string)) #3p
                fg3a.append(int(tag_player_parent.find('td',{'data-stat':'fg3a'}).string)) 
                ft.append(int(tag_player_parent.find('td',{'data-stat':'ft'}).string)) 
                fta.append(int(tag_player_parent.find('td',{'data-stat':'fta'}).string)) 
                orb.append(int(tag_player_parent.find('td',{'data-stat':'orb'}).string)) 
                drb.append(int(tag_player_parent.find('td',{'data-stat':'drb'}).string)) 
                trb.append(int(tag_player_parent.find('td',{'data-stat':'trb'}).string)) 
                ast.append(int(tag_player_parent.find('td',{'data-stat':'ast'}).string)) 
                stl.append(int(tag_player_parent.find('td',{'data-stat':'stl'}).string)) 
                blk.append(int(tag_player_parent.find('td',{'data-stat':'blk'}).string)) 
                tov.append(int(tag_player_parent.find('td',{'data-stat':'tov'}).string)) 
                pf.append(int(tag_player_parent.find('td',{'data-stat':'pf'}).string)) 
                pts.append(int(tag_player_parent.find('td',{'data-stat':'pts'}).string)) 
                if tag_player_parent.find('td',{'data-stat':'plus_minus'}).string != None:
                    plus_minus.append(int(tag_player_parent.find('td',{'data-stat':'plus_minus'}).string))
                else:
                    plus_minus.append(0)
        counter += 1
    for i in player_id:
        game_id.append(url[46:58])
    return [game_id, player_id, team_id, starter, minutes, fg, fga, fg3, fg3a, ft, fta, orb, drb, trb, ast, stl, blk, tov, pf, pts, plus_minus]

def get_all_games_box_score(url_dict):
    game_id = []
    player_id = []
    team_id = []
    starter = []
    minutes = []
    fg = []
    fga = []
    fg3 = []
    fg3a = []
    ft = []
    fta = []
    orb = []
    drb = []
    trb = []
    ast = []
    stl = []
    blk = []
    tov = []
    pf = []
    pts = []
    plus_minus = []
    for game, url_list in url_dict.items():
        print game
        box_score_data = player_box_score_data(url_list[0])
        game_id = game_id + box_score_data[0]
        player_id += box_score_data[1]
        team_id += box_score_data[2]
        starter += box_score_data[3]
        minutes += box_score_data[4]
        fg += box_score_data[5]
        fga += box_score_data[6]
        fg3 += box_score_data[7]
        fg3a += box_score_data[8]
        ft += box_score_data[9]
        fta += box_score_data[10]
        orb += box_score_data[11]
        drb += box_score_data[12]
        trb += box_score_data[13]
        ast += box_score_data[14]
        stl += box_score_data[15]
        blk += box_score_data[16]
        tov += box_score_data[17]
        pf += box_score_data[18]
        pts += box_score_data[19]
        plus_minus += box_score_data[20]
    return [game_id, player_id, team_id, starter, minutes, fg, fga, fg3, fg3a, ft, fta, orb, drb, trb, ast, stl, blk, tov, pf, pts, plus_minus]
 
#all_box_scores = get_all_games_box_score(url_dict)

# GAME INFO SCRAPING CODE: outputs all_game_info list

def game_info(url_dict): #game_id, home, away, home_1st, home_2nd, home_3rd, home_4th,
                    #home_OT1, home_OT2, home_OT3, home_OT4, home_OT5, home_OT6, home_total
                    #away_1st, away_2nd, away_3rd, away_4th, away_OT1, away_OT2, 
                    #away_OT3, away_OT4, away_OT5, away_OT6, away_total
                    #home_wins, home_losses, away_wins, away_losses
    game_id = []
    home = []
    away = []
    home_score = [[] for i in range(10)] #1st, 2nd, 3rd, 4th, OT1, OT2, OT3, OT4, OT5, OT6
    home_total = []
    away_score = [[] for i in range(10)] #1st, 2nd, 3rd, 4th, OT1, OT2, OT3, OT4, OT5, OT6
    away_total = []
    home_wins = []
    home_losses = []
    away_wins = []
    away_losses = []
    for game_id_val, url_list in url_dict.items():
        game_id.append(game_id_val)
        print game_id_val
        home.append(game_id_val[-3:])
        html = get_html(url_list[0])
        parser = BeautifulSoup(html, 'html.parser')
        comment_parser = BeautifulSoup(parser.find(id = 'all_line_score').find(string=lambda text:isinstance(text,Comment)), 'html.parser')
        number_of_OT = int(comment_parser.find('th', text = 'Scoring')['colspan']) - 5 #find number of OT
        number_of_OT_counter = number_of_OT
        while number_of_OT_counter < 6: #sets unused OT columns to None
            home_score[number_of_OT_counter+4].append(None)
            away_score[number_of_OT_counter+4].append(None)
            number_of_OT_counter += 1
        for tag in comment_parser.find_all('a'): #finds the two score columns where tag.string is the team code
            counter = 0
            if tag.string == game_id_val[-3:]:
                for score_tag in tag.parent.parent.find_all('td')[1:-1]:
                    home_score[counter].append(int(score_tag.string))
                    counter += 1
                home_total.append(int(tag.parent.parent.find_all('td')[-1].string))
            else:
                away.append(tag.string)
                for score_tag in tag.parent.parent.find_all('td')[1:-1]:
                    away_score[counter].append(int(score_tag.string))
                    counter += 1
                away_total.append(int(tag.parent.parent.find_all('td')[-1].string))
        for tag in parser.find_all('a', {'itemprop':"name"}):
            if tag['href'][7:10] == game_id_val[-3:]:
                record = tag.parent.parent.parent.find('div',{'class':'score'}).next_sibling.string.split('-')
                home_wins.append(record[0])
                home_losses.append(record[1])
            else:
                record = tag.parent.parent.parent.find('div',{'class':'score'}).next_sibling.string.split('-')
                away_wins.append(record[0])
                away_losses.append(record[1])
    return [game_id, home, away] + home_score + [home_total] + away_score + [away_total] + [home_wins, home_losses, away_wins, away_losses]
                
#all_game_info = game_info(url_dict)

# PLAY-BY-PLAY SCRAPING CODE

def get_play_by_play(url_dict):
    play_by_play = []
    counter = 0
    for game_id_val, url_list in url_dict.items():
        print game_id_val
        html = get_html(url_list[1])
        parser = BeautifulSoup(html, 'html.parser')
        teams = parser.find(class_ = 'scorebox').find_all('a',{'itemprop':'name'})
        team1 = teams[0]['href'][7:10]
        team2 = teams[1]['href'][7:10]
        pbp = parser.find('table', {'id':'pbp'}).find_all('tr')
        quarter = 0
        for tag in pbp:
            if tag.has_attr('class'): #removes headers
                if tag.has_attr('id'):
                    if quarter < 4:
                        quarter += 1
                    else:
                        quarter += 5.0/12
                continue
            column = tag.find_all('td')
            if column[1].string != None: #removes "start of x quarter" rows
                if 'quarter' in column[1].string:
                    continue
                if 'overtime' in column[1].string:
                    continue
            primary_player_id = None
            secondary_player_id = None
            tertiary_player_id = None
            primary_note = None
            secondary_note = None
            score_change = None
            stat = None
            team1_score = None
            team2_score = None
            time = int(quarter*720) - (60*int(column[0].string.split(':')[0])+int(column[0].string.split(':')[1].split('.')[0]))
            
            #JUMP BALLS
            if column[1].has_attr('colspan'):
                if len(column[1].find_all('a')) > 1:
                    stat = 1
                    jump_counter = 0
                    for jump_players in column[1].find_all('a'):
                        if jump_counter == 0:
                            primary_player_id = jump_players['href'][11:-5] #player 1 who jumped
                        if jump_counter == 1:  
                            secondary_player_id = jump_players['href'][11:-5] #player 2 who jumped
                        if jump_counter == 2:
                            tertiary_player_id = jump_players['href'][11:-5] #player 3 who retrieved
                        jump_counter += 1 
                    play_by_play.append([game_id_val,
                                         primary_player_id,
                                         secondary_player_id,
                                         tertiary_player_id,
                                         team1,
                                         team2,
                                         primary_note,
                                         secondary_note,
                                         score_change,
                                         stat,
                                         team1_score,
                                         team2_score,
                                         time]) 
                    continue
                
            #TEAM 1: PLAYER STATS
            elif column[1].string == None:
                #STAT = 2,3: MAKE SHOT
                if 'makes' in column[1].text and 'pt' in column[1].text:
                    if '2-pt' in column[1].text:
                        stat = 2
                        score_change = 2
                    else:
                        stat = 3
                        score_change = 3
                    make_pt_players = column[1].find_all('a')
                    primary_player_id = make_pt_players[0]['href'][11:-5]
                    if 'ft' not in column[1].text:
                        primary_note = 0;
                    else:
                        primary_note = int(column[1].text[column[1].text.find('ft')-3:column[1].text.find('ft')-1])
                    if 'assist' in column[1].text:
                        secondary_player_id= make_pt_players[1]['href'][11:-5]
                        secondary_note = 1
                #STAT = 5,6: MISS SHOT
                elif 'misses' in column[1].text and 'pt' in column[1].text:
                    if '2-pt' in column[1].text:
                        stat = 5
                    else:
                        stat = 6
                    miss_pt_players = column[1].find_all('a')
                    primary_player_id = miss_pt_players[0]['href'][11:-5]
                    if 'ft' not in column[1].text:
                        primary_note = 0;
                    else:
                        primary_note = int(column[1].text[column[1].text.find('ft')-3:column[1].text.find('ft')-1])
                    if 'block' in column[1].text:
                        secondary_player_id= miss_pt_players[1]['href'][11:-5]
                        secondary_note = 2
                #STAT = 8,9: REBOUND
                elif 'rebound' in column[1].text:
                    if 'Defensive' in column[1].text:
                        stat = 8
                    if 'Offensive' in column[1].text:
                        stat = 9
                    rebound_player = column[1].find('a')
                    primary_player_id = rebound_player['href'][11:-5]
                #STAT = 4,7: FREE THROWS
                elif 'free throw' in column[1].text:
                    if 'makes' in column[1].text:
                        stat = 4
                        score_change = 1
                    if 'misses' in column[1].text:
                        stat = 7
                    free_throw_player = column[1].find('a')
                    primary_player_id = free_throw_player['href'][11:-5]
                    if 'technical' in column[1].text:
                        primary_note = 1
                    if 'flagrant' in column[1].text:
                        primary_note = 2
                #STAT = 10: TURNOVER
                elif 'Turnover' in column[1].text or 'turnover' in column[1].text:
                    stat = 10
                    if 'bad pass' in column[1].text:
                        primary_note = 1
                    if 'lost ball' in column[1].text:
                        primary_note = 2
                    if '3 sec' in column[1].text:
                        primary_note = 3
                    if 'offensive foul' in column[1].text:
                        primary_note = 4
                    if 'traveling' in column[1].text:
                        primary_note = 5
                    if 'lane violation' in column[1].text:
                        primary_note = 6
                    if 'step out of bounds' in column[1].text:
                        primary_note = 7
                    if 'back court' in column[1].text:
                        primary_note = 8
                    if 'dbl dribble' in column[1].text:
                        primary_note = 9 
                    if 'offensive goaltending' in column[1].text:
                        primary_note = 10
                    if 'kicked ball' in column[1].text:
                        primary_note = 11
                    if 'discontinued dribble' in column[1].text:
                        primary_note = 12
                    if 'palming' in column[1].text:
                        primary_note = 13
                    if 'inbound' in column[1].text:
                        primary_note = 14
                    if 'illegal screen' in column[1].text:
                        primary_note = 15
                    if 'swinging elbows' in column[1].text:
                        primary_note = 16
                    if 'jump ball violation' in column[1].text:
                        primary_note = 17
                    if 'illegal assist' in column[1].text:
                        primary_note = 18
                    if 'double personal' in column[1].text:
                        primary_note = 19
                    if 'punched ball' in column[1].text:
                        primary_note = 20
                    turnover_player = column[1].find_all('a')
                    primary_player_id = turnover_player[0]['href'][11:-5]
                    if 'steal by' in column[1].text:
                        secondary_player_id = turnover_player[1]['href'][11:-5]
                    if primary_note == None:
                        print column
                #STAT = 11: FOULS
                elif 'foul' in column[1].text:
                    stat = 11
                    shooting_foul_players = column[1].find_all('a')
                    primary_player_id = shooting_foul_players[0]['href'][11:-5]
                    if 'drawn' in column[1].text:
                        secondary_player_id = shooting_foul_players[1]['href'][11:-5]
                    if 'Shooting' in column[1].text:
                        if 'block' not in column[1].text:
                            primary_note = 1
                        else:
                            primary_note = 7
                    elif 'Personal' in column[1].text:
                        if 'block' in column[1].text:
                            primary_note = 8
                        elif 'take' in column[1].text:
                            primary_note = 11
                        else:
                            primary_note = 2
                    elif 'charge' in column[1].text:
                        primary_note = 3
                    elif 'Offensive' in column[1].text:
                        primary_note = 4
                    elif 'Def 3 sec' in column[1].text:
                        primary_note = 5
                    elif 'Loose ball' in column[1].text:
                        primary_note = 6
                    elif 'Flagrant' in column[1].text:
                        if 'type 1' in column[1].text:
                            primary_note = 9
                        elif 'type 2' in column[1].text:
                            primary_note = 10
                    elif 'Technical foul by' in column[1].text:
                        primary_note = 12
                    elif 'Clear path' in column[1].text:
                        primary_note = 13
                    elif 'Inbound' in column[1].text:
                        primary_note = 14
                    elif 'Away from play' in column[1].text:
                        primary_note = 15
                    if primary_note == None:
                        print column
                        
                #STAT = 12: SUBSTITUTION
                elif 'enters the game' in column[1].text:
                    stat = 12
                    sub_players = column[1].find_all('a')
                    primary_player_id = sub_players[0]['href'][11:-5]
                    secondary_player_id = sub_players[1]['href'][11:-5]
                #STAT = 18: VIOLATIONS
                elif 'Violation' in column[1].text and 'team' not in column[5].text:
                    stat = 18
                    primary_player_id = column[1].find('a')['href'][11:-5]
                    if 'kicked ball' in column[1].text:
                        primary_note = 1
                    if 'lane' in column[1].text:
                        primary_note = 2
                    if 'def goaltending' in column[1].text:
                        primary_note = 3
                    if primary_note == None:
                        print column
                    
            #TEAM 2: PLAYER STATS
            elif column[5].string == None:
                #STAT = 2,3: MAKE SHOT
                if 'makes' in column[5].text and 'pt' in column[5].text:
                    if '2-pt' in column[5].text:
                        stat = 2
                        score_change = 2
                    else:
                        stat = 3
                        score_change = 3
                    make_pt_players = column[5].find_all('a')
                    primary_player_id = make_pt_players[0]['href'][11:-5]
                    if 'ft' not in column[5].text:
                        primary_note = 0;
                    else:
                        primary_note = int(column[5].text[column[5].text.find('ft')-3:column[5].text.find('ft')-1])
                    if 'assist' in column[5].text:
                        secondary_player_id= make_pt_players[1]['href'][11:-5]
                        secondary_note = 1
                #STAT = 5,6: MISS SHOT
                elif 'misses' in column[5].text and 'pt' in column[5].text:
                    if '2-pt' in column[5].text:
                        stat = 5
                    else:
                        stat = 6
                    miss_pt_players = column[5].find_all('a')
                    primary_player_id = miss_pt_players[0]['href'][11:-5]
                    if 'ft' not in column[5].text:
                        primary_note = 0;
                    else:
                        primary_note = int(column[5].text[column[5].text.find('ft')-3:column[5].text.find('ft')-1])
                    if 'block' in column[5].text:
                        secondary_player_id= miss_pt_players[1]['href'][11:-5]
                        secondary_note = 2
                #STAT = 8,9: REBOUND
                elif 'rebound' in column[5].text:
                    if 'Defensive' in column[5].text:
                        stat = 8
                    if 'Offensive' in column[5].text:
                        stat = 9
                    rebound_player = column[5].find('a')
                    primary_player_id = rebound_player['href'][11:-5]
                #STAT = 4,7: FREE THROWS
                elif 'free throw' in column[5].text:
                    if 'makes' in column[5].text:
                        stat = 4
                        score_change = 1
                    if 'misses' in column[5].text:
                        stat = 7
                    free_throw_player = column[5].find('a')
                    primary_player_id = free_throw_player['href'][11:-5]
                    if 'technical' in column[5].text:
                        primary_note = 1
                    if 'flagrant' in column[5].text:
                        primary_note = 2
                #STAT = 10: TURNOVER
                elif 'Turnover' in column[5].text or 'turnover' in column[5].text:
                    stat = 10
                    if 'bad pass' in column[5].text:
                        primary_note = 1
                    if 'lost ball' in column[5].text:
                        primary_note = 2
                    if '3 sec' in column[5].text:
                        primary_note = 3
                    if 'offensive foul' in column[5].text:
                        primary_note = 4
                    if 'traveling' in column[5].text:
                        primary_note = 5
                    if 'lane violation' in column[5].text:
                        primary_note = 6
                    if 'step out of bounds' in column[5].text:
                        primary_note = 7
                    if 'back court' in column[5].text:
                        primary_note = 8
                    if 'dbl dribble' in column[5].text:
                        primary_note = 9 
                    if 'offensive goaltending' in column[5].text:
                        primary_note = 10
                    if 'kicked ball' in column[5].text:
                        primary_note = 11
                    if 'discontinued dribble' in column[5].text:
                        primary_note = 12
                    if 'palming' in column[5].text:
                        primary_note = 13
                    if 'inbound' in column[5].text:
                        primary_note = 14
                    if 'illegal screen' in column[5].text:
                        primary_note = 15
                    if 'swinging elbows' in column[5].text:
                        primary_note = 16
                    if 'jump ball violation' in column[5].text:
                        primary_note = 17
                    if 'illegal assist' in column[5].text:
                        primary_note = 18
                    if 'double personal' in column[5].text:
                        primary_note = 19
                    if 'punched ball' in column[5].text:
                        primary_note = 20
                    turnover_player = column[5].find_all('a')
                    primary_player_id = turnover_player[0]['href'][11:-5]
                    if 'steal by' in column[5].text:
                        secondary_player_id = turnover_player[1]['href'][11:-5]
                    if primary_note == None:
                        print column
                #STAT = 11: FOULS
                elif 'foul' in column[5].text:
                    stat = 11
                    shooting_foul_players = column[5].find_all('a')
                    primary_player_id = shooting_foul_players[0]['href'][11:-5]
                    if 'drawn' in column[5].text:
                        secondary_player_id = shooting_foul_players[1]['href'][11:-5]
                    if 'Shooting' in column[5].text:
                        if 'block' not in column[5].text:
                            primary_note = 1
                        else:
                            primary_note = 7
                    elif 'Personal' in column[5].text:
                        if 'block' in column[5].text:
                            primary_note = 8
                        elif 'take' in column[5].text:
                            primary_note = 11
                        else:
                            primary_note = 2
                    elif 'charge' in column[5].text:
                        primary_note = 3
                    elif 'Offensive' in column[5].text:
                        primary_note = 4
                    elif 'Def 3 sec' in column[5].text:
                        primary_note = 5
                    elif 'Loose ball' in column[5].text:
                        primary_note = 6
                    elif 'Flagrant' in column[5].text:
                        if 'type 1' in column[5].text:
                            primary_note = 9
                        elif 'type 2' in column[5].text:
                            primary_note = 10
                    elif 'Technical foul by' in column[5].text:
                        primary_note = 12
                    elif 'Clear path' in column[5].text:
                        primary_note = 13
                    elif 'Inbound' in column[5].text:
                        primary_note = 14
                    elif 'Away from play' in column[5].text:
                        primary_note = 15
                    if primary_note == None:
                        print column
                #STAT = 12: SUBSTITUTION
                elif 'enters the game' in column[5].text:
                    stat = 12
                    sub_players = column[5].find_all('a')
                    primary_player_id = sub_players[0]['href'][11:-5]
                    secondary_player_id = sub_players[1]['href'][11:-5]
                #STAT = 18: VIOLATIONS
                elif 'Violation' in column[5].text and 'team' not in column[5].text:
                    stat = 18
                    primary_player_id = column[5].find('a')['href'][11:-5]
                    if 'kicked ball' in column[5].text:
                        primary_note = 1
                    if 'lane' in column[5].text:
                        primary_note = 2
                    if 'def goaltending' in column[5].text:
                        primary_note = 3
                    if primary_note == None:
                        print column
                    
            #TEAM STATS:
            else:
                #STAT 13: TEAM OFFENSIVE REBOUND
                if 'Offensive rebound' in column[1].text:
                    stat = 13
                    primary_note = 1
                elif 'Offensive rebound' in column[5].text:
                    stat = 13
                    primary_note = 2
                #STAT 14: TEAM DEFENSIVE REBOUND
                elif 'Defensive rebound' in column[1].text:
                    stat = 14
                    primary_note = 1
                elif 'Defensive rebound' in column[5].text:
                    stat = 14
                    primary_note = 2
                #STAT 15: Turnover
                elif 'Turnover' in column[1].text:
                    stat = 15
                    primary_note = 1
                    if 'shot clock' in column[1].text:
                        secondary_note = 1
                elif 'Turnover' in column[5].text:
                    stat = 15
                    primary_note = 2
                    if 'shot clock' in column[5].text:
                        secondary_note = 1
                #STAT 16: TIMEOUT
                elif 'Official timeout' in column[1].text:
                    stat = 16 
                    primary_note = 3
                elif 'timeout' in column[1].text:
                    stat = 16
                    primary_note = 1
                elif 'timeout' in column[5].text:
                    stat = 16
                    primary_note = 2
                #STAT 17: TEAM TECHNICAL FOUL
                elif 'Technical foul by Team' in column[1].text:
                    stat = 17
                    primary_note = 1
                elif 'Technical foul by Team' in column[5].text:
                    stat = 17
                    primary_note = 2 
                elif 'Violation by Team' in column[1].text:
                    stat = 19
                    primary_note = 1
                elif 'Violation by Team' in column[5].text:
                    stat = 19
                    primary_note = 2
            if stat == None:
                print column
            team1_score = int(column[3].text.split('-')[0])
            team2_score = int(column[3].text.split('-')[1])
            play_by_play.append([game_id_val,
                                 primary_player_id,
                                 secondary_player_id,
                                 tertiary_player_id,
                                 team1,
                                 team2,
                                 primary_note,
                                 secondary_note,
                                 score_change,
                                 stat,
                                 team1_score,
                                 team2_score,
                                 time])
        counter += 1
        print counter
    return play_by_play

#play_by_play = get_play_by_play(url_dict)

# SHOT CHART SCRAPING CODE

def get_shot_chart(url_dict):
    shot_chart_data = []
    counter = 1
    for game_id_val, url_list in url_dict.items():
        print game_id_val + ', ' + str(counter)
        html = get_html(url_list[2])
        parser = BeautifulSoup(html, 'html.parser')
        for team in parser.find_all('img', {'alt':'nbahalfcourt'}):
            play_list = team.find_all('div')
            for play in play_list:
                top = int(play['style'].split('px')[0].split(':')[1])
                left = int(play['style'].split('px')[1].split(':')[1])
                if play['tip'][4] == 'q':
                    quarter = int(play['tip'][0])
                elif play['tip'][4] == 'o':
                    quarter = (int(play['tip'][0]) * 0.4166667) + 4
                time = int(720 * quarter) - 60*int(play['tip'].split(', ')[1].split(' remaining')[0].split(':')[0]) - int(play['tip'].split(', ')[1].split(' remaining')[0].split(':')[1].split('.')[0])
                player_id = play['class'][2].split('-')[1]
                if play['class'][3] == 'make':
                    result = 1
                elif play['class'][3] == 'miss':
                    result = 0
                else:
                    print play['class'][3]
                play_id = play_id_for_shot_chart([game_id_val,time])
                shot_chart_data.append([play_id,game_id_val,player_id,top,left,time,result])
        counter += 1
#        if counter > 5:
#            return shot_chart_data
    return shot_chart_data      

#shot_chart_data = get_shot_chart(url_dict)
#%%
# PLAYER SUBSTITUTIONS CODE
def get_player_subs():
    
    player_subs = []
    
    session = sessionmaker()
    session.configure(bind=engine)
    
    s = session()
    
    #For each game, get starting lineup for each team
    #from play_by_play, make dictionary for each player, with value being list of 
    #lists: [[time_in, time_out], [time_in, time_out]...]
    #from shot_chart, determine if players were in or out for each shot
    for game in s.query(Game_information): #game = game_information query for all games
        starters = defaultdict(dict)
        for box_line in s.query(Box_scores).filter( #for every player box_score
                Box_scores.game_id == game.game_id):
            Qp = [0,0,0,0,0,0,0,0]
            Qp_times = [0,720,1440,2160,2880,3180,3480,3780,4080]
            double_sub = [0,0,0,0,0,0,0,0]
            sub_in = []
            sub_out = []
            if box_line.starter == 1:
                sub_in.append(0)
            for play in s.query(Play_by_play).filter( #If player is subbing in
                    Play_by_play.game_id == game.game_id,
                    Play_by_play.stat == 12,
                    Play_by_play.primary_player_id == box_line.player_id):
                if play.time not in Qp_times:
                    sub_in.append(play.time)
            for play in s.query(Play_by_play).filter( #If player is subbing out
                    Play_by_play.game_id == game.game_id,
                    Play_by_play.stat == 12,
                    Play_by_play.secondary_player_id == box_line.player_id):
                if play.time not in Qp_times:
                    if play.time in sub_in: #eliminate immediate sub in and sub out
                        sub_in.remove(play.time)
                        for index in range(len(Qp_times)):
                            if (play.time > Qp_times[index] and 
                                play.time <= Qp_times[index + 1]):
                                double_sub[index] = 1
                    else:
                        sub_out.append(play.time) 
            for index in range(len(Qp)): #determine if player played in quarter
                for play in s.query(Play_by_play).filter( 
                        Play_by_play.game_id == game.game_id,
                        or_(Play_by_play.primary_player_id == box_line.player_id,
                            Play_by_play.secondary_player_id == box_line.player_id)):
                    if play.stat == 11 and play.primary_note == 12:
                        #Eliminate technical fouls
                        continue
                    if play.time > Qp_times[index] and play.time < Qp_times[index+1]:
                        Qp[index] = 1
                    if (play.stat != 12 and 
                        play.time > Qp_times[index] and
                        play.time <= Qp_times[index+1]):
                        double_sub[index] = 0

            if 1 not in Qp: #player didn't play
                continue
            
            for index in range(len(Qp)): #Appends full quarters
                sub_check = 0
                if Qp[index] == 1 and double_sub[index] == 0:
                    for time in sub_in:
                        if time > Qp_times[index] and time < Qp_times[index+1]:
                            sub_check = 1
                    for time in sub_out:
                        if time > Qp_times[index] and time < Qp_times[index+1]:
                            sub_check = 1
                    if sub_check == 0:
                        if index != 0:
                            sub_in.append(Qp_times[index])
                        sub_out.append(Qp_times[index+1])
            
            sub_in.sort()
            sub_out.sort()
#           
            print game.game_id
            print box_line.player_id
#            
#            print sub_in
#            print sub_out
            
            for index in range(len(Qp)): #if sub_out/sub_in is empty, append the final time value to sub_out
                if Qp[index] == 1:
                    if len(sub_out) == 0:
                        sub_out.append(Qp_times[index+1])
                    if len(sub_in) == 0:
                        sub_in.append(Qp_times[index])
#            
#            print box_line.player_id
#            
#            print sub_in
#            print sub_out
            
            #until here
            
            avail_check = 0 #make sure sub_in[index] < sub_out[index] for all index
                                             
            while avail_check == 0:
                #Go through and check correctness for available values
                for sub_index in range(min(len(sub_out),len(sub_in))):
                    #find sub_in quarter
                    sub_in_quarter = None
                    for time_index in range(len(Qp)):
                        if (sub_out[sub_index] > Qp_times[time_index] and
                            sub_out[sub_index] <= Qp_times[time_index+1]):
                            sub_out_quarter = time_index
                            break
                    for time_index in range(len(Qp)):
                        if (sub_in[sub_index] > Qp_times[time_index] and
                            sub_in[sub_index] <= Qp_times[time_index+1]):
                            sub_in_quarter = time_index
                            break
                    #Now we check for correctness for existing values
                    if (sub_in[sub_index] < sub_out[sub_index] and
                        sub_in[sub_index] < Qp_times[sub_out_quarter]):
                        
                        #If starter tag is incorrect
                        if sub_in_quarter == None:
                            sub_in.remove(0)
                            break
                        
                        #Need to add to sub_out
                        sub_out.insert(sub_index, Qp_times[sub_in_quarter+1])
#                        
#                        print sub_in
#                        print sub_out
#                        
                        break
                    elif sub_in[sub_index] > sub_out[sub_index]:
                        #Need to add to sub_in
                        sub_in.insert(sub_index, Qp_times[sub_out_quarter])
#                        
#                        print sub_in
#                        print sub_out
#                        
                        break
                    if sub_index == min(len(sub_out),len(sub_in)) - 1:
                        avail_check = 1
                        
#            print box_line.player_id
#            
#            print sub_in
#            print sub_out          
#            
            #Fill in gaps to make lists equal length
            if len(sub_out) != len(sub_in):
                for sub_index in range(min(len(sub_out),len(sub_in)),
                                       max(len(sub_out),len(sub_in))):
                    if len(sub_in) > len(sub_out):
                        for time_index in range(len(Qp)):
                            if (sub_in[sub_index] >= Qp_times[time_index] and
                                sub_in[sub_index] < Qp_times[time_index+1]):
                                sub_in_quarter = time_index + 1
                                break  
                        sub_out.insert(sub_index,Qp_times[sub_in_quarter])
                    elif len(sub_out) > len(sub_in):
                        for time_index in range(len(Qp)):
                            if (sub_out[sub_index] > Qp_times[time_index] and
                                sub_out[sub_index] <= Qp_times[time_index+1]):
                                sub_in_quarter = time_index
                                break
                        sub_in.insert(sub_index,Qp_times[sub_in_quarter])
      
            for index in range(len(sub_in)):
                player_subs.append([game.game_id, 
                                    box_line.player_id, 
                                    sub_in[index], 
                                    sub_out[index]])
    s.close()
    
    return player_subs
#%%
#player_subs = get_player_subs(url_dict)

#SHOT CHART WITH TEAMMATES (Includes population)

def get_shot_chart_with_teammates():
    
    session = sessionmaker()
    session.configure(bind=engine)
    
    s = session()
    
    counter = 0
    
    for shot in s.query(Shot_chart): #All shots
        counter += 1
        players_in_shot = 0
        if shot.game_id not in ['201611110BOS', '201701200MEM', '201702130BRK', '201702240CHI', '201703130SAC']: #these are glitchy
            team_id = s.query(Box_scores).filter(Box_scores.game_id == shot.game_id, Box_scores.player_id == shot.player_id)[0].team_id #get team_id of shooter
            for player in s.query(Box_scores).filter(Box_scores.game_id == shot.game_id, Box_scores.team_id == team_id): #find players on same team
                on_court = 0
                for sub in s.query(Player_subs).filter(Player_subs.game_id == shot.game_id, Player_subs.player_id == player.player_id, Player_subs.sub_in < shot.time, Player_subs.sub_out >= shot.time): #find subs for each player
                    if shot.time > sub.sub_in and shot.time <= sub.sub_out:
                        on_court = 1
                        players_in_shot += 1
                        break
                add_value = Shot_with_teammates([shot.shot_id, player.player_id, on_court, team_id])
                s.add(add_value)   
        else:
            continue
        
        if players_in_shot != 5:
            print shot.game_id
            print shot.shot_id
        
        if counter%5000 == 0:
            print counter
            
    s.commit()            
    s.close()
    
#FT WITH TEAMMATES (Includes population)
def get_ft_chart_with_teammates():
    
    session = sessionmaker()
    session.configure(bind=engine)
    
    s = session()
    
    counter = 0
    
    for play in s.query(Play_by_play).filter(or_(Play_by_play.stat == 4, 
                       Play_by_play.stat == 7)): #All fts
        if Play_by_play.game_id not in ['201611110BOS', '201701200MEM', 
        '201702130BRK', '201702240CHI', '201703130SAC']: #these are glitchy
            if s.query(func.count(Box_scores.game_id)).filter(
                    Box_scores.game_id == play.game_id, 
                    Box_scores.player_id == play.primary_player_id)[0][0] > 0:                         
                team_id = s.query(Box_scores).filter(
                        Box_scores.game_id == play.game_id, 
                        Box_scores.player_id == play.primary_player_id)[0].team_id #get team_id of shooter
                for player in s.query(Box_scores).filter(
                        Box_scores.game_id == play.game_id, 
                        Box_scores.team_id == team_id): #find players on same team
                    on_court = 0
                    for sub in s.query(Player_subs).filter(
                            Player_subs.game_id == play.game_id, 
                            Player_subs.player_id == player.player_id, 
                            Player_subs.sub_in <= play.time, 
                            Player_subs.sub_out >= play.time): #find subs for each player
                        if play.time > sub.sub_in and play.time <= sub.sub_out:
                            on_court = 1
                            break
                    add_value = Ft_with_teammates(
                            [play.play_id, player.player_id, on_court, team_id])
                    s.add(add_value)  
        counter += 1
        
        print counter
        print play.play_id
      
    s.commit()                  
    s.close()
    
# PLUS-MINUS SCRAPING CODE

def get_plus_minus(html_dict):
    plus_minus_all = []
    for game_id_val, html in html_dict.items():
        parser = BeautifulSoup(html,'html.parser')
        for player in parser.find_all('div',{'class':'player'}):
            player_string = player.find('span').string
            player_id = player_name_game_id_to_player_id([player_string,game_id_val])
            total_pixel_counter = 1.0
            qtr_counter = 1
            for play in player.next_sibling.next_sibling.find_all('div'):
                on_temp = total_pixel_counter - qtr_counter
                total_pixel_counter += float(play['style'].split(':')[1].split('p')[0])
                if (total_pixel_counter > 251 and total_pixel_counter <= 502):
                    qtr_counter = 2
                elif (total_pixel_counter > 502 and total_pixel_counter <= 753):
                    qtr_counter = 3
                elif (total_pixel_counter > 753):
                    qtr_counter = 4
                off_temp = total_pixel_counter - qtr_counter
                if play.has_attr('class'):
                    on = int(on_temp/1000.0*2880)
                    off = int((off_temp)/1000.0*2880)
                    plus_minus = int(play.text)
                    plus_minus_all.append([game_id_val, player_id, on, off, plus_minus])  
                total_pixel_counter += 1
                if (total_pixel_counter > 251 and total_pixel_counter <= 502):
                    qtr_counter = 2
                elif (total_pixel_counter > 502 and total_pixel_counter <= 753):
                    qtr_counter = 3
                elif (total_pixel_counter > 753):
                    qtr_counter = 4
                print [game_id_val, player_id, on, off, plus_minus]
    return plus_minus_all

#plus_minus_data = get_plus_minus(html_dict)


#%% Populate Game_information with all_game_info list

engine = create_engine('mysql+mysqldb://root:rodgera@localhost/basketball')

session = sessionmaker()
session.configure(bind=engine)

for game in range(len(all_game_info[0])):
    print all_game_info[0][game]
    add_game = Game_information(game_id = all_game_info[0][game], 
                                home = all_game_info[1][game], 
                                away = all_game_info[2][game], 
                                home_1st = all_game_info[3][game], 
                                home_2nd = all_game_info[4][game], 
                                home_3rd = all_game_info[5][game], 
                                home_4th = all_game_info[6][game], 
                                home_OT1 = all_game_info[7][game], 
                                home_OT2 = all_game_info[8][game], 
                                home_OT3 = all_game_info[9][game], 
                                home_OT4 = all_game_info[10][game], 
                                home_OT5 = all_game_info[11][game], 
                                home_OT6 = all_game_info[12][game], 
                                home_total = all_game_info[13][game], 
                                away_1st = all_game_info[14][game], 
                                away_2nd = all_game_info[15][game], 
                                away_3rd = all_game_info[16][game], 
                                away_4th = all_game_info[17][game], 
                                away_OT1 = all_game_info[18][game], 
                                away_OT2 = all_game_info[19][game], 
                                away_OT3 = all_game_info[20][game], 
                                away_OT4 = all_game_info[21][game], 
                                away_OT5 = all_game_info[22][game], 
                                away_OT6 = all_game_info[23][game], 
                                away_total = all_game_info[24][game], 
                                home_wins = all_game_info[25][game], 
                                home_losses = all_game_info[26][game], 
                                away_wins = all_game_info[27][game], 
                                away_losses = all_game_info[28][game])
    s = session()
    s.add(add_game)
    s.commit()
s.close()

#%% Populate Box_scores with all_box_scores list

engine = create_engine('mysql+mysqldb://root:rodgera@localhost/basketball')

session = sessionmaker()
session.configure(bind=engine)

for player in range(len(all_box_scores[0])):
    print all_box_scores[0][player]
    add_player = box_scores(game_id = all_box_scores[0][player],
                            player_id = all_box_scores[1][player],
                            team_id = all_box_scores[2][player],
                            starter = all_box_scores[3][player],
                            minutes = all_box_scores[4][player],
                            fg = all_box_scores[5][player],
                            fga = all_box_scores[6][player],
                            fg3 = all_box_scores[7][player],
                            fg3a = all_box_scores[8][player],
                            ft = all_box_scores[9][player],
                            fta = all_box_scores[10][player],
                            orb = all_box_scores[11][player],
                            drb = all_box_scores[12][player],
                            trb = all_box_scores[13][player],
                            ast = all_box_scores[14][player],
                            stl = all_box_scores[15][player],
                            blk = all_box_scores[16][player],
                            tov = all_box_scores[17][player],
                            pf = all_box_scores[18][player],
                            pts = all_box_scores[19][player],
                            plus_minus = all_box_scores[20][player]) 
    s = session()
    s.add(add_player)
    s.commit()
s.close()

#%%#%% Populate play-by-play with play_by_play list
engine = create_engine('mysql+mysqldb://root:rodgera@localhost/basketball')

session = sessionmaker()
session.configure(bind=engine)

for play in play_by_play:
    print play
    add_play_by_play = Play_by_play(play)
    s = session()
    s.add(add_play_by_play)
    s.commit()
s.close()

#%% Populate Shot_chart with shot_chart_data

for shot in shot_chart_data:
    add_shot = Shot_chart(shot)
    s = session()
    s.add(add_shot)
    s.commit()
s.close()    

#%% Populate plus_minus with plus_minus_data

for item in plus_minus_data:
    add_item = Plus_minus(item)
    s = session()
    s.add(add_item)
    s.commit()
s.close()  

#%% Populate player_subs with player_subs

for item in player_subs:
    add_item = Player_subs(item)
    s = session()
    s.add(add_item)
    s.commit()
s.close()  