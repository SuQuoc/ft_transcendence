from django.core.cache import cache

from .Room import TournamentRoom, Player
from .utils import get_room_group, T_TOURNAMENT_BRACKET, T_TOURNAMENT_END, T_FREE_WIN, T_MATCH_RESULT, T_DC_IN_GAME, T_DC_OUT_GAME
import random
import uuid
import json
import asyncio
from typing import List
from .utils import create_match_config
from .pong_game_consumer import GameMode
from channels.layers import get_channel_layer

channel_layer = get_channel_layer()

#asyncio.create_task()
async def tournament_loop(room: TournamentRoom, queue):
    """
    Starts the tournament logic in a bracket style
    """
    channel_group = get_room_group(room.name)

    winners = []
    players = room.players
    while len(players) > 1:
        pairs, odd_one = make_random_pairs(players)
        print(f"pairs: {pairs}")
        if odd_one:
            await send_free_win(channel_group, odd_one.id)
                    
        # await asyncio.sleep(20)
        winners = []
        losers = [] #!!
        matches = [
            {
                "match_id": create_match_config([pair[0].id, pair[1].id], GameMode.TOURNAMENT.value), # NOTE: creates a match in cache and stores who can connect
                "player1": pair[0].name,
                "player2": pair[1].name
            }
            for pair in pairs
        ]
        print(json.dumps(matches, indent=4))
        await send_tournament_bracket(channel_group, matches)
        
        match_results = []
        dc_in_game = 0
        dc_out_game = []
        while len(match_results) + dc_in_game < len(pairs) * 2:
            message = await queue.get()
            if message.get("type") == T_MATCH_RESULT:
                match_results.append(message)
            elif message.get("type") == T_DC_IN_GAME:
                dc_in_game += 1
            elif message.get("type") == T_DC_OUT_GAME: # finished his game and dc while waiting
                id = message.get("id")
                dc_out_game.append(id)
            queue.task_done() # NOTE: necessary in our case?

        match_results = remove_duplicates(match_results)
        winners = [result.get("winner") for result in match_results]    
        losers = [result.get("loser") for result in match_results]
        players = [player for player in players if player.id in winners]
        if dc_out_game:
            players = [player for player in players if player.id not in dc_out_game]

    winner_name = players[0].name
    await send_tournament_end(channel_group, winner_name)
    print("END OF TOURNAMENT ======\n")


def make_random_pairs(list) -> List[tuple]:
    """
    Shuffles the list and returns list of tuples with two elements. 
    If list is odd, the last element is returned separately.
    If list is empty or has only one element, returns an empty list and None.
    """
    length = len(list)
    if length < 2:
        return [], None
    
    random.shuffle(list)
    if length % 2 != 0:
        odd_one = list.pop()
    odd_one = None
    return [tuple(list[i:i+2]) for i in range(0, length, 2)], odd_one


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
        
        winner = result["winner"]
        if winner not in seen:
            seen.add(winner)
            unique_results.append(result)
    return unique_results


async def send_tournament_bracket(group_name, matches):
    await channel_layer.group_send(
        group_name,
        {
            "type": T_TOURNAMENT_BRACKET,
            "matches": matches
        })


async def send_tournament_end(group_name, winner):
    await channel_layer.group_send(
        group_name,
        {
            "type": T_TOURNAMENT_END,
            "winner": winner 
        })


async def send_free_win(group_name, user_id):
    await channel_layer.group_send(
        group_name,
        {
            "type": T_FREE_WIN,
            "user_id": user_id
        })