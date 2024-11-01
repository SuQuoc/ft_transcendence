import base64
import json
from django.core.cache import cache
from enum import Enum
import uuid


# TYPES of messages
T_ON_TOURNAMENT_PAGE = "on_tournament_page"
T_CREATE_ROOM = "create_room"
T_NEW_ROOM = "new_room"
T_ROOM_SIZE_UPDATE = "room_size_update"

T_JOIN_ROOM = "join_room"
T_PLAYER_JOINED_ROOM = "player_joined_room"

T_LEAVE_ROOM = "leave_room"
T_PLAYER_LEFT_ROOM = "player_left_room"
T_DELETE_ROOM = "delete_room"

T_GET_TOURNAMENT_LIST = "get_tournament_list"
T_TOURNAMENT_LIST = "tournament_list"

T_GET_ROOM_INFO = "get_room_info"
T_ROOM_INFO = "room_info"

T_START_TOURNAMENT = "start_tournament"
T_TOURNAMENT_BRACKET = "tournament_bracket"

T_SUCCESS = "success"
T_ERROR = "error"

# Cache keys
FULL_ROOMS = "full_rooms"
AVA_ROOMS = "available_rooms"

class Errors(Enum):
    NOT_IN_ROOM = "not_in_room"
    NO_CURRENT_ROOM = "no_current_room"
    ROOM_NAME_TAKEN = "room_name_taken"
    ROOM_DOES_NOT_EXIST = "room_does_not_exist"
    ROOM_FULL = "room_full"
    ROOM_NAME_INVALID = "room_name_invalid"
    ALREADY_IN_ROOM = "already_in_room"


def get_user_id_from_jwt(jwt_token: str):
    try:
        # Split the token to get the payload part (YY)
        payload_part = jwt_token.split('.')[1]
        
        # Decode the payload from Base64
        payload_decoded = base64.urlsafe_b64decode(payload_part + '==').decode('utf-8')
        user_id = json.loads(payload_decoded)['user_id']
        # Return the last 30 characters of the decoded payload
        return user_id
    except (IndexError, ValueError, base64.binascii.Error) as e:
        print(f"Error decoding JWT payload: {e}")


def update_or_add_room_to_cache(room: dict, cache_name, cached_data: dict=None, ):
    """
    Updates or adds a room to the cache. 
    If the cached_data is not provided, it gets the cached_data from the cache with the cache_name.
    """
    if not isinstance(room, dict):
        raise ValueError("room must be a dictionary.")
    if not cache_name:
        raise ValueError("cache_name must be provided.")
    if not cached_data:
        cached_data = cache.get(cache_name, {})

    cached_data.update({room["name"]: room})
    cache.set(cache_name, cached_data)


def del_room_from_cache(room_name, cache_name, cached_data: dict=None):
    """
    Deletes a room to the cache. 
    If the cached_data is not provided, it gets the cached_data from the cache with the cache_name.
    """
    
    if not cache_name:
        raise ValueError("cache_name must be provided.")
    if not cached_data:
        cached_data = cache.get(cache_name, {})

    del cached_data[room_name]
    cache.set(cache_name, cached_data)


def get_room_dict(room_name, available_rooms: dict, all_rooms: dict) -> dict:
    return available_rooms.get(room_name) or all_rooms.get(room_name)


def get_room_group(room_name: str):
    return f"tournament_{room_name}"


def create_match_access_list(user_id_list):
    """
    Creates an entry in cache to check which client is allowed to connect to which game
    """
    match_id = str(uuid.uuid4())
    cache.set(match_id, user_id_list) # used to confirm client to connecting to game
    return match_id