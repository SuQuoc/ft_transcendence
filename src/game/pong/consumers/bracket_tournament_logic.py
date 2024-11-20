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


    players = room.players
    pairs, odd_one = make_random_pairs(players)
    if odd_one:
        await send_free_win(channel_group, odd_one.id)
    # someone left while waiting for other match to end

    while len(players) > 1:
        matches = [
            {
                "match_id": create_match_config([pair[0].id, pair[1].id],
                                                GameMode.TOURNAMENT.value,
                                                points_to_win=room.points_to_win), # NOTE: creates a match in cache and stores who can connect
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
            print("MESSAGE ARRIVED")
            if message.get("type") == T_MATCH_RESULT:
                match_results.append(message)
            elif message.get("type") == T_DC_IN_GAME:
                print("DC in game")
                dc_in_game += 1
            elif message.get("type") == T_DC_OUT_GAME: # finished his game and dc while waiting
                print("DC out game")
                id = message.get("id")
                dc_out_game.append(id)
            queue.task_done() # NOTE: necessary in our case?

        match_results = remove_duplicates(match_results)
        if match_results:
            winners = get_winners(match_results, players)

        if dc_out_game:
            winners = [winner for winner in winners if winner.id not in dc_out_game]

        pairs, odd_one = make_random_pairs(winners)
        if odd_one:
            await send_free_win(channel_group, odd_one.id)
        players = winners

    if players:
        winner_name = players[0].name
        print("!!!!! Winner is: ", winner_name)
        await send_tournament_end(channel_group, winner_name)
    print("TOURNAMENT TASK FINISSHED ==============")

def get_winners(match_results, players) -> List[Player]:
    winner_ids = [result.get("winner") for result in match_results]
    return [player for player in players if player.id in winner_ids]

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
    if not match_results:
        return []

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
    """
    Sends a free win message to a user if player count is odd due to disconnections
    """
    await channel_layer.group_send(
        group_name,
        {
            "type": T_FREE_WIN,
            "winner_id": user_id
        })
