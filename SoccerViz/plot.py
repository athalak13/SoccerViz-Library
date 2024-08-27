import matplotlib.pyplot as plt
from matplotlib.colors import to_rgba
import matplotlib.patheffects as path_effects
from mplsoccer import VerticalPitch, Pitch, FontManager,PyPizza,create_transparent_cmap,FontManager, arrowhead_marker, Sbopen
from highlight_text import ax_text,fig_text
import numpy as np
import matplotlib.pyplot as plt
from understatapi import UnderstatClient
import pandas as pd
import matplotlib.ticker as ticker
import matplotlib.patheffects as path_effects
import numpy as np




font_normal = FontManager('https://raw.githubusercontent.com/googlefonts/roboto/main/'
                          'src/hinted/Roboto-Regular.ttf')
font_italic = FontManager('https://raw.githubusercontent.com/googlefonts/roboto/main/'
                          'src/hinted/Roboto-Italic.ttf')
font_bold = FontManager('https://raw.githubusercontent.com/google/fonts/main/apache/robotoslab/'
                        'RobotoSlab[wght].ttf')
fm_rubik = FontManager('https://raw.githubusercontent.com/google/fonts/main/ofl/'
                       'rubikmonoone/RubikMonoOne-Regular.ttf')


# function to plot the pass network plot
def pass_network(pass_between_home, pass_between_away, avg_loc_home, avg_loc_away, home_team_name, away_team_name):
    # Specify the URL or local path to the Oswald font file
    oswald_font_url = "https://raw.githubusercontent.com/google/fonts/main/ofl/oswald/Oswald%5Bwght%5D.ttf"

    # Create the FontManager instance
    oswald_regular = FontManager(oswald_font_url)


    # Define your parameters
    MAX_LINE_WIDTH = 500
    MAX_MARKER_SIZE = 1500
    MIN_TRANSPARENCY = 0.0

    # Calculate line width and marker size based on your data
    pass_between_home['width'] = (pass_between_home.pass_count / pass_between_home.pass_count.max() * MAX_LINE_WIDTH)
    avg_loc_home['marker_size'] = (avg_loc_home['count'] / avg_loc_home['count'].max() * MAX_MARKER_SIZE)

    # Calculate color and transparency
    color = np.array(to_rgba('black'))
    color = np.tile(color, (len(pass_between_home), 1))
    c_transparency = pass_between_home.pass_count / pass_between_home.pass_count.max()
    c_transparency = (c_transparency * (1 - MIN_TRANSPARENCY)) + MIN_TRANSPARENCY
    color[:, 3] = c_transparency

    # Create a VerticalPitch object
    pitch = VerticalPitch(
        pitch_type="opta",
        pitch_color="white",
        line_color="black",
        linewidth=1,
    )

    fig, axs = pitch.grid(ncols=2, title_height=0.08, endnote_space=0,
                          # Turn off the endnote/title axis. I usually do this after
                          # I am happy with the chart layout and text placement
                          axis=False,
                          title_space=0, grid_height=0.82, endnote_height=0.05)

    # Plot the pass network
    arrows = pitch.arrows(
        pass_between_home.x,
        pass_between_home.y,
        pass_between_home.x_end,
        pass_between_home.y_end,
        lw=c_transparency,
        color=color,
        zorder=2,
        ax=axs['pitch'][0],
    )
    pass_nodes = pitch.scatter(
        avg_loc_home.x,
        avg_loc_home.y,
        color="red",
        edgecolors="black",
        s=avg_loc_home.marker_size,
        linewidth=0.5,
        alpha=1,
        ax=axs['pitch'][0],
    )

    for index, row in avg_loc_home.iterrows():
        text = pitch.annotate(
            row.shirtNo,
            xy=(row.x, row.y),
            c="white",
            va="center",
            ha="center",
            size=12,
            weight="bold",
            ax=axs['pitch'][0],
            fontproperties=oswald_regular.prop,
        )
        text.set_path_effects([path_effects.withStroke(linewidth=1, foreground="yellow")])

    # 2nd Team Pass Network Plots Start

    # Define your parameters
    MAX_LINE_WIDTH = 500
    MAX_MARKER_SIZE = 1500
    MIN_TRANSPARENCY = 0.0

    # Calculate line width and marker size based on your data
    pass_between_away['width'] = (pass_between_away.pass_count / pass_between_away.pass_count.max() * MAX_LINE_WIDTH)
    avg_loc_away['marker_size'] = (avg_loc_away['count'] / avg_loc_away['count'].max() * MAX_MARKER_SIZE)

    # Calculate color and transparency
    color1 = np.array(to_rgba('black'))
    color1 = np.tile(color1, (len(pass_between_away), 1))
    c_transparency1 = pass_between_away.pass_count / pass_between_away.pass_count.max()
    c_transparency1 = (c_transparency1 * (1 - MIN_TRANSPARENCY)) + MIN_TRANSPARENCY
    color1[:, 3] = c_transparency1

    # Plot the pass network
    arrows = pitch.arrows(
        pass_between_away.x,
        pass_between_away.y,
        pass_between_away.x_end,
        pass_between_away.y_end,
        lw=c_transparency1,
        color=color1,
        zorder=2,
        ax=axs['pitch'][1],
    )
    pass_nodes = pitch.scatter(
        avg_loc_away.x,
        avg_loc_away.y,
        color="blue",
        edgecolors="black",
        s=avg_loc_away.marker_size,
        linewidth=0.5,
        alpha=1,
        ax=axs['pitch'][1],
    )

    for index, row in avg_loc_away.iterrows():
        text = pitch.annotate(
            row.shirtNo,
            xy=(row.x, row.y),
            c="white",
            va="center",
            ha="center",
            size=12,
            weight="bold",
            ax=axs['pitch'][1],
            fontproperties=oswald_regular.prop,
        )
        text.set_path_effects([path_effects.withStroke(linewidth=1, foreground="black")])

    # Add labels to the pass networks
    highlight_text = [{'color': "red", 'fontname': 'Rockwell'},
                      {'color': "blue", 'fontname': 'Rockwell'}]
    ax_text(0.5, 0.7, f"<{home_team_name}> & <{away_team_name}> Pass Networks", fontsize=28, color='#000009',
            fontname='Rockwell', highlight_textprops=highlight_text,
            ha='center', va='center', ax=axs['title'])
    axs["endnote"].text(
        1,
        1,
        "twitter/X : @athalakbar13",
        color="black",
        va="center",
        ha="right",
        fontsize=18,
        fontname= 'Rockwell',
    )

    plt.show()
    return fig
