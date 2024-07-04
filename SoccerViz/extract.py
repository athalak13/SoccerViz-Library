#import libraries
import re
import json
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService



def get_html_selenium(url):
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15')

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
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

    # Create players DataFrame
    players_home_df = pd.DataFrame(data["matchCentreData"]['home']['players'])
    players_home_df["teamId"] = data["matchCentreData"]['home']['teamId']
    players_away_df = pd.DataFrame(data["matchCentreData"]['away']['players'])
    players_away_df["teamId"] = data["matchCentreData"]['away']['teamId']
    players_df = pd.concat([players_home_df, players_away_df])

    return players_df


def shots(sofascore_url):
    options = webdriver.ChromeOptions()
    options.set_capability('goog:loggingPrefs', {"performance": "ALL", "browser": "ALL"})
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    driver.set_page_load_timeout(10)

    try:
        driver.get(sofascore_url)
    except Exception as e:
        print(f"Error occurred while loading the page: {e}")
        driver.quit()
        return None

    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    logs_raw = driver.get_log("performance")
    logs = [json.loads(lr['message'])['message'] for lr in logs_raw]

    shotmap = None
    for x in logs:
        if 'shotmap' in x['params'].get('headers', {}).get(':path', ''):
            try:
                response_body = driver.execute_cdp_cmd('Network.getResponseBody',
                                                       {'requestId': x["params"]["requestId"]})
                shotmap = json.loads(response_body['body'])['shotmap']
                break
            except Exception as e:
                print(f"Error occurred while extracting shotmap: {e}")
                break

    driver.quit()
    return shotmap

