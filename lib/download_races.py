# load dependencies
import pandas as pd
import numpy as np
from pprint import pprint
import requests
from datetime import datetime, timedelta
from tqdm.auto import tqdm # progress bar

path = "~/Documents/01-Computing/Kaggle/02-F1/lib"
Year = 2021

# time for today's race finish
now_date = datetime.now().strftime('%Y-%m-%d')
now_time = datetime.now() + timedelta(hours = 3)
now_time = now_time.strftime('%H:%M:%S')

races = {'season': [],
        'round': [],
        'circuit_id': [],
        'lat': [],
        'long': [],
        'country': [],
        'date': [],
        'url': []}

print("Downloading race info...")
for year in tqdm(list(range(1950,Year+1))):
    
    r = requests.get(f'https://ergast.com/api/f1/{year}.json')
    json = r.json()
 
    for item in json['MRData']['RaceTable']['Races']:
        if item['date'] <= now_date:
            if year == Year:
                if item['date'] != now_date and item['time'] <= now_time:
                    try:
                        races['season'].append(int(item['season']))
                    except:
                        races['season'].append(None)

                    try:
                        races['round'].append(int(item['round']))
                    except:
                        races['round'].append(None)

                    try:
                        races['circuit_id'].append(item['Circuit']['circuitName'])
                    except:
                        races['circuit_id'].append(None)

                    try:
                        races['lat'].append(float(item['Circuit']['Location']['lat']))
                    except:
                        races['lat'].append(None)

                    try:
                        races['long'].append(float(item['Circuit']['Location']['long']))
                    except:
                        races['long'].append(None)

                    try:
                        races['country'].append(item['Circuit']['Location']['country'])
                    except:
                        races['country'].append(None)

                    try:
                        races['date'].append(item['date'])
                    except:
                        races['date'].append(None)

                    try:
                        races['url'].append(item['url'])
                    except:
                        races['url'].append(None)        
            else:
                try:
                    races['season'].append(int(item['season']))
                except:
                    races['season'].append(None)

                try:
                    races['round'].append(int(item['round']))
                except:
                    races['round'].append(None)

                try:
                    races['circuit_id'].append(item['Circuit']['circuitName'])
                except:
                    races['circuit_id'].append(None)

                try:
                    races['lat'].append(float(item['Circuit']['Location']['lat']))
                except:
                    races['lat'].append(None)

                try:
                    races['long'].append(float(item['Circuit']['Location']['long']))
                except:
                    races['long'].append(None)

                try:
                    races['country'].append(item['Circuit']['Location']['country'])
                except:
                    races['country'].append(None)

                try:
                    races['date'].append(item['date'])
                except:
                    races['date'].append(None)

                try:
                    races['url'].append(item['url'])
                except:
                    races['url'].append(None)        
        
races = pd.DataFrame(races)

# save race results
races.to_csv(f'{path}/../data/raw_data/races.csv', index = False)

race = pd.read_csv(f'{path}/../data/raw_data/races.csv')
rounds = []
for year in np.array(race.season.unique()):
    rounds.append([year, list(race[race.season == year]['round'])])
    
# RESULTS
results = {'season': [],
           'round':[],
           'circuit_id':[],
           'driver': [],
           'date_of_birth': [],
           'nationality': [],
           'constructor': [],
           'grid': [],
           'status': [],
           'points': [],
           'podium': [],
           'url': [],
           'fastestlap_pos': [],
           'fl_averagespeed': [],
           'fl_lap': [],
           'fl_time': [],
           'time': []}

