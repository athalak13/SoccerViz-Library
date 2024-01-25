#import libraries
import re
import json
import pandas as pd
import requests
from bs4 import BeautifulSoup

#function to extract passing data
def pass_data(url,HEADERS):
    response = requests.get(url)
    if response.status_code == 200:
        html = BeautifulSoup(response.text, 'html.parser')
    else:
        response = requests.get(url, headers=HEADERS)
        html = BeautifulSoup(response.text, 'html.parser')

    # Define your regex pattern accurately to match the data you want
    regex_pattern = r'(?<=require\.config\.params\["args"\].=.)[\s\S]*?;'
    data_txt = re.findall(regex_pattern, str(html))[0]

    # Clean up the text if necessary
    data_txt = data_txt.replace('matchId', '"matchId"')
    data_txt = data_txt.replace('matchCentreData', '"matchCentreData"')
    data_txt = data_txt.replace('matchCentreEventTypeJson', '"matchCentreEventTypeJson"')
    data_txt = data_txt.replace('formationIdNameMappings', '"formationIdNameMappings"')
    data_txt = data_txt.replace('};', '}')
    data = data_txt
    data = json.loads(data)

    # Access the JSON data as needed
    event_types_json = data["matchCentreData"]
    formation_mappings = data["formationIdNameMappings"]
    events_dict = data["matchCentreData"]["events"]
    teams_dict = {
        data["matchCentreData"]['home']['teamId']: data["matchCentreData"]['home']['name'],
        data["matchCentreData"]['away']['teamId']: data["matchCentreData"]['away']['name']
    }
    players_dict = data["matchCentreData"]["playerIdNameDictionary"]

    # Create players DataFrame
    players_home_df = pd.DataFrame(data["matchCentreData"]['home']['players'])
    players_home_df["teamId"] = data["matchCentreData"]['home']['teamId']
    players_away_df = pd.DataFrame(data["matchCentreData"]['away']['players'])
    players_away_df["teamId"] = data["matchCentreData"]['away']['teamId']
    players_df = pd.concat([players_home_df, players_away_df])

    events = events_dict

    df = pd.DataFrame(events)

    # Create 'eventType' column based on 'type' key if available, else set it to 'Unknown'
    df['eventType'] = df.apply(lambda row: row['type']['displayName'] if 'type' in row else 'Unknown', axis=1)

    # Create 'outcomeType' column based on 'outcomeType' key if available, else set it to 'Unknown'
    df['outcomeType'] = df.apply(lambda row: row['outcomeType']['displayName'] if 'outcomeType' in row else 'Unknown',
                                 axis=1)

    # Filter only passes
    passes_ids = df.index[df['eventType'] == 'Pass']
    df_passes = df.loc[
        passes_ids, ["id", "x", "y", "endX", "endY", "teamId", "playerId", "eventType", "outcomeType", "minute"]]

    return df_passes

#function to extract players dataframe
def player_data(url, HEADERS):
    response = requests.get(url)
    if response.status_code == 200:
        html = BeautifulSoup(response.text, 'html.parser')
    else:
        response = requests.get(url, headers=HEADERS)
        html = BeautifulSoup(response.text, 'html.parser')

    # Define your regex pattern accurately to match the data you want
    regex_pattern = r'(?<=require\.config\.params\["args"\].=.)[\s\S]*?;'
    data_txt = re.findall(regex_pattern, str(html))[0]

    # Clean up the text if necessary
    data_txt = data_txt.replace('matchId', '"matchId"')
    data_txt = data_txt.replace('matchCentreData', '"matchCentreData"')
    data_txt = data_txt.replace('matchCentreEventTypeJson', '"matchCentreEventTypeJson"')
    data_txt = data_txt.replace('formationIdNameMappings', '"formationIdNameMappings"')
    data_txt = data_txt.replace('};', '}')
    data = data_txt
    data = json.loads(data)

    # Access the JSON data as needed
    event_types_json = data["matchCentreData"]
    formation_mappings = data["formationIdNameMappings"]
    events_dict = data["matchCentreData"]["events"]
    teams_dict = {
        data["matchCentreData"]['home']['teamId']: data["matchCentreData"]['home']['name'],
        data["matchCentreData"]['away']['teamId']: data["matchCentreData"]['away']['name']
    }
    players_dict = data["matchCentreData"]["playerIdNameDictionary"]

    # Create players DataFrame
    players_home_df = pd.DataFrame(data["matchCentreData"]['home']['players'])
    players_home_df["teamId"] = data["matchCentreData"]['home']['teamId']
    players_away_df = pd.DataFrame(data["matchCentreData"]['away']['players'])
    players_away_df["teamId"] = data["matchCentreData"]['away']['teamId']
    players_df = pd.concat([players_home_df, players_away_df])

    events = events_dict

    df = pd.DataFrame(events)

    # Create 'eventType' column based on 'type' key if available, else set it to 'Unknown'
    df['eventType'] = df.apply(lambda row: row['type']['displayName'] if 'type' in row else 'Unknown', axis=1)

    # Create 'outcomeType' column based on 'outcomeType' key if available, else set it to 'Unknown'
    df['outcomeType'] = df.apply(lambda row: row['outcomeType']['displayName'] if 'outcomeType' in row else 'Unknown',
                                 axis=1)

    # Filter only passes
    passes_ids = df.index[df['eventType'] == 'Pass']
    df_passes = df.loc[
        passes_ids, ["id", "x", "y", "endX", "endY", "teamId", "playerId", "eventType", "outcomeType", "minute"]]

    return players_df