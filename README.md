Installation

## Use the package manager [pip](pypi.org) to install 


    pip install SoccerViz==0.6.0


Import the SoccerViz Package

    #SoccerViz Package
    from SoccerViz import plot,extract,datafilter

Scrape event data from **[WhoScored](whoscored.com)** **_ONLY_** inorder to use it for data analysis and visualization, you would have to fill in the following parameters according to
your liking, below example is given follow it and keep in mind the instructions given too with the code.
    
    
    #This is an example URL from Whoscored.com similar to the below one
    
    url = 'https://www.whoscored.com/Matches/1821060/Live/England-Premier-League-2024-2025-Aston-Villa-Arsenal'  #This is an example URL from Whoscored.com
    understat_url = 'https://understat.com/match/26618'  #Copy Link of the Understat URL


    #Call the extract functions to get Pass Dataframe,Players Dataframe of the particular match
    
    
    df = extract.pass_data(url)
    players_df = extract.player_data(url)
    home_df,away_df = extract.shots(understat_url)
    
    #You can find the TEAM Id's of the clubs on their WhoScored page html tags by clicking on the club logos
    
    home_team_id=24 #Arsenal Team ID
    away_team_id=13 #Aston Villa Team ID
    home_team_name = 'Arsenal'
    away_team_name = 'Aston Villa'


After scrapping the event data and assembling into DataFrames, you will need to filter the data according to the teams and players.

    #Filter all the data according to the teams by calling the function into DataFrames(their names are pretty self explanatory)

    #You can use and call any dataframe you would like to analyze in raw tables and columns i.e. in a DataFrame form
    pass_between_home, pass_between_away, avg_loc_home, avg_loc_away, passes_home, passes_away,df_prg_home,df_comp_prg_home,df_uncomp_prg_home,df_prg_away,df_comp_prg_away,df_uncomp_prg_away = datafilter.analyze_passes(df, players_df, home_team_id, away_team_id)

    #Same goes for the shots of the match
    df1_missed,df2_missed,df1_saved,df2_saved,df1_goal,df2_goal,df1_block,df2_block,totalxG1,totalxG2=datafilter.analyze_shots(home_df,away_df)


Now finally, you can plot the pass network map for both the teams to analyze and visualize by calling the function
## Plotting Pass Network
    #Call the function and manually put in the home and away team names
    
    plot = plot.pass_network(pass_between_home, pass_between_away, avg_loc_home,avg_loc_away,home_team_name,away_team_name)
    
![passmap.png](SoccerViz%2Fpassmap.png)

## Plotting Prg Passes
    
    #Call the function and put in home and away team names
    plot = plot.prg_passes(df_comp_prg_home, df_uncomp_prg_home, df_comp_prg_away, df_uncomp_prg_away, home_team_name,
                    away_team_name)
![prgpassmap.png](SoccerViz%2Fprgpassmap.png)


## Plotting Shot Maps
    
    #Call the function 
    plot = plot.shot_map(df1_missed, df2_missed, df1_saved, df2_saved, df1_goal, df2_goal, df1_block, df2_block, home_team_name,
                 away_team_name,totalxG1, totalxG2)
    
![shotmap.png](SoccerViz%2Fshotmap.png)


## Compare Players from the Big 5 EU Leagues 2022-2024 seasons using Pizza Plots 

        First and foremost download the CSV File 'big5stats22-24.csv' *data from FBRef via WorldFootballR
        Or you can download from the GitHub>DATA
        #Load the CSV file as DF
        df = pd.read_csv('#filepath')

The available parameters are:
        ['Gls', 'Ast', 'G+A', 'xG', 'PrgC', 'PrgP', 'PrgR', 'Shots', 'Shts on Target', 
        'TklW', 'Blocks', 'Int', 'Succ Takeons', 'Recov', 'Aerial Duels', 'Pass CmpRate', 
        'LongPass CmpRate', 'KeyPasses', 'PassPA', 'FinalThird Passes', 'CrsPA']

Positions Values should be coherent with these:
        'DF', 'MF', 'FW', 'GK' 

Example Usage

        position = 'DF'  #specify the position
        player1 = 'Riccardo Calafiori'  # double-check spellings from FBRef
        player2 = 'Ben White'  # double-check special characters in player names
        
        #specify any parameters from the list above to compare players
        params = ['G+A', 'PrgC','PrgP', 'TklW','Blocks','Int','LongPass CmpRate','KeyPasses','CrsPA']

        values, values2 = datafilter.compare_players(df, position, player1, player2, params)
        plot = plot.pizza_plot(values, values2, params, player1, player2)
![calavzini_plot.png](SoccerViz%2Fcalavzini_plot.png)

## Plot ShotMaps for Individual Players throughout the Season

        playerid="5220" #put the player Id in strings from Understat.com URL
        season=2023 #season you wish to plot the shotmap of
        player_name = "Kai Havertz" #player_name
        
        plot = plot.playershots(playerid,season,player_name) #Call in the function to plot
        
![kai.png](SoccerViz%2Fkai.png)



## Credits

Huge Shoutout to the guys at Mplsoccer, do check their package out also, and also checkout Mckay Johns Youtube Channel, which helped me alot in learning python and football analytics
    
And please don't forget to drop me feedback on Twitter/X, @athalakbar13.

Enjoy!!

    