print("Downloading race results...")
for n in tqdm(list(range(len(rounds)))):
    for i in rounds[n][1]:
        
        r = requests.get(f'http://ergast.com/api/f1/{rounds[n][0]}/{i}/results.json')
        json = r.json()

        for item in json['MRData']['RaceTable']['Races'][0]['Results']:
            try:
                results['season'].append(int(json['MRData']['RaceTable']['season']))
            except:
                results['season'].append(None)

            try:
                results['round'].append(int(json['MRData']['RaceTable']['round']))
            except:
                results['round'].append(None)

            try:
                results['circuit_id'].append(json['MRData']['RaceTable']['Races'][0]['Circuit']['circuitName'])
            except:
                results['circuit_id'].append(None)

            try:
                results['driver'].append(item['Driver']['driverId'])
            except:
                results['driver'].append(None)
            
            try:
                results['date_of_birth'].append(item['Driver']['dateOfBirth'])
            except:
                results['date_of_birth'].append(None)
                
            try:
                results['nationality'].append(item['Driver']['nationality'])
            except:
                results['nationality'].append(None)

            try:
                results['constructor'].append(item['Constructor']['constructorId'])
            except:
                results['constructor'].append(None)

            try:
                results['grid'].append(int(item['grid']))
            except:
                results['grid'].append(None)

            try:
                results['time'].append(int(item['Time']['millis']))
            except:
                results['time'].append(None)
                
            try:
                results['fastestlap_pos'].append(int(item[0]['FastestLap']['rank']))
            except:
                results['fastestlap_pos'].append(None)
                
            try:
                results['fl_lap'].append(int(item[0]['FastestLap']['lap']))
            except:
                results['fl_lap'].append(None)
                
            try:
                results['fl_averagespeed'].append(int(item[0]['FastestLap']['AverageSpeed']['speed']))
            except:
                results['fl_averagespeed'].append(None)
                
            try:
                results['fl_time'].append(int(item[0]['FastestLap']['Time']['time']))
            except:
                results['fl_time'].append(None)
                
            try:
                results['status'].append(item['status'])
            except:
                results['status'].append(None)

            try:
                results['points'].append(int(item['points']))
            except:
                results['points'].append(None)

            try:
                results['podium'].append(int(item['position']))
            except:
                results['podium'].append(None)

            try:
                results['url'].append(json['MRData']['RaceTable']['Races'][0]['url'])
            except:
                results['url'].append(None)

results = pd.DataFrame(results)

# save results
results.to_csv(f'{path}/../data/raw_data/results.csv', index = False)

# DRIVER STANDINGS
driver_standings = {'season': [],
                    'round':[],
                    'driver': [],
                    'driver_points': [],
                    'driver_wins': [],
                   'driver_standings_pos': []}

print("Downloading driver standings...")
for n in tqdm(list(range(len(rounds)))):
    for i in rounds[n][1]:
    
        r = requests.get(f'https://ergast.com/api/f1/{rounds[n][0]}/{i}/driverStandings.json')
        json = r.json()

        for item in json['MRData']['StandingsTable']['StandingsLists'][0]['DriverStandings']:
            try:
                driver_standings['season'].append(int(json['MRData']['StandingsTable']['StandingsLists'][0]['season']))
            except:
                driver_standings['season'].append(None)

            try:
                driver_standings['round'].append(int(json['MRData']['StandingsTable']['StandingsLists'][0]['round']))
            except:
                driver_standings['round'].append(None)
                                         
            try:
                driver_standings['driver'].append(item['Driver']['driverId'])
            except:
                driver_standings['driver'].append(None)
            
            try:
                driver_standings['driver_points'].append(int(item['points']))
            except:
                driver_standings['driver_points'].append(None)
            
            try:
                driver_standings['driver_wins'].append(int(item['wins']))
            except:
                driver_standings['driver_wins'].append(None)
                
            try:
                driver_standings['driver_standings_pos'].append(int(item['position']))
            except:
                driver_standings['driver_standings_pos'].append(None)
            
driver_standings = pd.DataFrame(driver_standings)
driver_standings.to_csv(f'{path}/../data/raw_data/driver_standings.csv', index = False)

# CONSTRUCTOR STANDINGS
constructor_rounds = rounds[8:]
constructor_standings = {'season': [],
                         'round':[],
                         'constructor': [],
                         'constructor_points': [],
                         'constructor_wins': [],
                         'constructor_standings_pos': []}

