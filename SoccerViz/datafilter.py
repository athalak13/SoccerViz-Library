# import libraries
import numpy as np
import pandas as pd
import json
import math
from scipy import stats


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


def analyze_shots(home_df, away_df):
    df = pd.concat([home_df, away_df])
    cols_to_convert = ['X', 'Y', 'xG']
    for col in cols_to_convert:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    combined_df = df
    combined_df = combined_df.fillna(0)
    combined_df['markersize'] = combined_df['xG'] * 1000
    combined_df = combined_df.sort_values('minute', ascending=True)

    combined_df.rename(columns={'h_a': 'isHome'}, inplace=True)
    combined_df['isHome'] = combined_df['isHome'].replace({'h': True, 'a': False})
    combined_df['isHome'] = combined_df['isHome'].astype(bool)

    # 1 represents home and 2 represents away
    df1 = combined_df.loc[combined_df['isHome'] == True]
    df2 = combined_df.loc[combined_df['isHome'] == False]
    df1['cum_xg'] = df1['xG'].cumsum()
    df2['cum_xg'] = df2['xG'].cumsum()
    totalxG1 = df1['xG'].sum()
    totalxG2 = df2['xG'].sum()
    totalxG1 = format(totalxG1, '.2f')
    totalxG2 = format(totalxG2, '.2f')

    # Correcting the Co-Ordinates to fit in one map
    df1['X'] = 100 * df1['X']
    df1['Y'] = 100 * df1['Y']
    df2['X'] = 100 * df2['X']
    df2['Y'] = 100 * df2['Y']
    df1['X'] = 100 - df1['X']
    df1['Y'] = 100 - df1['Y']

    df1_missed = df1.loc[df1['result'].isin(['ShotOnPost', 'MissedShots'])]
    df2_missed = df2.loc[df2['result'].isin(['ShotOnPost', 'MissedShots'])]
    df1_saved = df1.loc[df1['result'] == 'SavedShot']
    df2_saved = df2.loc[df2['result'] == 'SavedShot']
    df1_goal = df1.loc[df1['result'] == 'Goal']
    df2_goal = df2.loc[df2['result'] == 'Goal']
    df1_block = df1.loc[df1['result'] == 'BlockedShot']
    df2_block = df2.loc[df2['result'] == 'BlockedShot']

    return df1_missed, df2_missed, df1_saved, df2_saved, df1_goal, df2_goal, df1_block, df2_block, totalxG1, totalxG2


def validate_input(df, position, player1, player2, params):
    # Check if position exists in the dataframe
    if position not in df['Pos'].unique():
        raise ValueError(f"Position {position} does not exist in the dataframe.")

    # Check if both players exist in the dataframe
    if player1 not in df['Player'].unique():
        raise ValueError(f"Player {player1} does not exist in the dataframe.")
    if player2 not in df['Player'].unique():
        raise ValueError(f"Player {player2} does not exist in the dataframe.")

    # Check if all params exist in the dataframe columns
    for param in params:
        if param not in df.columns:
            raise ValueError(f"Parameter {param} does not exist in the dataframe.")


def compare_players(df, position, player1, player2, params):
    # Validate input parameters before any column manipulation
    validate_input(df, position, player1, player2, params)

    # Filter the dataframe for the given position and 90s played
    df_filtered = df.loc[(df['Pos'] == position) & (df['Mins'] >= 1000)]

    # Drop unnecessary columns
    df_filtered = df_filtered.drop(['Season_End_Year', 'Squad', 'Comp', 'Nation', 'Pos', 'Age',
                                    'Mins'], axis=1)

    # Get player stats
    player_data = df_filtered.loc[df_filtered['Player'] == player1].reset_index()
    player_stats = list(player_data.loc[0, params])

    player2_data = df_filtered.loc[df_filtered['Player'] == player2].reset_index()
    player2_stats = list(player2_data.loc[0, params])

    # Calculate percentiles
    values = [math.floor(stats.percentileofscore(df_filtered[param], stat)) for param, stat in
              zip(params, player_stats)]
    values2 = [math.floor(stats.percentileofscore(df_filtered[param], stat)) for param, stat in
               zip(params, player2_stats)]

    return values, values2


