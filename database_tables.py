#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun Jun  4 18:23:22 2017

@author: rodgeryuan
"""
import MySQLdb
from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine

engine = create_engine('mysql+mysqldb://root:rodgera@localhost/basketball')
session = sessionmaker()
session.configure(bind=engine)

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

Base = declarative_base()
 
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

class Teams(Base):
    __tablename__ = 'teams'
    # Here we define columns for the table person
    # Notice that each column is also a normal Python instance attribute.
    team_id = Column(String(3), primary_key=True)
    name = Column(String(250), nullable=False)
    
class Game_information(Base):
    __tablename__ = 'game_information'
    # Here we define columns for the table person
    # Notice that each column is also a normal Python instance attribute.
    game_id = Column(String(12), primary_key=True)
    home = Column(String(3), ForeignKey('teams.team_id'),nullable = False)
    away = Column(String(3), ForeignKey('teams.team_id'),nullable = False)
    home_1st = Column(Integer)
    home_2nd = Column(Integer)
    home_3rd = Column(Integer)
    home_4th = Column(Integer)
    home_OT1 = Column(Integer)
    home_OT2 = Column(Integer)
    home_OT3 = Column(Integer)
    home_OT4 = Column(Integer)
    home_OT5 = Column(Integer)
    home_OT6 = Column(Integer)
    home_total = Column(Integer)
    away_1st = Column(Integer)
    away_2nd = Column(Integer)
    away_3rd = Column(Integer)
    away_4th = Column(Integer)
    away_OT1 = Column(Integer)
    away_OT2 = Column(Integer)
    away_OT3 = Column(Integer)
    away_OT4 = Column(Integer)
    away_OT5 = Column(Integer)
    away_OT6 = Column(Integer)
    away_total = Column(Integer)
    home_wins = Column(Integer)
    home_losses = Column(Integer)
    away_wins = Column(Integer)
    away_losses = Column(Integer)

class Box_scores(Base):
    __tablename__ = 'box_scores'
    # Here we define columns for the table person
    # Notice that each column is also a normal Python instance attribute.
    id = Column(Integer, primary_key=True)
    game_id = Column(String(12), ForeignKey('Game_information.game_id'),nullable = False)
    player_id = Column(String(9), ForeignKey('players.player_id'),nullable = False)
    team_id = Column(String(3), ForeignKey('teams.team_id'),nullable = False)
    starter = Column(Boolean)
    minutes = Column(Integer)
    fg = Column(Integer)
    fga = Column(Integer)
    fg3 = Column(Integer)
    fg3a = Column(Integer)
    ft = Column(Integer)
    fta = Column(Integer)
    orb = Column(Integer)
    drb = Column(Integer)
    trb = Column(Integer)
    ast = Column(Integer)
    stl = Column(Integer)
    blk = Column(Integer)
    tov = Column(Integer)
    pf = Column(Integer)
    pts = Column(Integer)
    plus_minus = Column(Integer) 

class Play_by_play(Base):#stat key: 1. Jump Ball 2. Make 2 point shot 3. Make 3 point shot
                         #4. Make Free Throw 5. Miss 2 point shot 6. Miss 3 point shot
                         #7. Miss Free Throw 8. Defensive Rebound 9. Offensive Rebound
                         #10. Turnover 11. Foul 12. Substitution 13. Team Offensive Rebound
                         #14. Team Defensive Rebound 15. Turnover by Team 16. Timeout
                         #17. Team Technical 18. Violations 19. Team Violations
                         #
                         #Notes: 
                         #2-3: primary note is distance of shot, secondary player
                         #                  is who assisted the shot
                         #                  secondary note = 1 means assist
                         #
                         #4,7: primary note 1 means technical free throw, 2 means flagrant
                         #
                         #5,6: block: secondary_note = 2
                         #
                         #10: primary notes: 1: bad pass 2: lost ball 3: 3 sec
                         #                  4: offensive foul 5: traveling 6: lane violation 
                         #                  7: out of bounds 8: back court 9: dbl dribble
                         #                  10: offensive goaltending 11: kicked ball 
                         #                  12: discontinued dribble 13: palming
                         #                  14: inbound 15: illegal screen 16: Swinging elbows
                         #                  17: jump ball violation 18: illegal assist
                         #                  19: double personal 20: punched ball
                         #  secondary_player_id = player who stole the ball
                         #
                         #11: primary_note = foul types: 1: Shooting foul 2: Personal 
                         #                              3: Charge 4: Offensive 5: Def 3 sec 
                         #                              6: Loose Ball 7: Shooting block foul
                         #                              8: Personal block foul 9: Flagrant 1
                         #                              10: Flagrant 2 11: Personal take foul
                         #                              12: Technical 13: Clear path 14: Inbound
                         #                              15: Away from play 16: Swinging elbows
                         #          
                         #    
                         #12: primary is player entering, secondary is player subbing out
                         #
                         #13-15: primary note: 1 is Team1, 2 is Team2, 3 is Official
                         #
                         #18: Violations: 1. kicked ball 2. lane 3. def goaltending
                         #                
    __tablename__ = "play_by_play"
 
    play_id = Column(Integer, primary_key=True)
    game_id = Column(String(12), ForeignKey('Game_information.game_id'),nullable = False)
    primary_player_id = Column(String(9), ForeignKey('players.player_id'),nullable = True)
    secondary_player_id = Column(String(9), ForeignKey('players.player_id'),nullable = True)
    tertiary_player_id = Column(String(9), ForeignKey('players.player_id'),nullable = True)
    team1 = Column(String(3), ForeignKey('teams.team_id'),nullable = True)
    team2 = Column(String(3), ForeignKey('teams.team_id'),nullable = True)
    primary_note = Column(Integer)
    secondary_note = Column(Integer)
    score_change = Column(Integer)
    stat = Column(Integer)
    team1_score = Column(Integer)
    team2_score = Column(Integer)
    time = Column(Integer)
 
    #----------------------------------------------------------------------
    def __init__(self, all_play_by_play):
        """"""
        self.game_id = all_play_by_play[0]
        self.primary_player_id = all_play_by_play[1]
        self.secondary_player_id = all_play_by_play[2]
        self.tertiary_player_id = all_play_by_play[3]
        self.team1 = all_play_by_play[4]
        self.team2 = all_play_by_play[5]
        self.primary_note = all_play_by_play[6]
        self.secondary_note = all_play_by_play[7]
        self.score_change = all_play_by_play[8]
        self.stat = all_play_by_play[9]
        self.team1_score = all_play_by_play[10]
        self.team2_score = all_play_by_play[11]
        self.time = all_play_by_play[12]

class Shot_chart(Base):
    __tablename__ = 'shot_chart'
    # Notice that each column is also a normal Python instance attribute.
    shot_id = Column(Integer, primary_key=True)
    play_id = Column(Integer, ForeignKey('play_by_play.play_id'), nullable = True)
    game_id = Column(String(12), ForeignKey('Game_information.game_id'),nullable = False)
    player_id = Column(String(9), ForeignKey('players.player_id'),nullable = False)
    top = Column(Integer)
    left = Column(Integer)
    time = Column(Integer)
    result = Column(Boolean)
    
    def __init__(self, all_shot_chart):
        """"""
        self.play_id = all_shot_chart[0]
        self.game_id = all_shot_chart[1]
        self.player_id = all_shot_chart[2]
        self.top = all_shot_chart[3]
        self.left = all_shot_chart[4]
        self.time = all_shot_chart[5]
        self.result = all_shot_chart[6]
        
class Shot_with_teammates(Base):#teammate_id is id of teammate
                          #on_court: 1 = yes, 0 = no
    __tablename__ = 'shot_with_teammates'
    id = Column(Integer, primary_key=True)
    shot_id = Column(Integer, ForeignKey('shot_chart.shot_id'), nullable = False)
    teammate_id = Column(String(9), ForeignKey('players.player_id'),nullable = False)
    on_court = Column(Boolean)
    team_id = Column(String(3), ForeignKey('teams.team_id'),nullable = False)
    
    def __init__(self, all_shot_with_teammates):
        """"""
        self.shot_id = all_shot_with_teammates[0]
        self.teammate_id = all_shot_with_teammates[1]
        self.on_court = all_shot_with_teammates[2]
        self.team_id = all_shot_with_teammates[3]
        
class Ft_with_teammates(Base):#teammate_id is id of teammate
                          #on_court: 1 = yes, 0 = no
    __tablename__ = 'ft_with_teammates'
    id = Column(Integer, primary_key=True)
    play_id = Column(Integer, ForeignKey('play_by_play.play_id'), nullable = False)
    teammate_id = Column(String(9), ForeignKey('players.player_id'),nullable = False)
    on_court = Column(Boolean)
    team_id = Column(String(3), ForeignKey('teams.team_id'),nullable = False)
    
    def __init__(self, all_ft_with_teammates):
        """"""
        self.play_id = all_ft_with_teammates[0]
        self.teammate_id = all_ft_with_teammates[1]
        self.on_court = all_ft_with_teammates[2]
        self.team_id = all_ft_with_teammates[3]

class Plus_minus(Base):#
    __tablename__ = 'plus_minus'
    id = Column(Integer, primary_key=True)
    game_id = Column(String(12), ForeignKey('Game_information.game_id'),nullable = False)
    player_id = Column(String(9), ForeignKey('players.player_id'),nullable = False)
    on = Column(Integer)
    off = Column(Integer)
    plus_minus = Column(Integer)
    
    def __init__(self, plus_minus_data):
        """"""
        self.game_id = plus_minus_data[0]
        self.player_id = plus_minus_data[1]
        self.on = plus_minus_data[2]
        self.off = plus_minus_data[3]
        self.plus_minus = plus_minus_data[4]
    
class Player_subs(Base):#
    __tablename__ = 'player_subs'
    id = Column(Integer, primary_key=True)
    game_id = Column(String(12), ForeignKey('game_information.game_id'),nullable = False)
    player_id = Column(String(9), ForeignKey('players.player_id'),nullable = False)
    sub_in = Column(Integer)
    sub_out = Column(Integer)
    
    def __init__(self, player_subs):
        """"""
        self.game_id = player_subs[0]
        self.player_id = player_subs[1]
        self.sub_in = player_subs[2]
        self.sub_out = player_subs[3]
        
Base.metadata.create_all(engine)