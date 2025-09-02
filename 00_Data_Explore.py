## Documentation here: https://pypi.org/project/nba_api/

from nba_api.stats.endpoints import playercareerstats

# Nikola Jokić
career = playercareerstats.PlayerCareerStats(player_id='203999')
print(career.get_data_frames()[0])

from nba_api.stats.static import players
print(players.find_players_by_full_name('james'))