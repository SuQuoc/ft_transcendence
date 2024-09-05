from .lobby import Lobby
from channels.layers import get_channel_layer

# This class is used to send messages to the client
class SendToClient:

    def __init__(self, joinTournamentPage_group_name):
        self.joinTournamentPage_group_name = joinTournamentPage_group_name

    # This function is used to create a dictionary of lobbies that will be sent to the client
    # The dictionary will contain the following information:
    # - The tournament name (lobby_name)
    # - The creator name (creator_name)
    # - The current number of players in the lobby (current_player_num)
    # - The maximum number of players in the lobby (max_player_num)
    async def createLobbyStatusDict(self, lobbies: dict) -> dict | None:
        if lobbies is None or len(lobbies) == 0:
            print("[WARNING] createLobbyStatusDict lobbies is None")
            return {}
        msg = {
                i: {
                    "tournament_name": lobby.lobby_name,
                    "creator_name": "creator",
                    "current_player_num": lobby.len,
                    "max_player_num": lobby.max_len,
                }
                for i, lobby in enumerate(lobbies.values())
            }
        return msg
    
    """ async def createLobbyStatusDict(self, lobbies: dict) -> dict | None:
        if lobbies is None or len(lobbies) == 0:
            print("[WARNING] createLobbyStatusDict lobbies is None")
            return {}
        msg = {
                lobby.lobby_name: {
                    "tournament_name": lobby.lobby_name,
                    "creator_name": "creator",
                    "current_player_num": lobby.len,
                    "max_player_num": lobby.max_len,
                }
                for lobby in lobbies.values()
            }
        return msg """

    # This function is used to send the lobby status to the client
    async def sendLobbyStatus(self, lobbies:dict) -> None:
        print("sendLobbyStatus")
        channel_layer = get_channel_layer()
        msg = await self.createLobbyStatusDict(lobbies)
        if msg is None:
            return
        msg["type"] = "update.tournamentList"
        await channel_layer.group_send(
            self.joinTournamentPage_group_name, msg )
        #    {
        #        "type": "update.tournamentList",
        #        "tournaments": msg
        #    }
        #)

    async def sendLobbyPlayerList(self, lobby: Lobby) -> None:
        print("update.LobbyPlayerList")
        channel_layer = get_channel_layer()
        msg = {
            i: {
                "player_name": "1",
            }
            for i, player in enumerate(lobby.players.values())
        }
        msg["type"] = "update.LobbyPlayerList"
        await channel_layer.group_send(
            lobby.lobby_name, msg
        )