print("Downloading constructor standings...")
for n in tqdm(list(range(len(constructor_rounds)))):
    for i in constructor_rounds[n][1]:
    
        r = requests.get(f'https://ergast.com/api/f1/{constructor_rounds[n][0]}/{i}/constructorStandings.json')
        json = r.json()

        for item in json['MRData']['StandingsTable']['StandingsLists'][0]['ConstructorStandings']:
            try:
                constructor_standings['season'].append(int(json['MRData']['StandingsTable']['StandingsLists'][0]['season']))
            except:
                constructor_standings['season'].append(None)

            try:
                constructor_standings['round'].append(int(json['MRData']['StandingsTable']['StandingsLists'][0]['round']))
            except:
                constructor_standings['round'].append(None)
                                         
            try:
                constructor_standings['constructor'].append(item['Constructor']['constructorId'])
            except:
                constructor_standings['constructor'].append(None)
            
            try:
                constructor_standings['constructor_points'].append(int(item['points']))
            except:
                constructor_standings['constructor_points'].append(None)
            
            try:
                constructor_standings['constructor_wins'].append(int(item['wins']))
            except:
                constructor_standings['constructor_wins'].append(None)
                
            try:
                constructor_standings['constructor_standings_pos'].append(int(item['position']))
            except:
                constructor_standings['constructor_standings_pos'].append(None)
            
constructor_standings = pd.DataFrame(constructor_standings)
constructor_standings.to_csv(f'{path}/../data/raw_data/constructor_standings.csv', index = False)

# PIT STOPS
# http://ergast.com/mrd/methods/pitstops/

# LAP TIMES
# http://ergast.com/mrd/methods/laps/
race = pd.read_csv(f'{path}/../data/raw_data/races.csv')
rounds = []
for year in np.array(range(2018, Year+1)):
    rounds.append([year, list(race[race.season == year]['round'])])
    
lap_times = {'season': [],
             'round':[],
             'circuit_id': [],
             'lap_number': [],
             'driver': [],
             'lap_position': [],
             'lap_time': []}

print("Downloading driver lap times...")
for n in tqdm(list(range(len(rounds)))):
    print("Year: ", rounds[n][0])
    for i in rounds[n][1]:
        lap_ind = 1
        while lap_ind > 0:
            r = requests.get(f'https://ergast.com/api/f1/{rounds[n][0]}/{i}/laps/{lap_ind}.json')
            json = r.json()
            
            if len(json['MRData']['RaceTable']['Races']) > 0:
                for item in json['MRData']['RaceTable']['Races'][0]['Laps'][0]['Timings']:
                    try:
                        lap_times['season'].append(int(json['MRData']['RaceTable']['Races'][0]['season']))
                    except:
                        lap_times['season'].append(None)

                    try:
                        lap_times['round'].append(int(json['MRData']['RaceTable']['Races'][0]['round']))
                    except:
                        lap_times['round'].append(None)

                    try:
                        lap_times['circuit_id'].append(json['MRData']['RaceTable']['Races'][0]['Circuit']['circuitName'])
                    except:
                        lap_times['circuit_id'].append(None)
                    
                    try:
                        lap_times['lap_number'].append(json['MRData']['RaceTable']['Races'][0]['Laps'][0]['number'])
                    except:
                        lap_times['lap_number'].append(None)
                        
                    try:
                        lap_times['driver'].append(item['driverId'])
                    except:
                        lap_times['driver'].append(None)
                        
                    try:
                        lap_times['lap_position'].append(item['position'])
                    except:
                        lap_times['lap_position'].append(None)
                        
                    try:
                        lap_times['lap_time'].append(item['time'])
                    except:
                        lap_times['lap_time'].append(None)
                lap_ind+=1
            else:
                break
            
lap_times = pd.DataFrame(lap_times)
lap_times.to_csv(f'{path}/../data/raw_data/lap_times.csv', index = False)