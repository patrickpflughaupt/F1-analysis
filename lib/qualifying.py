# load dependencies
import pandas as pd
import numpy as np
from selenium import webdriver
import requests
import bs4
from bs4 import BeautifulSoup
import time
import re
from tqdm.auto import tqdm

# define path
path = "~/Documents/01-Computing/Kaggle/02-F1/lib"
Year = 2021

# load races to get length of this season's races
df_races = pd.read_csv(f'{path}/../data/raw_data/races.csv')
df_races = df_races['date'].to_list()

def grep(pattern,word_list):
    expr = re.compile(pattern)
    return [elem for elem in word_list if expr.match(elem)]
max_this_season = len(grep(pattern='2021', word_list=df_races))

# download qualifying
print("Downloading qualifying results...")
qualifying_results = pd.DataFrame()
for year in tqdm(list(range(1983,Year+1))):
    r = requests.get(f'https://www.formula1.com/en/results.html/{year}/races.html')
    soup = BeautifulSoup(r.text, 'html.parser')
    
    year_links = []
    ind = 1
    for page in soup.find_all('a', attrs = {'class':"resultsarchive-filter-item-link FilterTrigger"}):
        link = page.get('href')
        if f'/en/results.html/{year}/races/' in link: 
            if ind <= max_this_season:
                year_links.append(link)
                ind+=1

    year_df = pd.DataFrame()
    for n, link in list(enumerate(year_links)):
        link = link.replace('race-result.html', 'starting-grid.html')
        df = pd.read_html(f'https://www.formula1.com{link}')
        df = df[0]
        df['season'] = year
        df['round'] = n+1
        for col in df:
            if 'Unnamed' in col:
                df.drop(col, axis = 1, inplace = True)

        year_df = pd.concat([year_df, df])

    qualifying_results = pd.concat([qualifying_results, year_df])

qualifying_results.rename(columns = {'Pos': 'grid_position', 'Driver': 'driver_name', 'Car': 'car',
                                     'Time': 'qualifying_time'}, inplace = True)
qualifying_results.drop('No', axis = 1, inplace = True)
qualifying_results.to_csv(f'{path}/../data/raw_data/qualifying.csv', index = False)