# function to plot the progressive passes of both the teams
def prg_passes(df_comp_prg_home,df_uncomp_prg_home, df_comp_prg_away, df_uncomp_prg_away, home_team_name,away_team_name):
    # Specify the URL or local path to the Oswald font file
    oswald_font_url = "https://raw.githubusercontent.com/google/fonts/main/ofl/oswald/Oswald%5Bwght%5D.ttf"

    # Create the FontManager instance
    oswald_regular = FontManager(oswald_font_url)


    pitch = Pitch(pitch_type='opta', pitch_color='white', line_color='black')
    fig, axs = pitch.grid(nrows=2, ncols=2, title_height=0.08, endnote_space=0,
                          # Turn off the endnote/title axis. I usually do this after
                          # I am happy with the chart layout and text placement
                          axis=False,
                          title_space=0, grid_height=0.82
                          , endnote_height=0.05)
    fig.set_facecolor('white')

    # Plot the completed passes
    pitch.lines(df_comp_prg_home.x, df_comp_prg_home.y,
                df_comp_prg_home.endX, df_comp_prg_home.endY, comet=True, color='green', ax=axs['pitch'][0, 0],
                label='completed passes', alpha=0.35)

    pitch.scatter(df_comp_prg_home.endX, df_comp_prg_home.endY, color='green', s=100, ax=axs['pitch'][0, 0], alpha=0.5)
    pitch.lines(df_uncomp_prg_home.x, df_uncomp_prg_home.y,
                df_uncomp_prg_home.endX, df_uncomp_prg_home.endY, comet=True, color='red', ax=axs['pitch'][0, 1],
                label='unsuccessful passes', alpha=0.35)
    pitch.scatter(df_uncomp_prg_home.endX, df_uncomp_prg_home.endY, color='red', s=100, ax=axs['pitch'][0, 1],
                  alpha=0.5)
    highlight_text = [{'color': 'green', 'fontname': 'Rockwell'},
                      {'color': 'red', 'fontname': 'Rockwell'}]
    ax_text(0.5, 0.7, f"{home_team_name} <Successful> Prg Passes & <Unsuccessful> Prg Passes v. {away_team_name}", fontsize=25,
            color='#000009',
            fontname='Rockwell', highlight_textprops=highlight_text,
            ha='center', va='center', ax=axs['title'])

    pitch.lines(df_comp_prg_away.x, df_comp_prg_away.y,
                df_comp_prg_away.endX, df_comp_prg_away.endY, comet=True, color='green', ax=axs['pitch'][1, 0],
                label='completed passes', alpha=0.35)

    pitch.scatter(df_comp_prg_away.endX, df_comp_prg_away.endY, color='green', s=100, ax=axs['pitch'][1, 0], alpha=0.5)
    pitch.lines(df_uncomp_prg_away.x, df_uncomp_prg_away.y,
                df_uncomp_prg_away.endX, df_uncomp_prg_away.endY, comet=True, color='red', ax=axs['pitch'][1, 1],
                label='unsuccessful passes', alpha=0.35)
    pitch.scatter(df_uncomp_prg_away.endX, df_uncomp_prg_away.endY, color='red', s=100, ax=axs['pitch'][1, 1],
                  alpha=0.5)
    highlight_text = [{'color': 'green', 'fontname': 'Rockwell'},
                      {'color': 'red', 'fontname': 'Rockwell'}]
    ax_text(0.5, -5.25, f"{away_team_name} <Successful> Prg Passes & <Unsuccessful> Prg Passes v. {home_team_name}", fontsize=25,
            color='#000009',
            fontname='Rockwell', highlight_textprops=highlight_text,
            ha='center', va='center', ax=axs['title'])

    axs["endnote"].text(
        1,
        1,
        "Twitter/X : @athalakbar13",
        color="black",
        va="center",
        ha="right",
        fontsize=18,
        fontname='Rockwell',
    )

    plt.show()
    return fig


