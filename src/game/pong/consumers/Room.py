import json

class Player:
    creation_keys = ["channel_name"]
    converting_keys = ["name"] # "user_id"]

    def __init__(self, **kwargs):
        for key in Player.creation_keys:
            if key not in kwargs:
                raise ValueError(f"Missing required key for instantiating: {key}")
        
        self.channel_name = kwargs.get("channel_name")
        self.name = kwargs.get("name")
        self.id = None
    
    @staticmethod
    def from_dict(data: dict):
        for key in Player.converting_keys:
            if key not in data:
                raise ValueError(f"Missing required key for converting from dict: {key}")
        return Player(**data)
    
    def to_dict(self):
        return {
            "channel_name": self.channel_name,
            "name": self.name
        }

    def __eq__(self, other):
        if isinstance(other, Player):
            return self.channel_name == other.channel_name
        raise ValueError("other must be an instance of Player")
        return False

    

# Potential Room class for tournaments
class TournamentRoom:
    AVAILABLE = "available"
    FULL = "full"

    creation_keys = [
        "name",
        "creator",
        "points_to_win",
        "max_player_num",
    ]

    converting_keys = [
        "players",
        "cur_player_num",
        "status"
    ]

    def __init__(self, **kwargs):
        for key in TournamentRoom.creation_keys:
            if key not in kwargs:
                raise ValueError(f"Missing required key for instantiating: {key}")
        
        # creation keys
        self.name = kwargs.get("name")
        self.creator = Player(**kwargs.get("creator"))

        self.points_to_win = int(kwargs.get("points_to_win"))
        self.max_player_num = int(kwargs.get("max_player_num"))

        # + converting keys
        if "players" in kwargs:
            self.players = [Player(**player_dict) for player_dict in kwargs.get("players")]
        else:
            self.players = [self.creator]

        self.cur_player_num = int(kwargs.get("cur_player_num", 1))
        self.status = kwargs.get("status", TournamentRoom.AVAILABLE)

        if self.points_to_win <= 0:
            raise ValueError("points_to_win must be a positive integer")
        if self.max_player_num <= 0:
            raise ValueError("max_player_num must be a positive integer")
        
    @staticmethod
    def from_dict(data: dict):
        for key in TournamentRoom.converting_keys:
            if key not in data:
                raise ValueError(f"Missing required key for converting from dict: {key}")
    
        return TournamentRoom(**data)
    
    def to_dict(self):
        # json.dumps(
        return {
            "name": self.name,
            "creator": self.creator.to_dict(),
            "players": [player.to_dict() for player in self.players] ,
            "points_to_win": self.points_to_win,
            "max_player_num": self.max_player_num,
            "cur_player_num": self.cur_player_num,
            "status": self.status
        }
    
    def to_data_for_client(self):
        """
        does the same as to_dict but without sensitive data
        """
        # json.dumps(
        return {
            "name": self.name,
            "creator_name": self.creator.name,
            "players": [player.name for player in self.players],
            "points_to_win": self.points_to_win,
            "max_player_num": self.max_player_num,
            "cur_player_num": self.cur_player_num,
            "status": self.status
        }

    def is_full(self):
        return self.cur_player_num == self.max_player_num
    
    def is_empty(self):
        return self.cur_player_num == 0
    
    def add_player(self, player: Player):
        if not isinstance(player, Player):
            raise ValueError("player must be an instance of Player")
        if self.is_full():
            raise ValueError(f"Lobby room '{self.name}' is max - SHOULD NEVER HAPPEN.")

        self.players.append(player)
        self.cur_player_num += 1
        if self.is_full():
            self.status = TournamentRoom.FULL
        return True
    
    def remove_player(self, player: Player):
        if not isinstance(player, Player):
            raise ValueError("player must be an instance of Player")
        
        # Logic is written so this can NEVER HAPPEN
        # elif player not in self.players:
            # return False 
            #raise ValueError(f"Player {player.name} is not in the room - SHOULD NEVER HAPPEN.")
        self.players.remove(player)
        self.cur_player_num -= 1
    
