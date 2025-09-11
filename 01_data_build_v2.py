import pandas as pd
import datetime
from sqlalchemy import create_engine

def date_to_season(row):
    game_date = datetime.datetime.strptime(row['gameDate'], "%Y-%m-%d %H:%M:%S")

    season = game_date.year
    if game_date.month < 9:
        season = season - 1
    return season

## Read in Game Level Data

pd.set_option('display.max_columns', None)

print('Creating player Game Level Table')

df_all_season_stats_game_lvl = pd.read_csv('archive/PlayerStatistics.csv', low_memory=False)
df_all_season_stats_game_lvl['season'] = df_all_season_stats_game_lvl.apply(date_to_season, axis=1)
#print(df_all_season_stats_game_lvl.tail())

sqlEngine = create_engine('mysql+pymysql://root:k2udaeV%40@localhost:3306/fantasy_basketball', pool_recycle=3600)
connection = sqlEngine.connect()

try:
    frame = df_all_season_stats_game_lvl.to_sql(f"all_seasons_game_lvl", connection, if_exists='fail');

except ValueError as vx:
   print(vx)


print('Creating player Stats Table')
df_player_data = pd.read_csv('archive/Players.csv', low_memory=False)
#print(df_player_data.tail())

try:
    frame = df_player_data.to_sql(f"player_data", connection, if_exists='fail');

except ValueError as vx:
   print(vx)

print('Creating player season Level Table')

sql_text = """

create table Season_level_stats AS
SELECT plyr_stat.*,
        plyr.birthdate,
        team.first_game,
        ceiling(datediff(team.first_game, plyr.birthdate)/365) as season_start_age,
        (team.num_wins/team.num_games) as team_win_pct
FROM (
    SELECT season, 
        personId,
        playerteamName,
        CONCAT(FirstName, ' ' ,LastName) As Player_Name,
        count(distinct gameID) as games_played,
        sum(numMinutes) as minutes_played,
        sum(points) as total_points,
        sum(reboundsTotal) as total_rebounds,
        sum(assists) as total_assists,
        sum(steals) as total_steals,
        sum(blocks) as total_blocks,
        sum(fieldGoalsAttempted) as total_field_goals_attempted,
        sum(fieldGoalsMade) as total_field_goals_made,
        sum(freeThrowsAttempted) as total_free_throws_attempted,
        sum(freeThrowsMade) as total_free_throws_made,
        sum(threePointersMade) as total_three_pointers,
        SUM(turnovers) AS total_turnovers
    FROM fantasy_basketball.all_seasons_game_lvl
    WHERE gameType = 'Regular Season'
    GROUP BY season, personId, playerteamName, FirstName, LastName
    ) AS plyr_stat
LEFT JOIN fantasy_basketball.player_data plyr
ON plyr_stat.personID = plyr.personID
LEFT JOIN (
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
    ) team
ON plyr_stat.playerteamName = team.playerteamName AND plyr_stat.season = team.season
;
"""
df_temp = pd.read_sql(sql_text, connection)
print(df_temp)

