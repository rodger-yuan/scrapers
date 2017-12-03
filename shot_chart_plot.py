#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 14 15:11:07 2017

@author: rodgeryuan
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from mpl_toolkits.mplot3d import Axes3D
from database_tables import *
from matplotlib._png import read_png
from matplotlib.cbook import get_sample_data

#%% SET VARIBLES
num_bins = 15 #number of bins
player_id = 'thompkl01' #player_id
bin_min = 8 #minimum number of shots per bin

#%% GET AVERAGE AND STD DEV FOR EACH BIN

makes_top = [] #all makes
makes_left = []
misses_top = [] #all misses
misses_left = []

session = sessionmaker()
session.configure(bind=engine)

s = session()

query = s.query(Shot_Chart)

s.close()

for item in query:
    if item.result == 1:
        makes_top.append(item.top)
        makes_left.append(item.left)
    if item.result == 0:
        misses_top.append(item.top)
        misses_left.append(item.left)

#%% Arrange data by bins
        
hist_makes, xedges_makes, yedges_makes = np.histogram2d(makes_left, makes_top, bins = num_bins, range = [[0,500],[0,500]])
hist_misses, xedges_misses, yedges_misses = np.histogram2d(misses_left, misses_top, bins = num_bins, range = [[0,500],[0,500]])

hist_avg = np.zeros_like(hist_makes)

for x_coor in np.arange(hist_makes.shape[0]):
    for y_coor in np.arange(hist_makes.shape[1]):
        if hist_makes[x_coor][y_coor] + hist_misses[x_coor][y_coor] != 0:
            hist_avg[x_coor][y_coor] = hist_makes[x_coor][y_coor]/(hist_makes[x_coor][y_coor] + hist_misses[x_coor][y_coor])

hist_avg = hist_avg.flatten()  
           
#Get data from database

session = sessionmaker()
session.configure(bind=engine)

s = session()

all_top = []
all_left = []
makes_p_top, misses_p_top, makes_p_left, misses_p_left = [],[],[],[]

all_shots = s.query(Shot_Chart).filter(Shot_Chart.player_id == player_id)
makes_p = s.query(Shot_Chart).filter(Shot_Chart.player_id == player_id, Shot_Chart.result == 1)
misses_p = s.query(Shot_Chart).filter(Shot_Chart.player_id == player_id, Shot_Chart.result == 0)

s.close()

for item in all_shots:
    all_top.append(item.top + 20)
    all_left.append(item.left + 9)

for item in makes_p:
    makes_p_top.append(item.top + 20)
    makes_p_left.append(item.left + 9)

for item in misses_p:
    misses_p_top.append(item.top + 20)
    misses_p_left.append(item.left + 9)
    
# Shot Chart Figure
fig = plt.figure(figsize = (10,8))
ax = fig.add_subplot(111, projection = '3d')
x, y = np.random.rand(2, 100) * 4
hist, xedges, yedges = np.histogram2d(all_left, all_top, bins=num_bins, range=[[0, 500], [0, 500]])

# Construct arrays for the anchor positions of the 16 bars.
# Note: np.meshgrid gives arrays in (ny, nx) so we use 'F' to flatten xpos,
# ypos in column-major order. For numpy >= 1.7, we could instead call meshgrid
# with indexing='ij'.
xpos, ypos = np.meshgrid(xedges[:-1] + 500.0/num_bins/2, yedges[:-1] + 500.0/num_bins/2)
xpos= xpos.flatten('F')
ypos= ypos.flatten('F')
zpos = np.zeros_like(xpos)

#Get half court image
img = mpimg.imread('nbahalfcourt.png')

X1 = np.arange(0,500,1)
Y1 = np.arange(0,472,1)
X1, Y1 = np.meshgrid(X1,Y1)

# Construct arrays with the dimensions for the 16 bars.
dx = 5 * np.ones_like(zpos)
dy = dx.copy()
dz = hist.flatten()

dx_final, dy_final, dz_final = [],[],[]
xpos_final, ypos_final, zpos_final = [],[],[]

#Choose minimum number of shots per bin

use_index = []

for index in range(len(dz)): 
    if dz[index] > bin_min:
        dx_final.append(dx[index])
        dy_final.append(dy[index])
        dz_final.append(dz[index])
        xpos_final.append(xpos[index])
        ypos_final.append(ypos[index])
        zpos_final.append(zpos[index])
        use_index.append(index)

#Determine fg percentage for the bins of choice

hist_p_makes, xedges_makes, yedges_makes = np.histogram2d(makes_p_left, makes_p_top, bins = num_bins, range = [[0,500],[0,500]])
hist_p_misses, xedges_misses, yedges_misses = np.histogram2d(misses_p_left, misses_p_top, bins = num_bins, range = [[0,500],[0,500]])

hist_p_avg = np.zeros_like(hist_p_makes)

for x_coor in np.arange(hist_p_makes.shape[0]):
    for y_coor in np.arange(hist_p_makes.shape[1]):
        if hist_p_makes[x_coor][y_coor] + hist_p_misses[x_coor][y_coor] != 0:
            hist_p_avg[x_coor][y_coor] = hist_p_makes[x_coor][y_coor]/(hist_p_makes[x_coor][y_coor] + hist_p_misses[x_coor][y_coor])

#Color bars to reflect accuracy compared to the league

color_all = []
hist_p_avg = hist_p_avg.flatten()

for index in use_index:
    if hist_p_avg[index] < hist_avg[index] - 0.1:
        color_all.append('#0000ff')
    if hist_p_avg[index] >= hist_avg[index] - 0.1 and hist_p_avg[index] < hist_avg[index] - 0.06:
        color_all.append('#6666ff')
    if hist_p_avg[index] >= hist_avg[index] - 0.06 and hist_p_avg[index] < hist_avg[index] - 0.02:
        color_all.append('#ccccff')
    if hist_p_avg[index] >= hist_avg[index] - 0.02 and hist_p_avg[index] < hist_avg[index] + 0.02:
        color_all.append('w')
    if hist_p_avg[index] >= hist_avg[index] + 0.02 and hist_p_avg[index] < hist_avg[index] + 0.06:
        color_all.append('#ffcccc')
    if hist_p_avg[index] >= hist_avg[index] + 0.06 and hist_p_avg[index] < hist_avg[index] + 0.1:
        color_all.append('#ff6666')
    if hist_p_avg[index] >= hist_avg[index] + 0.1:
        color_all.append('#ff0000')
        
ax.bar3d(xpos_final, ypos_final, zpos_final, dx_final, dy_final, dz_final, color = color_all, zsort = 'average')
ax.plot_surface(X1, Y1, 0, rstride = 3, cstride = 3, facecolors = img, shade = False)

ax.view_init(elev = 50, azim = 120)

plt.show()

#%%
img = mpimg.imread('nbahalfcourt.png')
fig1 = plt.figure()
ax1 = fig1.add_subplot(111, projection = '3d')

X1 = np.arange(0,500,1)
Y1 = np.arange(0,472,1)
X1, Y1 = np.meshgrid(X1,Y1)
ax1.plot_surface(X1, Y1, 1, rstride = 5, cstride = 5, facecolors = img, shade = False)
plt.axis('on')

plt.show()
