# import libraries
import numpy as np
import pandas as pd
import json


# function to prep and filter the data extracted
def analyze_passes(df, players_df, home_team_id, away_team_id):
    df = df
    df1 = df

    # differentiating data for 2 teams
    teamid = home_team_id
    df = df[df['teamId'] == teamid]
    df['passer'] = df['playerId']
    df['reciever'] = df['playerId'].shift(-1)
    passes_home = df[df['eventType'] == 'Pass']
    successful_home = df[df['outcomeType'] == 'Successful']

    teamid1 = away_team_id
    df1 = df1[df1['teamId'] == teamid1]
    df1['passer'] = df1['playerId']
    df1['reciever'] = df1['playerId'].shift(-1)
    passes_away = df1[df1['eventType'] == 'Pass']
    successful_away = df1[df1['outcomeType'] == 'Successful']

    # filtering passes to player and successful
    passes_home = passes_home.merge(players_df[["playerId", "name"]], on='playerId', how='left')
    passes_away = passes_away.merge(players_df[["playerId", "name"]], on='playerId', how='left')
    successful_home = successful_home.merge(players_df[["playerId", "isFirstEleven"]], on='playerId', how='left')
    successful_home = successful_home[successful_home['isFirstEleven'] == True]
    successful_away = successful_away.merge(players_df[["playerId", "isFirstEleven"]], on='playerId', how='left')
    successful_away = successful_away[successful_away['isFirstEleven'] == True]

    # avg_locations filter
    avg_loc_home = successful_home.groupby('playerId').agg({'x': ['mean'], 'y': ['mean', 'count']})
    avg_loc_home.columns = ['x', 'y', 'count']
    avg_loc_home = avg_loc_home.merge(players_df[['playerId', 'name', 'shirtNo', 'position']], on='playerId',
                                      how='left')
    avg_loc_away = successful_away.groupby('playerId').agg({'x': ['mean'], 'y': ['mean', 'count']})
    avg_loc_away.columns = ['x', 'y', 'count']
    avg_loc_away = avg_loc_away.merge(players_df[['playerId', 'name', 'shirtNo', 'position']], on='playerId',
                                      how='left')

    # passes in between players filter
    pass_between_home = successful_home.groupby(['passer', 'reciever']).id.count().reset_index()
    pass_between_home.rename({'id': 'pass_count'}, axis='columns', inplace=True)
    pass_between_home = pass_between_home.merge(avg_loc_home, left_on='passer', right_on='playerId')
    pass_between_home = pass_between_home.merge(avg_loc_home, left_on='reciever', right_on='playerId',
                                                suffixes=['', '_end'])

    pass_between_away = successful_away.groupby(['passer', 'reciever']).id.count().reset_index()
    pass_between_away.rename({'id': 'pass_count'}, axis='columns', inplace=True)
    pass_between_away = pass_between_away.merge(avg_loc_away, left_on='passer', right_on='playerId')
    pass_between_away = pass_between_away.merge(avg_loc_away, left_on='reciever', right_on='playerId',
                                                suffixes=['', '_end'])
    # filtering for more than 3 passing combinations
    pass_between_home = pass_between_home[pass_between_home['pass_count'] >= 4]
    pass_between_away = pass_between_away[pass_between_away['pass_count'] >= 4]

    passes_home['beginning'] = np.sqrt(np.square(100 - passes_home['x']) + np.square(50 - passes_home['y']))
    passes_home['end'] = np.sqrt(np.square(100 - passes_home['endX']) + np.square(50 - passes_home['endY']))
    passes_home['progressive'] = [(passes_home['end'][x]) / (passes_home['beginning'][x]) < .75 for x in
                                  range(len(passes_home.beginning))]
    df_prg_home = passes_home[passes_home['progressive'] == True]
    df_comp_prg_home = df_prg_home[df_prg_home['outcomeType'] == 'Successful']
    df_uncomp_prg_home = df_prg_home[df_prg_home['outcomeType'] == 'Unsuccessful']

    passes_away['beginning'] = np.sqrt(np.square(100 - passes_away['x']) + np.square(50 - passes_away['y']))
    passes_away['end'] = np.sqrt(np.square(100 - passes_away['endX']) + np.square(50 - passes_away['endY']))
    passes_away['progressive'] = [(passes_away['end'][x]) / (passes_away['beginning'][x]) < .75 for x in
                                  range(len(passes_away.beginning))]
    df_prg_away = passes_away[passes_away['progressive'] == True]
    df_comp_prg_away = df_prg_away[df_prg_away['outcomeType'] == 'Successful']
    df_uncomp_prg_away = df_prg_away[df_prg_away['outcomeType'] == 'Unsuccessful']

    return pass_between_home, pass_between_away, avg_loc_home, avg_loc_away, passes_home, passes_away, df_prg_home, df_comp_prg_home, df_uncomp_prg_home, df_prg_away, df_comp_prg_away, df_uncomp_prg_away

def analyze_shots(shots):

    shots = shots.json()

    df = pd.json_normalize(shots['shotmap'])
    player_names = [shot['player']['name'] for shot in shots['shotmap']]
    df_player_names = pd.DataFrame(player_names, columns=['Player Names'])
    merged_df = pd.concat([df, df_player_names], axis=1)
    combined_df = df
    combined_df = combined_df.fillna(0)
    combined_df['markersize'] = combined_df['xg'] * 800
    combined_df = combined_df.sort_values('time', ascending=True)

    #1 represents Home Team
    #2 represents Away Team
    df1 = combined_df.loc[combined_df['isHome'] == True]
    df2 = combined_df.loc[combined_df['isHome'] == False]
    df1['cum_xg'] = df1['xg'].cumsum()
    df2['cum_xg'] = df2['xg'].cumsum()
    totalxG1 = df1['xg'].sum()
    totalxG2 = df2['xg'].sum()
    totalxG1 = format(totalxG1, '.2f')
    totalxG2 = format(totalxG2, '.2f')

    df2['playerCoordinates.x'] = 100 - df2['playerCoordinates.x']
    df2['playerCoordinates.y'] = 100 - df2['playerCoordinates.y']
    df2['goalMouthCoordinates.x'] = 100 - df2['goalMouthCoordinates.x']
    df2['goalMouthCoordinates.y'] = 100 - df2['goalMouthCoordinates.y']

    df1_missed = df1.loc[df1['shotType'] == 'miss']
    df2_missed = df2.loc[df2['shotType'] == 'miss']
    df1_saved = df1.loc[df1['shotType'] == 'save']
    df2_saved = df2.loc[df2['shotType'] == 'save']
    df1_goal = df1.loc[df1['shotType'] == 'goal']
    df2_goal = df2.loc[df2['shotType'] == 'goal']
    df1_block = df1.loc[df1['shotType'] == 'block']
    df2_block = df2.loc[df2['shotType'] == 'block']

    return df1_missed,df2_missed,df1_saved,df2_saved,df1_goal,df2_goal,df1_block,df2_block,totalxG1,totalxG2





