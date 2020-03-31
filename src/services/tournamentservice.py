import json
import os


class TournamentService:
    @staticmethod
    def store_tournaments(tournaments, path='./tourney_data/tourneys.tmt'):
        tournaments = [tournament.to_dict() for tournament in tournaments]
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as f:
            json.dump(tournaments, f)
        return

    @staticmethod
    def load_tournaments(path='./tourney_data/tourneys.tmt'):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if os.path.exists(path):
            with open(path, 'r') as f:
                tournaments = json.loads(f.read())
            print(tournaments)
            return tournaments
        else:
            return []