# import libraries
import numpy as np
import pandas as pd
import json
import math
from scipy import stats


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

def analyze_shots(home_df,away_df):
    df = pd.concat([home_df, away_df])
    cols_to_convert = ['X','Y','xG']
    for col in cols_to_convert:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    combined_df = df
    combined_df = combined_df.fillna(0)
    combined_df['markersize'] = combined_df['xG'] * 1000
    combined_df = combined_df.sort_values('minute', ascending=True)

    combined_df.rename(columns={'h_a': 'isHome'}, inplace=True)
    combined_df['isHome'] = combined_df['isHome'].replace({'h': True, 'a': False})
    combined_df['isHome'] = combined_df['isHome'].astype(bool)

    #1 represents home and 2 represents away
    df1 = combined_df.loc[combined_df['isHome'] == True]
    df2 = combined_df.loc[combined_df['isHome'] == False]
    df1['cum_xg'] = df1['xG'].cumsum()
    df2['cum_xg'] = df2['xG'].cumsum()
    totalxG1 = df1['xG'].sum()
    totalxG2 = df2['xG'].sum()
    totalxG1 = format(totalxG1, '.2f')
    totalxG2 = format(totalxG2, '.2f')

    # Correcting the Co-Ordinates to fit in one map
    df1['X'] = 100 * df1['X']
    df1['Y'] = 100 * df1['Y']
    df2['X'] = 100 * df2['X']
    df2['Y'] = 100 * df2['Y']
    df1['X'] = 100 - df1['X']
    df1['Y'] = 100 - df1['Y']

    df1_missed = df1.loc[df1['result'].isin(['ShotOnPost', 'MissedShots'])]
    df2_missed = df2.loc[df2['result'].isin(['ShotOnPost', 'MissedShots'])]
    df1_saved = df1.loc[df1['result'] == 'SavedShot']
    df2_saved = df2.loc[df2['result'] == 'SavedShot']
    df1_goal = df1.loc[df1['result'] == 'Goal']
    df2_goal = df2.loc[df2['result'] == 'Goal']
    df1_block = df1.loc[df1['result'] == 'BlockedShot']
    df2_block = df2.loc[df2['result'] == 'BlockedShot']

    return df1_missed,df2_missed,df1_saved,df2_saved,df1_goal,df2_goal,df1_block,df2_block,totalxG1,totalxG2


def validate_input(df, position, player1, player2, params):
    # Check if position exists in the dataframe
    if position not in df['Pos'].unique():
        raise ValueError(f"Position {position} does not exist in the dataframe.")

    # Check if both players exist in the dataframe
    if player1 not in df['Player'].unique():
        raise ValueError(f"Player {player1} does not exist in the dataframe.")
    if player2 not in df['Player'].unique():
        raise ValueError(f"Player {player2} does not exist in the dataframe.")

    # Check if all params exist in the dataframe columns
    for param in params:
        if param not in df.columns:
            raise ValueError(f"Parameter {param} does not exist in the dataframe.")


def compare_players(df, position, player1, player2, params):
    # Validate input parameters before any column manipulation
    validate_input(df, position, player1, player2, params)

    # Filter the dataframe for the given position and 90s played
    df_filtered = df.loc[(df['Pos'] == position) & (df['Mins'] >= 1000)]

    # Drop unnecessary columns
    df_filtered = df_filtered.drop(['Season_End_Year', 'Squad', 'Comp', 'Nation', 'Pos', 'Age',
                                    'Mins'], axis=1)

    # Get player stats
    player_data = df_filtered.loc[df_filtered['Player'] == player1].reset_index()
    player_stats = list(player_data.loc[0, params])

    player2_data = df_filtered.loc[df_filtered['Player'] == player2].reset_index()
    player2_stats = list(player2_data.loc[0, params])

    # Calculate percentiles
    values = [math.floor(stats.percentileofscore(df_filtered[param], stat)) for param, stat in
              zip(params, player_stats)]
    values2 = [math.floor(stats.percentileofscore(df_filtered[param], stat)) for param, stat in
               zip(params, player2_stats)]

    return values, values2






