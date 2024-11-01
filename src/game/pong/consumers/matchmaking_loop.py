# APPROACH IF THE MATCHMAKING IS MORE COMPLEX: 
# own background task where a consumer sends messages to the task via queues

import asyncio
from channels.layers import get_channel_layer
from django.core.cache import cache
import uuid


matchmaking_queue = asyncio.Queue()
channel_layer = get_channel_layer()


async def matchmaking_loop():
    while True:
        # EXPECTING THIS --> matchmaking_queue.put({"uuid": "player1", "channel_name": "channel1"})
        player1 = await matchmaking_queue.get()
        player2 = await matchmaking_queue.get()

        # Implement logic to notify players they’ve been matched
        print(f"Matched {player1["uuid"]} and {player2["uuid"]}")

        id = str(uuid.uuid4())
        cache.set(id, [player1["uuid"], player2["uuid"]])

        # Notify the players (This can be via a websocket, etc.)
        # Here you would send messages through Django Channels or other methods
        send_players_where_to_connect_to(id, player1["channel_name"])
        send_players_where_to_connect_to(id, player2["channel_name"])


async def send_players_where_to_connect_to(uuid: str, channel_name):
        if not isinstance(uuid, str):
            uuid = str(uuid)

        await channel_layer.send(
            channel_name,
            {
                'type': 'match_found',
                'match_id': uuid
            })
       
