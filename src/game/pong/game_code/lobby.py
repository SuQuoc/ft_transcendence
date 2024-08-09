from .match import Match
from .pongPlayer import PongPlayer

# This class would start when a lobby starts and manages the games !

class Lobby:

    def __init__(self, lobby_name=None, max_len=2) -> None:
        self.players: dict[str, PongPlayer] = {}
        self.lobby_name = lobby_name
        self.len = 0
        self.max_len = max_len
        self.matches: list[Match] = []

    def addPlayer(self, new_player: PongPlayer) -> None:
        if isinstance(new_player, PongPlayer) is False or new_player is None:
            print("[Error-Lobby] Player is wrong type or None")
            return False
        if self.len >= self.max_len:
            print("[Warning-Lobby] Lobby full")
            return False
        self.players[new_player.id] = new_player
        self.len = len(self.players)
        return True

    def removePlayer(self, player_id: str) -> None:
        if player_id not in self.players:
            print("[Warning-Lobby] Player not in lobby")
            # Send msg ?
            return
        self.players.pop(player_id)
        self.len = len(self.players)

    # This needs to be a bit more dynamic !
    # Returns None if lobby is not full !
    def startMatch(self) -> None | Match:
        if self.len != self.max_len:
            print("[Warning-Lobby] Not enough Players to start game")
            # Send msg ?
            return

        self.matches = self.split_dict_in_match(self.players)
        return self.matches

    def setWinner(self, game_nr, winner_nr):
        # If you give up on a function just pass xD
        pass

    def split_dict_in_match(self, input_dict: dict[str, PongPlayer]) -> list[dict]:
        players = list(input_dict.values())
        matches = [Match(players[i], players[i + 1]) for i in range(0, len(players), 2)]
        return matches

    """ def startNextRound(self):
        for game in self.game:
            games = game.  """
