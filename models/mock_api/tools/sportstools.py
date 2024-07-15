from models.mock_api.pycragapi import CRAG

class SportsTools:
    def __init__(self):
        self.api = CRAG()
        self.nba_teams = ["Atlanta Hawks", "Boston Celtics", "Brooklyn Nets", "Charlotte Hornets", "Chicago Bulls", "Cleveland Cavaliers", "Dallas Mavericks", "Denver Nuggets", "Detroit Pistons", "Golden State Warriors", "Houston Rockets", "Indiana Pacers", "Los Angeles Clippers", "Los Angeles Lakers", "Memphis Grizzlies", "Miami Heat", "Milwaukee Bucks", "Minnesota Timberwolves", "New Orleans Pelicans", "New York Knicks", "Oklahoma City Thunder", "Orlando Magic", "Philadelphia 76ers", "Phoenix Suns", "Portland Trail Blazers", "Sacramento Kings", "San Antonio Spurs", "Toronto Raptors", "Utah Jazz", "Washington Wizards"]
        self.nba_teams_alter = {
            "Atlanta Hawks": ["Hawks", "Atlanta", "ATL"],
            "Boston Celtics": ["Celtics", "Boston", "BOS"],
            "Brooklyn Nets": ["Nets", "Brooklyn", "BKN"],
            "Charlotte Hornets": ["Hornets", "Charlotte", "CHA"],
            "Chicago Bulls": ["Bulls", "Chicago", "CHI"],
            "Cleveland Cavaliers": ["Cavaliers", "Cleveland", "CLE"],
            "Dallas Mavericks": ["Mavericks", "Dallas", "DAL"],
            "Denver Nuggets": ["Nuggets", "Denver", "DEN"],
            "Detroit Pistons": ["Pistons", "Detroit", "DET"],
            "Golden State Warriors": ["Warriors", "Golden State", "GSW"],
            "Houston Rockets": ["Rockets", "Houston", "HOU"],
            "Indiana Pacers": ["Pacers", "Indiana", "IND"],
            "Los Angeles Clippers": ["Clippers", "LA Clippers", "LAC"],
            "Los Angeles Lakers": ["Lakers", "LA Lakers", "LAL"],
            "Memphis Grizzlies": ["Grizzlies", "Memphis", "MEM"],
            "Miami Heat": ["Heat", "Miami", "MIA"],
            "Milwaukee Bucks": ["Bucks", "Milwaukee", "MIL"],
            "Minnesota Timberwolves": ["Timberwolves", "Minnesota", "MIN"],
            "New Orleans Pelicans": ["Pelicans", "New Orleans", "NOP"],
            "New York Knicks": ["Knicks", "New York", "NYK"],
            "Oklahoma City Thunder": ["Thunder", "Oklahoma City", "OKC"],
            "Orlando Magic": ["Magic", "Orlando", "ORL"],
            "Philadelphia 76ers": ["76ers", "Philadelphia", "PHI"],
            "Phoenix Suns": ["Suns", "Phoenix", "PHX"],
            "Portland Trail Blazers": ["Trail Blazers", "Portland", "POR"],
            "Sacramento Kings": ["Kings", "Sacramento", "SAC"],
            "San Antonio Spurs": ["Spurs", "San Antonio", "SAS"],
            "Toronto Raptors": ["Raptors", "Toronto", "TOR"],
            "Utah Jazz": ["Jazz", "Utah", "UTA"],
            "Washington Wizards": ["Wizards", "Washington", "WAS"]
        }
        self.soccer_leagues = ["ENG-Premier League", "ESP-La Liga", "FRA-Ligue 1"]
        self.soccer_teams = ["Nott\'ham Forest", "Alavés", "Almería", "Arsenal", "Aston Villa", "Athletic Club", "Atlético Madrid", "Barcelona", "Betis", "Bournemouth", "Brentford", "Brest", "Brighton", "Burnley", "Celta Vigo", "Chelsea", "Clermont Foot", "Crystal Palace", "Cádiz", "Everton", "Fulham", "Getafe", "Girona", "Granada", "Las Palmas", "Le Havre", "Lens", "Lille", "Liverpool", "Lorient", "Luton Town", "Lyon", "Mallorca", "Manchester City", "Manchester Utd", "Marseille", "Metz", "Monaco", "Montpellier", "Nantes", "Newcastle Utd", "Nice", "Osasuna", "Paris S-G", "Rayo Vallecano", "Real Madrid", "Real Sociedad", "Reims", "Rennes", "Sevilla", "Sheffield Utd", "Strasbourg", "Tottenham", "Toulouse", "Valencia", "Villarreal", "West Ham", "Wolves"]
        self.soccer_teams_alter = {
            "Nott\'ham Forest": ["Nottham Forest"],
            "Alavés": [],
            "Almería": [],
            "Arsenal": [],
            "Aston Villa": [],
            "Athletic Club": [],
            "Atlético Madrid": [],
            "Barcelona": [],
            "Betis": [],
            "Bournemouth": [],
            "Brentford": [],
            "Brest": [],
            "Brighton": [],
            "Burnley": [],
            "Celta Vigo": [],
            "Chelsea": [],
            "Clermont Foot": [],
            "Crystal Palace": [],
            "Cádiz": [],
            "Everton": [],
            "Fulham": [],
            "Getafe": [],
            "Girona": [],
            "Granada": [],
            "Las Palmas": [],
            "Le Havre": [],
            "Lens": [],
            "Lille": [],
            "Liverpool": [],
            "Lorient": [],
            "Luton Town": [],
            "Lyon": [],
            "Mallorca": [],
            "Manchester City": [],
            "Manchester Utd": [],
            "Marseille": [],
            "Metz": [],
            "Monaco": [],
            "Montpellier": [],
            "Nantes": [],
            "Newcastle Utd": [],
            "Nice": [],
            "Osasuna": [],
            "Paris S-G": [],
            "Rayo Vallecano": [],
            "Real Madrid": [],
            "Real Sociedad": [],
            "Reims": [],
            "Rennes": [],
            "Sevilla": [],
            "Sheffield Utd": [],
            "Strasbourg": [],
            "Tottenham": [],
            "Toulouse": [],
            "Valencia": [],
            "Villarreal": [],
            "West Ham": [],
            "Wolves": []
        }

    
    def get_nba_teams(self, query:str):
        teams = []
        for team in self.nba_teams:
            if team.lower() in query.lower():
                teams.append(team)
            else:
                for alt_name in self.nba_teams_alter[team]:
                    if len(alt_name) > 3 and alt_name.lower() in query.lower():
                       teams.append(team)
                    if len(alt_name) == 3:
                        query_split = query.split()
                        for q in query_split:
                            if alt_name.lower() == q.lower():
                                teams.append(team)
        return teams
    
    def get_soccer_teams(self, query:str):
        teams = []
        for team in self.soccer_teams:
            if team.lower() in query.lower():
                teams.append(team)
            else:
                for alt_name in self.soccer_teams_alter[team]:
                    if alt_name.lower() in query.lower():
                        teams.append(team)
        return teams
    
    def get_soccer_leagues(self, query:str):
        leagues = []
        for league in self.soccer_leagues:
            if league.lower() in query.lower():
                leagues.append(league)
        return leagues

    def soccer_get_games_on_date(self, date_str:str, soccer_team_name:str = None):
        """ 
            Description: Get all soccer game rows given date_str
            Input: 
                - soccer_team_name: soccer team name, if None, get results for all teams
                - date_str: in format of %Y-%m-%d, %Y-%m or %Y, e.g. 2024-03-01, 2024-03, 2024
            Output: a json contains info of the games
        """
        games = self.api.sports_soccer_get_games_on_date(date_str, soccer_team_name)['result']
        games_ = {}
        if games is None:
            return None
        else:
            keys = games.keys()
            keys_ = games["date"].keys()
            for key in keys_:
                games_[key] = {}
                for k in keys:
                    games_[key][k] = games[k][key]
                    if k == "date":
                        games_[key][k] = games_[key][k][:10]
            return games_

    def nba_get_games_on_date(self, date_str:str, nba_team_name:str = None):
        """ 
            Description: Get all NBA game rows given date_str
            Input: 
                - nba_team_name: NBA team name, if None, get results for all teams
                - date_str: in format of %Y-%m-%d, %Y-%m or %Y, e.g. 2024-03-01, 2024-03, 2024
            Output: a json contains info of the games
        """
        return self.api.sports_nba_get_games_on_date(date_str, nba_team_name)['result']

    def nba_get_play_by_play_data_by_game_ids(self, game_ids: list):
        """ 
            Description: Get all nba play by play rows given game ids
            Input: list of nba game ids, e.g., ["0022200547", "0029600027"]
            Output: info of the play by play events of given game id
        """
        return self.api.sports_nba_get_play_by_play_data_by_game_ids(game_ids)['result']