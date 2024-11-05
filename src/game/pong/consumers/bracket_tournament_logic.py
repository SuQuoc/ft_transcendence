

from django.core.cache import cache
from channels.layers import get_channel_layer

from .Room import TournamentRoom, Player
from .utils import get_room_group, T_TOURNAMENT_BRACKET
import random
import uuid
import json
import asyncio
from typing import List
from .utils import create_match_access_list
from .pong_game_consumer import GameMode

#asyncio.create_task()
async def tournament_loop(room: TournamentRoom, queue):
    """
    Starts the tournament logic in a bracket style
    """
    players = room.players
    while len(players) > 1:
        random.shuffle(players)
        pairs = make_pairs(players)
        print(f"pairs: {pairs}")
        # await asyncio.sleep(20)
        winners = []
        losers = []
        matches = [
            {
                "match_id": create_match_access_list([pair[0].id, pair[1].id], GameMode.TOURNAMENT.value), # NOTE: creates a match in cache and stores who can connect
                "player1": pair[0].name,
                "player2": pair[1].name
            }
            for pair in pairs
        ]
        print(json.dumps(matches, indent=4))
        await send_matches(get_room_group(room.name), matches)
        
        match_results = []
        for player in players:
            match_result = await queue.get()
            print(f"match_result IN TOURNAMENT TASK: {match_result}")
            match_results.append(match_result)
            queue.task_done() # NOTE: necessary in our case?

        match_results = remove_duplicates(match_results)
        print(f"match_results: {json.dumps(match_results, indent=4)}")
        winners = [result.get("winner") for result in match_results]    
        losers = [result.get("loser") for result in match_results]
        players = [player for player in players if player.id in winners]

    
    print("END OF TOURNAMENT ======\n")
    await send_tournament_end(get_room_group(room.name), winners[0])



async def send_tournament_end(group_name, winner):
    await get_channel_layer().group_send(
        group_name,
        {
            "type": "tournament_end",
            "winner": winner 
        })
    



async def send_matches(group_name, matches):
    await get_channel_layer().group_send(
        group_name,
        {
            "type": T_TOURNAMENT_BRACKET,
            "matches": matches
        })
    

def make_pairs(list) -> List[tuple]:
    return [tuple(list[i:i+2]) for i in range(0, len(list), 2)]


def remove_duplicates(match_results):
    """
    Removes duplicates from a list of dictionaries.
    
    Args:
        match_results (list): A list of dictionaries representing match results.
        
    Returns:
        list: A list of dictionaries with duplicates removed.
    """
    seen = set()
    unique_results = []
    
    for result in match_results:
        if not isinstance(result, dict):
            result = json.loads(result)

        # Convert the dictionary to a frozenset of tuples to make it hashable
        result_tuple = frozenset(result.items())
        
        if result_tuple not in seen:
            seen.add(result_tuple)
            unique_results.append(result)
    
    return unique_results

