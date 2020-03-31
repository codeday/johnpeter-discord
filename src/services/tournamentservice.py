import json


class TournamentService:
    @staticmethod
    def store_tournaments(tournaments):
        tournaments = [tournament.to_dict() for tournament in tournaments]
        with open('./tourney_data/tourneys.tmt', 'w') as f:
            json.dumps(tournaments, f)
        return

    @staticmethod
    def load_tournaments():
        with open('./tourney_data/tourneys.tmt', 'r') as f:
            tournaments = json.loads(f)
        print(tournaments)
        return tournaments
