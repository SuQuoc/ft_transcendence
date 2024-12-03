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

    while len(players) > 1:
        matches = await create_tournament_bracket(channel_group, players, room)
        await send_tournament_bracket(channel_group, matches)

        winners = set()
        msg_count = 0
        while msg_count != len(players):
            message = await queue.get()
            if message.get("type") == T_MATCH_RESULT:
                msg_count += 1
                winners.add(get_winner(players, message.get("winner")))
            elif message.get("type") == T_DC_IN_GAME:
                print("DC in game")
                msg_count += 1 
            elif message.get("type") == T_DC_OUT_GAME: # finished his game and dc while waiting
                print("DC out game")
                id = message.get("id")
                print(f"id: {id}")
                winners = {player for player in winners if player.id != id}
            queue.task_done() # NOTE: necessary in our case?
        print(f"winners: {winners}")
        players = winners

    if players:
        winner = players.pop()
        print("!!!!! Winner is: ", winner.name)
        await send_tournament_end(channel_group, winner.name)
    print("TOURNAMENT TASK FINISHED ==============")


def get_winner(players, winner_id) -> Player:
    for player in players:
        if player.id == winner_id:
            return player


def make_random_pairs(players) -> List[tuple]:
    """
    Shuffles the list and returns list of tuples with two elements.
    If list is odd, the last element is returned separately.
    If list is empty or has only one element, returns an empty list and None.
    """

    if isinstance(players, set):
        players = list(players)

    length = len(players)
    if length < 2:
        return [], None

    random.shuffle(players)
    if length % 2 != 0:
        odd_one = players.pop()
    odd_one = None
    return [tuple(players[i:i+2]) for i in range(0, length, 2)], odd_one


# TODO: UNUSED
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



async def create_tournament_bracket(channel_group, players, room):
    pairs, odd_one = make_random_pairs(players)
    if odd_one:
        await send_free_win(channel_group, odd_one.id)

    matches = [
            {
                "match_id": create_match_config([pair[0].id, pair[1].id],
                                                [pair[0].name, pair[1].name],
                                                GameMode.TOURNAMENT.value,
                                                points_to_win=room.points_to_win), # NOTE: creates a match in cache and stores who can connect
                "player1": pair[0].name,
                "player2": pair[1].name
            }
            for pair in pairs
        ]
    print(json.dumps(matches, indent=4))
    return matches

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
