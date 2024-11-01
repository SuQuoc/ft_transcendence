

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


#asyncio.create_task()
async def tournament_loop(room: TournamentRoom, queue):
    """
    Starts the tournament logic in a bracket style
    """
    players = room.players
    while len(players) > 1:
        random.shuffle(players)
        pairs: List[Player] = make_pairs(players)
        
        winners = []
        losers = []
        matches = [
            {
                "match_id": create_match_access_list([pair[0].id, pair[1].id]),
                "player1": pair[0].name,
                "player2": pair[1].name
            }
            for pair in pairs
        ]


        print("2) tournament loop - sending brackets to clients")

        await send_matches(get_room_group(room.name), matches)
        
        match_results = []
        for player in players:
            match_result = await queue.get()
            print(f"match_result: {match_result}")
            match_results.append(match_result)
            queue.task_done() # NOTE: necessary in our case?
        match_results = remove_duplicates(match_results)
        print(f"match_results: {json.dumps(match_results, indent=4)}")
        winners = [result["winner"] for result in match_results]    
        losers = [result["loser"] for result in match_results]
        players = winners


async def send_matches(group_name, matches):
    await get_channel_layer().group_send(
        group_name,
        {
            "type": T_TOURNAMENT_BRACKET,
            "matches": matches
        })
    

def make_pairs(list) -> list:
    return [list[i:i+2] for i in range(0, len(list), 2)]


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
        # Convert the dictionary to a frozenset of tuples to make it hashable
        result_tuple = frozenset(result.items())
        
        if result_tuple not in seen:
            seen.add(result_tuple)
            unique_results.append(result)
    
    return unique_results



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