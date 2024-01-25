# import libraries
import numpy as np


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