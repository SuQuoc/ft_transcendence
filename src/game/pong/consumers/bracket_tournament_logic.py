

from django.core.cache import cache
from channels.layers import get_channel_layer

from .Room import TournamentRoom
from .utils import get_room_group, T_TOURNAMENT_MATCH
import random
import uuid


#asyncio.create_task()
async def start_tournament(room: TournamentRoom):
    """
    Starts the tournament logic in a bracket style
    """
    # start the tournament

    players = room.players
    while len(players) > 3:
        random.shuffle(players)
        pairs = make_pairs(players)
        
        winners = []
        losers = []
        matches = [
            {
                "match_id": uuid.uuid4(),
                "player1": pair[0],
                "player2": pair[1]
            }
            for pair in pairs
        ]
                
        await send_matches(get_room_group(room.name), matches)

        # result = wait for the GameConsumer to send the match result or a cancel message
            
        #winners.append(result.winner)
        #losers.append(result.loser)
        players = winners

async def send_matches(self, group_name, matches):
    await get_channel_layer().group_send(
        group_name,
        {
            "type": T_TOURNAMENT_MATCH,
            "matches": matches
        })
    



def make_pairs(list) -> list:
    return [list[i:i+2] for i in range(0, len(list), 2)]

# OLDIES
async def send_match_id(self, channel_name):
    await self.channel_layer.send(
        channel_name,
        {
            "type": "tournament_match",
            "match_id": "uuid",
            "player1": "player1",
            "player2": "player2"
        })