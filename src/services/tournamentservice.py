import json
import os

from database.tournaments import Tournament


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
            return [Tournament.from_dict(tournament) for tournament in tournaments]
        else:
            return []