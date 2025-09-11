## Documentation here: https://pypi.org/project/nba_api/

from nba_api.stats.endpoints import playercareerstats
import pandas as pd
pd.set_option('display.max_columns', None)

# Nikola Jokić
career = playercareerstats.PlayerCareerStats(player_id='203999')
print(career.get_data_frames()[0])

from nba_api.stats.static import players
print(players.find_players_by_full_name('james'))


nba_players = players.get_players()
print("Number of players fetched: {}".format(len(nba_players)))
print(nba_players[:5])

limit = 5
count = 0

for player in nba_players:
    id = player['id']
    print(id)
    career = playercareerstats.PlayerCareerStats(player_id=id)
    career_df = career.get_data_frames()[0]
    career_df['PLayer_Name'] = player['full_name']
    print(career_df)
    count = count+1
    if count > limit:
        break