def shot_map(df1_missed, df2_missed, df1_saved, df2_saved, df1_goal, df2_goal, df1_block, df2_block, home_team_name,
             away_team_name, totalxG1, totalxG2):
    pitch = Pitch(pitch_type='opta', pitch_color='white', linewidth=5, spot_scale=0.005)
    fig, ax = pitch.draw(figsize=(12, 10))

    # Plot the completed passes

    pitch.scatter(df1_missed['X'], df1_missed['Y'], color="red",
                  s=df1_missed.markersize, ax=ax, alpha=0.5, edgecolors='#383838')

    pitch.scatter(df2_missed['X'], df2_missed['Y'], color="blue",
                  s=df2_missed.markersize, ax=ax, alpha=0.5, edgecolors='#383838')

    pitch.scatter(df1_saved['X'], df1_saved['Y'], color="red",
                  s=df1_saved.markersize, alpha=0.75, ax=ax, edgecolors='black')

    pitch.scatter(df2_saved['X'], df2_saved['Y'], color="blue",
                  s=df2_saved.markersize, alpha=0.75, ax=ax, edgecolors='black')

    pitch.scatter(df1_goal['X'], df1_goal['Y'], color="red",
                  s=df1_goal.markersize,
                  marker='*', ax=ax, edgecolors='black', alpha=0.8)

    pitch.scatter(df2_goal['X'], df2_goal['Y'], color="blue",
                  s=df2_goal.markersize,
                  marker='*', ax=ax, edgecolors='black', alpha=0.8)

    pitch.scatter(df1_block['X'], df1_block['Y'], color="red",
                  s=df1_block.markersize, ax=ax, edgecolors='black', alpha=0.8)

    pitch.scatter(df2_block['X'], df2_block['Y'], color="blue",
                  s=df2_block.markersize, ax=ax, edgecolors='black', alpha=0.8)

    highlight_text = [{'color': 'red', 'fontname': "Rockwell"},
                      {'color': 'blue', 'fontname': "Rockwell"}]
    ax_text(25, 90, f"<{home_team_name}>", size=35, color="red",
            fontname="Rockwell",
            ha='center', va='center', ax=ax, weight='bold')
    ax_text(75, 90, f"<{away_team_name}>", size=35, color="blue",
            fontname="Rockwell",
            ha='center', va='center', ax=ax, weight='bold')

    ax.text(85, 5, "@athalakbar13", size=20, color='#000009',
            fontname="Rockwell",
            ha='center', va='center', alpha=0.5)
    ax.text(50, 103, "xG Shot Map", size=30, color='black',
            fontname="Rockwell",
            ha='center', va='center')
    ax.text(25, 82, f"(Total xG : {totalxG1})", size=20, color="red", alpha=0.85,
            fontname="Rockwell",
            ha='center', va='center', weight='bold')
    ax.text(75, 82, f"(Total xG : {totalxG2})", size=20, color="blue", alpha=0.85,
            fontname="Rockwell",
            ha='center', va='center', weight='bold')
    plt.show()
    return fig

