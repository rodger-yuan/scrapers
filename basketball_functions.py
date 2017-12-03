#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Jun  6 14:56:18 2017

@author: rodgeryuan
"""
import MySQLdb
from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, or_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
from database_tables import Box_scores, Play_by_play, Players, Game_information

def game_id_player_id_to_team_id(game_id_player_id):   
    engine = create_engine('mysql+mysqldb://root:rodgera@localhost/basketball')
 
    # create a Session
    session = sessionmaker()
    session.configure(bind=engine)
    
    s = session()
    
    for team in s.query(Box_scores).filter(Box_scores.game_id == game_id_player_id[0], Box_scores.player_id == game_id_player_id[1]):
        return team.team_id 
    
    s.close()
    
def play_id_for_Shot_chart(info): #info[0] = game_id, info[1] = time:
    engine = create_engine('mysql+mysqldb://root:rodgera@localhost/basketball')
    
    # create a Session
    session = sessionmaker()
    session.configure(bind=engine)
    
    s = session()
    
    play_id_val = s.query(Play_by_play).filter(Play_by_play.game_id == info[0],
                        Play_by_play.time == info[1], or_(Play_by_play.stat == 2, \
                        Play_by_play.stat == 3, Play_by_play.stat == 5, \
                        Play_by_play.stat == 6))
    
    if play_id_val.all() == []:
        play_id_return =  None
    else:
        play_id_return = s.query(Play_by_play).filter(
                Play_by_play.game_id == info[0], Play_by_play.time == info[1], 
                or_(Play_by_play.stat == 2, Play_by_play.stat == 3, 
                    Play_by_play.stat == 5, Play_by_play.stat == 6))[0].play_id
    
    s.close()
    
    return play_id_return

def player_name_game_id_to_player_id(player_name_game_id):
    engine = create_engine('mysql+mysqldb://root:rodgera@localhost/basketball')
 
    # create a Session
    session = sessionmaker()
    session.configure(bind=engine)
    
    s = session()
    
    player_id = s.query(Players).join(Box_scores, Box_scores.player_id == Players.player_id).filter(Box_scores.game_id == player_name_game_id[1],Players.name == player_name_game_id[0])[0].player_id
    
    s.close()

    return player_id            

def game_num_OT(game_id_val)  :
    engine = create_engine('mysql+mysqldb://root:rodgera@localhost/basketball')
 
    # create a Session
    session = sessionmaker()
    session.configure(bind=engine)
    
    s = session()
    
    OT1 = s.query(Game_information).filter(Game_information.game_id == game_id_val)[0].home_OT1
    OT2 = s.query(Game_information).filter(Game_information.game_id == game_id_val)[0].home_OT2
    OT3 = s.query(Game_information).filter(Game_information.game_id == game_id_val)[0].home_OT3
    OT4 = s.query(Game_information).filter(Game_information.game_id == game_id_val)[0].home_OT4
    OT5 = s.query(Game_information).filter(Game_information.game_id == game_id_val)[0].home_OT5
    OT6 = s.query(Game_information).filter(Game_information.game_id == game_id_val)[0].home_OT6 

    s.close()

    if OT1 != None:
        if OT2 != None:
            if OT3 != None:
                if OT4 != None:
                    if OT5 != None:
                        if OT6 != None:
                            numOT = 6
                        else:
                            numOT = 5
                    else:
                        numOT = 4
                else:
                    numOT = 3
            else:
                numOT = 2
        else:
            numOT = 1
    else:
        numOT = 0
    
    return numOT