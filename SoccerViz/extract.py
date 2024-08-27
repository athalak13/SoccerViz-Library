#import libraries
import re
import json
import pandas as pd
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService



def get_html_selenium(url):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument(
        'user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15')

    driver = webdriver.Chrome(options=options)
    driver.get(url)

    html = driver.page_source
    driver.quit()
    return html

def extract_data(html):
    regex_pattern = r'(?<=require\.config\.params\["args"\].=.)[\s\S]*?;'
    match = re.search(regex_pattern, str(html))
    if not match:
        raise ValueError("No match found for the regex pattern.")
    data_txt = match.group(0)

    # Clean up the text if necessary
    data_txt = data_txt.replace('matchId', '"matchId"')
    data_txt = data_txt.replace('matchCentreData', '"matchCentreData"')
    data_txt = data_txt.replace('matchCentreEventTypeJson', '"matchCentreEventTypeJson"')
    data_txt = data_txt.replace('formationIdNameMappings', '"formationIdNameMappings"')
    data_txt = data_txt.replace('};', '}')
    data = json.loads(data_txt)

    return data

def pass_data(url):
    html = get_html_selenium(url)
    data = extract_data(html)

    events_dict = data["matchCentreData"]["events"]

    # Create players DataFrame
    players_home_df = pd.DataFrame(data["matchCentreData"]['home']['players'])
    players_home_df["teamId"] = data["matchCentreData"]['home']['teamId']
    players_away_df = pd.DataFrame(data["matchCentreData"]['away']['players'])
    players_away_df["teamId"] = data["matchCentreData"]['away']['teamId']
    players_df = pd.concat([players_home_df, players_away_df])

    df = pd.DataFrame(events_dict)

    # Create 'eventType' column based on 'type' key if available, else set it to 'Unknown'
    df['eventType'] = df.apply(lambda row: row['type']['displayName'] if 'type' in row else 'Unknown', axis=1)

    # Create 'outcomeType' column based on 'outcomeType' key if available, else set it to 'Unknown'
    df['outcomeType'] = df.apply(lambda row: row['outcomeType']['displayName'] if 'outcomeType' in row else 'Unknown', axis=1)

    # Filter only passes
    passes_ids = df.index[df['eventType'] == 'Pass']
    df_passes = df.loc[
        passes_ids, ["id", "x", "y", "endX", "endY", "teamId", "playerId", "eventType", "outcomeType", "minute"]]

    return df_passes


def player_data(url):
    html = get_html_selenium(url)
    data = extract_data(html)


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

    return players_df


def shots(understat_url):
    response = requests.get(understat_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    ugly_soup = str(soup)
    match = re.search("var shotsData .*= JSON.parse\('(.*)'\)",
                      ugly_soup)
    shots_data = match.group(1)
    shots_data = json.loads(
        shots_data.encode('utf-8').decode('unicode_escape'))
    home_df = pd.DataFrame(shots_data['h'])
    away_df = pd.DataFrame(shots_data['a'])


    return home_df,away_df


