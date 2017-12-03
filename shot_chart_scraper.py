#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon May 29 13:42:44 2017

@author: rodgeryuan
"""

from collections import defaultdict

from bs4 import BeautifulSoup
from urllib import urlopen
import pandas as pd

base_url = 'http://www.basketball-reference.com/boxscores/shot-chart/201705250BOS.html'

def get_html(url): #inputs url and returns html
    page =  urlopen(url).read()
    return page

html = get_html(base_url)