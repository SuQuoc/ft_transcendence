from .match import Match
from .pongPlayer import PongPlayer

from channels.layers import get_channel_layer

# This class would start when a lobby starts and manages the games !

class Lobby:

    def __init__(self, lobby_name=None, max_len=2) -> None:
        self.players: dict[str, PongPlayer] = {}
        self.lobby_name = lobby_name
        self.len = 0
        self.max_len = max_len
        self.matches: list[Match] = [Match(None, None, name=self.lobby_name + "_match" + str(i)) for i in range(0, max_len, 2)]

    def addPlayer(self, new_player: PongPlayer) -> None | str:
        if isinstance(new_player, PongPlayer) is False or new_player is None:
            print("[Error-Lobby] Player is wrong type or None")
            return
        if self.len >= self.max_len:
            print("[Warning-Lobby] Lobby full")
            return
        self.players[new_player.id] = new_player
        self.len = len(self.players)
        return self.addPlayerToMatch(new_player)

    def addPlayerToMatch(self, player: PongPlayer) -> None:
        for match in self.matches:
            if match.player1 is None:
                match.addPlayer(player)
                return match
            if match.player2 is None:
                match.addPlayer(player)
                return match
        print("[Error-Lobby] We a fucked up this should never happen")

    def removePlayer(self, player: PongPlayer) -> None:
        if player.id not in self.players:
            print("[Warning-Lobby] Player not in lobby")
            # Send msg ?
            return
        self.players.pop(player.id)
        self.len = len(self.players)
        for match in self.matches:
            if player in [match.player1, match.player2]:
                match.removePlayer(player)

    # This needs to be a bit more dynamic !
    # Returns None if lobby is not full !
    def startMatch(self) -> None | Match:
        if self.len != self.max_len:
            print("[Warning-Lobby] Not enough Players to start game")
            # Send msg ?
            return
        return self.matches

    def setWinner(self, game_nr, winner_nr):
        # If you give up on a function just pass xD
        pass

    """ def startNextRound(self):
        for game in self.game:
            games = game.  """
