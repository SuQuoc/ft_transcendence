
class Player:
    creation_keys = ["channel_name"]
    converting_keys = ["name, user_id, image"]

    def __init__(self, **kwargs):
        for key in Player.creation_keys:
            if key not in kwargs:
                raise ValueError(f"Missing required key for instantiating: {key}")

        self.channel_name   = kwargs.get("channel_name")
        self.name           = kwargs.get("name")
        self.id             = kwargs.get("id")
        self.image          = kwargs.get("image")
    
    @staticmethod
    def from_dict(data: dict):
        for key in Player.converting_keys:
            if key not in data:
                raise ValueError(f"Missing required key for converting from dict: {key}")
        return Player(**data)

    def to_dict(self):
        return {
            "channel_name": self.channel_name,
            "name": self.name,
            "id": self.id,
            "image": self.image
        }

    def to_data_for_client(self):
        return {
            "name": self.name,
            "image": self.image
        }

    def __eq__(self, other):
        # Mainly to check if instance is in another data structure
        if isinstance(other, Player):
            return self.channel_name == other.channel_name
        raise ValueError("other must be an instance of Player")

    def __hash__(self):
        return hash(self.channel_name)

    def __str__(self) -> str:
        return f"Player: {self.name}, user_id: {self.id}"

    def __repr__(self) -> str:
        return f"Player: {self.name}, user_id: {self.id}"


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
        self.creator_name = self.creator.name
        self.points_to_win = int(kwargs.get("points_to_win"))
        self.max_player_num = int(kwargs.get("max_player_num"))

        # + converting keys
        if "players" in kwargs: # if instance is created from data in cache
            self.players = [Player(**player_dict) for player_dict in kwargs.get("players")]
        else: # if instance newly created
            self.players = [self.creator]
        self.player_names = [player.name for player in self.players]

        self.cur_player_num = int(kwargs.get("cur_player_num", 1))
        self.status = kwargs.get("status", TournamentRoom.AVAILABLE)

        # NOTE: not necessary if django form validation is used
        # which means validating user input before going any further
        if self.points_to_win <= 0:
            raise ValueError("points_to_win must be a positive integer")
        if self.max_player_num <= 0:
            raise ValueError("max_player_num must be a positive integer")

    @staticmethod
    def clean_data(rooms: dict):
        for room in rooms.values():
            room: dict
            room.pop("creator", None)
            room.pop("players_backend", None)
        return

    @staticmethod
    def from_dict(data: dict):
        for key in TournamentRoom.converting_keys:
            if key not in data:
                raise ValueError(f"Missing required key for converting from dict: {key}")

        return TournamentRoom(**data)

    def to_dict(self):
        return {
            "name": self.name,
            "creator": self.creator.to_dict(),
            "creator_name": self.creator_name,
            "players": [player.to_dict() for player in self.players],
            "player_names": [player.name for player in self.players],
            "points_to_win": self.points_to_win,
            "max_player_num": self.max_player_num,
            "cur_player_num": self.cur_player_num,
            "status": self.status
        }

    def to_data_for_client(self):
        """
        does the same as to_dict but without sensitive data, only leaves out the channel_name
        """
        return {
            "name": self.name,
            "creator_name": self.creator.name,
            "players": [player.to_data_for_client() for player in self.players],
            "points_to_win": self.points_to_win,
            "max_player_num": self.max_player_num,
            "cur_player_num": self.cur_player_num,
            "status": self.status
        }

    def is_full(self):
        return self.cur_player_num == self.max_player_num

    def is_empty(self):
        return self.cur_player_num == 0

    def has_player(self, player_id):
        for player in self.players:
            if player.id == player_id:
                return True
        return False

    def add_player(self, player: Player):
        if not isinstance(player, Player):
            raise ValueError("player must be an instance of Player")
        if self.is_full():
            raise ValueError(f"Lobby room '{self.name}' is max - SHOULD NEVER HAPPEN.")
        if self.has_player(player.id):
            raise AlreadyInRoom()

        self.players.append(player)
        self.cur_player_num += 1
        if self.is_full():
            self.status = TournamentRoom.FULL
        return True

    def remove_player(self, player: Player):
        if not isinstance(player, Player):
            raise ValueError("player must be an instance of Player")

        self.players.remove(player)
        self.cur_player_num -= 1


class AlreadyInRoom(Exception):
    """Custom exception type for room-related errors."""
    def __init__(self, message="User is already in the room."):
        self.message = message
        super().__init__(self.message)
