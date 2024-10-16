# Potential Room class for tournaments
class LobbyRoom:
    def __init__(self, room_name, creator_name, players): # players is a list of players
        self.room_name = room_name
        self.players = players
        self.creator_name = None

    def to_json(self):
        return json.dumps({
            "name": self.name,
            "players": self.players
        })

    @staticmethod
    def from_json(json_str):
        data = json.loads(json_str)
        return LobbyRoom(data["room_name"], data["creator_name"], data["players"])