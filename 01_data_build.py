import pandas as pd

from nba_api.stats.static import players
from nba_api.stats.endpoints import playercareerstats
from sqlalchemy import create_engine
import time


# get the set of all players
nba_players = players.get_players()
print("Number of players fetched: {}".format(len(nba_players)))

all_seasons = pd.DataFrame()

i = 1

#loop over players to make season level stats
for player in nba_players:
    id = player['id']
    #print(id)
    #print(player)
    try:
        career = playercareerstats.PlayerCareerStats(player_id=id)
        career_df = career.get_data_frames()[0]
        career_df['Player_Name'] = player['full_name']
        all_seasons = pd.concat([all_seasons, career_df], axis=0)
    except:
        print(f"passing player {player['full_name']}")
        pass
    time.sleep(1)
    print(f'{i}/{len(nba_players)}')
    i+=1

print(all_seasons.head())
print(all_seasons.columns)


sqlEngine = create_engine('mysql+pymysql://root:k2udaeV%40@localhost:3306/fantasy_basketball', pool_recycle=3600)
connection = sqlEngine.connect()

try:
    frame = all_seasons.to_sql(f"all_seasons", connection, if_exists='fail');

except ValueError as vx:
    print(vx)


#player, season, age, team, games played, minutes played, 9 cats
#
#team, season, win percent