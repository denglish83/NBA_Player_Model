import pandas as pd
import datetime
from sqlalchemy import create_engine
import statsmodels.api as sm
import numpy as np

sqlEngine = create_engine('mysql+pymysql://root:k2udaeV%40@localhost:3306/fantasy_basketball', pool_recycle=3600)
connection = sqlEngine.connect()

sql_text = """
WITH team AS (
    SELECT season,
            playerteamName,
            min(game_date) as first_game,
            SUM(win) as num_wins,
            count(*) as num_games
        FROM(
            SELECT season,
                playerteamName,
                gameID,
                max(win) as win,
                max(gameDate) as game_date
                FROM fantasy_basketball.all_seasons_game_lvl
                WHERE gameType = 'Regular Season'
                GROUP BY season, playerteamName, gameID
            ) team_lvl1
        GROUP BY season, playerteamName
    ) 


SELECT a.personid,
        a.player_name,
        a.season,
        a.games_played,
        a.minutes_played,
        a.season_start_age,
        a.season_start_age*a.season_start_age as age_squared,
        b.games_played as games_played_lag_1,
        CASE WHEN c.games_played IS NOT NULL THEN c.games_played 
            ELSE b.games_played END as games_played_lag_2,
        CASE WHEN d.games_played IS NOT NULL THEN d.games_played 
                WHEN c.games_played IS NOT NULL THEN c.games_played 
                ELSE b.games_played END as games_played_lag_3,
        b.minutes_played as minutes_played_lag_1,
        CASE WHEN c.minutes_played IS NOT NULL THEN c.minutes_played 
            ELSE b.minutes_played END as minutes_played_lag_2,
        CASE WHEN d.minutes_played IS NOT NULL THEN d.minutes_played 
                WHEN c.minutes_played IS NOT NULL THEN c.minutes_played 
                ELSE b.minutes_played END as minutes_played_lag_3,
        CASE WHEN a.playerteamname = b.playerteamname THEN 0 ELSE 1 END AS trade_lag_1,
        CASE WHEN b.playerteamname = c.playerteamname THEN 0 ELSE 1 END AS trade_lag_2,
        CASE WHEN c.playerteamname = d.playerteamname THEN 0 ELSE 1 END AS trade_lag_3,
        b.team_win_pct AS player_win_pct_lag_1,
        bb.num_wins/bb.num_games AS team_win_pct_lag_1,
        c.team_win_pct AS player_win_pct_lag_2,
        cc.num_wins/cc.num_games AS team_win_pct_lag_2,
        d.team_win_pct AS player_win_pct_lag_3,
        dd.num_wins/dd.num_games AS team_win_pct_lag_3
FROM fantasy_basketball.season_level_stats a
INNER JOIN fantasy_basketball.season_level_stats b
ON a.personid = b.personid AND a.season = b.season + 1
INNER JOIN team bb
ON b.playerteamname = bb.playerteamname AND b.season = bb.season
INNER JOIN fantasy_basketball.season_level_stats c
ON a.personid = c.personid AND a.season = c.season + 2
INNER JOIN team cc
ON c.playerteamname = cc.playerteamname AND c.season = cc.season
INNER JOIN fantasy_basketball.season_level_stats d
ON a.personid = d.personid AND a.season = d.season + 2
INNER JOIN team dd
ON d.playerteamname = dd.playerteamname AND d.season = dd.season
"""


df_temp = pd.read_sql(sql_text, connection)
df_temp['const'] = 1
print(df_temp.head())

x_vars = ['const', 'season_start_age','age_squared','minutes_played_lag_1','minutes_played_lag_2','minutes_played_lag_3',
          'trade_lag_1','trade_lag_2','trade_lag_3', 'player_win_pct_lag_1', 'player_win_pct_lag_2', 'player_win_pct_lag_3',
          'player_win_pct_lag_1', 'player_win_pct_lag_2', 'player_win_pct_lag_3','team_win_pct_lag_1','team_win_pct_lag_2','team_win_pct_lag_3']

x_train = df_temp[df_temp['season'] <= 2016][x_vars].fillna(0)
x_test = df_temp[df_temp['season'] > 2016][x_vars].fillna(0)
y_train = df_temp[df_temp['season'] <= 2016]['minutes_played'].fillna(0)
y_test = df_temp[df_temp['season'] > 2016]['minutes_played'].fillna(0)


def backward_elimination(X, y, significance_level=0.05):
    num_vars = X.shape[1]
    for i in range(num_vars):
        regressor_OLS = sm.OLS(y, X).fit()  # Fit model using Ordinary Least Squares (OLS)
        max_p_value = max(regressor_OLS.pvalues)  # Get the highest p-value
        if max_p_value > significance_level:  # If p-value is greater than the threshold, remove that predictor
            max_p_index = np.argmax(regressor_OLS.pvalues)
            X = np.delete(X, max_p_index, axis=1)
        else:
            break  # Stop when all p-values are below the significance level
    return X, regressor_OLS

X_optimized, final_model = backward_elimination(x_train, y_train)


print(final_model.summary())