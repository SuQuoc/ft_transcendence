from .lobby import Lobby

# This function is used to create a dictionary of lobbies that will be sent to the client
# The dictionary will contain the following information:
# - The tournament name (lobby_name)
# - The creator name (creator_name)
# - The current number of players in the lobby (current_player_num)
# - The maximum number of players in the lobby (max_player_num)
async def createLobbyStatusDict(lobbies: dict) -> dict | None:
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
