Installation

Use the package manager [pip](pypi.org) to install 
        
        pip install SoccerViz 0.0.2

Import the necessary Libraries and SoccerViz Package
    
    import re
    import json
    import pandas as pd
    import requests
    from bs4 import BeautifulSoup
    import numpy as np
    import matplotlib.pyplot as plt
    from matplotlib.colors import to_rgba
    import matplotlib.patheffects as path_effects
    from mplsoccer import VerticalPitch, Pitch, FontManager
    from highlight_text import ax_text
    
    #SoccerViz Package
    from SoccerViz import plot,extract,datafilter

Scrape event data from **[WhoScored](whoscored.com)** **_ONLY_** inorder to use it for data analysis and visualization, you would have to fill in the following parameters according to
your liking, below example is given follow it and keep in mind the instructions given too with the code.
    
    
    #This is an example URL from Whoscored.com similar to the below one
    
    url = 'https://www.whoscored.com/Matches/1729448/Live/England-Premier-League-2023-2024-Manchester-United-Tottenham'  #This is an example URL from Whoscored.com
    
    #Put your USER AGENT in the HEADERS parameter, you can find yours on "https://www.whatismybrowser.com/detect/what-http-headers-is-my-browser-sending"
    
    HEADERS = {
            "'USER AGENT: #your user agent"
        }

    #Call the extract functions to get Pass Dataframe and Players Dataframe of the particular match
    
    df = extract.pass_data(url,HEADERS)
    players_df = extract.player_data(url,HEADERS)
    
    #You can find the TEAM Id's of the clubs on their WhoScored page html tags by clicking on the club logos
    
    home_team_id=32 #Man Utd Team ID
    away_team_id=30  #Spurs Team ID

After scrapping the event data and assembling into DataFrames, you will need to filter the data according to the teams and players.

    #Filter all the data according to the teams by calling the function into DataFrames(their names are pretty self explanatory)
    #You can use and call any dataframe you would like to analyze in raw tables and columns i.e. in a DataFrame form
    pass_between_home, pass_between_away, avg_loc_home, avg_loc_away, passes_home, passes_away,df_prg_home,df_comp_prg_home,df_uncomp_prg_home,df_prg_away,df_comp_prg_away,df_uncomp_prg_away = datafilter.analyze_passes(df, players_df, home_team_id, away_team_id)

Now finally, you can plot the pass network map for both the teams to analyze and visualize by calling the function

    #Call the function and manually put in the home and away team names
    hometeam_name = 'Man Utd'
    awayteam_name = 'Spurs'
    plot = plot.pass_network(pass_between_home, pass_between_away, avg_loc_home,avg_loc_away,hometeam_name,awayteam_name)
    
![test1.png](SoccerWizz%2Ftest1.png)

Plotting Prg Passes
    
    #Call the function and put in home and away team names
    plot = plot.prg_passes(df_comp_prg_home, df_uncomp_prg_home, df_comp_prg_away, df_uncomp_prg_away, hometeam_name,
                    awayteam_name)
![test.png](SoccerViz%2Ftest.png)


Credits

    Huge Shoutout to the guys at Mplsoccer, do check their package out also, and also checkout Mckay Johns Youtube Channel, which helped me alot in learning python and football analytics
    
    And please don't forget to drop me feedback on Twitter/X, @athalakbar13.

Enjoy!!

    