def pizza_plot(values, values2, params, player1, player2):
    # Instantiate PyPizza class
    baker = PyPizza(
        params=params,  # max range values
        background_color="#222222", straight_line_color="#000000",
        last_circle_color="#000000", last_circle_lw=2.5, other_circle_lw=0,
        other_circle_color="#000000", straight_line_lw=1
    )

    # Plot pizza
    fig, ax = baker.make_pizza(
        values,  # list of values
        compare_values=values2,  # passing comparison values
        figsize=(8, 8),  # adjust figsize according to your need
        color_blank_space="same",  # use same color to fill blank space
        blank_alpha=0.4,  # alpha for blank-space colors
        param_location=105,  # where the parameters will be added
        kwargs_slices=dict(
            facecolor="#1A78CF", edgecolor="#000000",
            zorder=1, linewidth=1
        ),  # values to be used when plotting slices
        kwargs_compare=dict(
            facecolor="#ff9300", edgecolor="#222222", zorder=3, linewidth=1,
        ),  # values to be used when plotting comparison slices
        kwargs_params=dict(
            color="#F2F2F2", fontsize=12, zorder=5,
            fontproperties=font_normal.prop, va="center"
        ),  # values to be used when adding parameter
        kwargs_values=dict(
            color="#000000", fontsize=12,
            fontproperties=font_normal.prop, zorder=3,
            bbox=dict(
                edgecolor="#000000", facecolor="#1A78CF",
                boxstyle="round,pad=0.2", lw=1
            )
        ),  # values to be used when adding parameter-values
        kwargs_compare_values=dict(
            color="#000000", fontsize=12,
            fontproperties=font_normal.prop, zorder=3,
            bbox=dict(
                edgecolor="#000000", facecolor="#FF9300",
                boxstyle="round,pad=0.2", lw=1
            )
        )  # values to be used when adding comparison-values
    )

    # Add title
    fig_text(
        0.515, 0.99, f"<{player1}> vs <{player2}>",
        size=16, fig=fig,
        highlight_textprops=[{"color": '#1A78CF'}, {"color": '#FF9300'}],
        ha="center", fontproperties=font_bold.prop, color="#F2F2F2"
    )

    # Add subtitle
    fig.text(
        0.515, 0.92,
        "Percentile Rank v. Top 5 League Players 22-24 \n *min 1000mins",
        size=12,
        ha="center", fontproperties=font_bold.prop, color="#F2F2F2"
    )

    # Add credits
    CREDIT_1 = "data via WorldFootballR from FBref"
    CREDIT_2 = "@athalakbar13 via mplsoccer"

    fig.text(
        0.99, 0.005, f"{CREDIT_1}\n{CREDIT_2}", size=9,
        fontproperties=font_italic.prop, color="#F2F2F2",
        ha="right"
    )

    plt.show()
    return fig

def playershots(player_id, season, player_name):
    with UnderstatClient() as understat:
        player_shot_data = understat.player(player=player_id).get_shot_data()
        df = pd.DataFrame(player_shot_data)
        cols_to_convert = ['id', 'minute', 'Y', 'X', 'xG', 'player_id', 'match_id', 'season']

        df[cols_to_convert] = df[cols_to_convert].astype(float)
        df['X'] = df['X'] * 100
        df['Y'] = df['Y'] * 100
        df = df[df['season'] == season]

        goals = df[df['result'] == 'Goal']
        shots = df[df['result'] != 'Goal']

        pitch = VerticalPitch(pad_bottom=0.5,  # pitch extends slightly below halfway line
                              half=True,  # half of a pitch
                              goal_type='box',
                              goal_alpha=0.8,
                              pitch_type='opta',
                              pitch_color='black',
                              )  # control the goal transparency
        fig, ax = pitch.draw(figsize=(12, 10))

        sc = pitch.scatter(shots.X, shots.Y,
                           # size varies between 100 and 1000 (points squared)
                           s=(shots.xG * 900) + 100,
                           c='black',  # color for scatter in hex format
                           edgecolors='red',  # give the markers a charcoal border
                           # for other markers types see: https://matplotlib.org/api/markers_api.html

                           ax=ax)

        sc = pitch.scatter(goals.X, goals.Y,
                           # size varies between 100 and 1000 (points squared)
                           s=(goals.xG * 900) + 100,
                           c='red',  # color for scatter in hex format
                           edgecolors='black',
                           alpha=0.8,  # give the markers a charcoal border
                           # for other markers types see: https://matplotlib.org/api/markers_api.html

                           ax=ax)

        txt = ax.text(x=50, y=70, s=f"{player_name} Shots",
                      size=30,
                      # here i am using a downloaded font from google fonts instead of passing a fontdict
                      fontproperties=fm_rubik.prop, color=pitch.line_color,
                      va='center', ha='center')
        txt = ax.text(x=50, y=68, s=f" in {season}",
                      size=20,
                      # here i am using a downloaded font from google fonts instead of passing a fontdict
                      fontproperties=fm_rubik.prop, color=pitch.line_color,
                      va='center', ha='center')
        txt = ax.text(x=15, y=55, s='SoccerViz',
                      size=10,
                      # here i am using a downloaded font from google fonts instead of passing a fontdict
                      fontproperties=fm_rubik.prop, color=pitch.line_color,
                      va='center', ha='center')
        plt.show()
        return fig


