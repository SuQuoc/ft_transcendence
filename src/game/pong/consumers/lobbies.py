import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.cache import cache  # Import Django"s cache
from .Room import TournamentRoom, Player, AlreadyInRoom
from .utils import *
from pong.forms import CreateTournamentForm
import asyncio
from .bracket_tournament_logic import tournament_loop
import httpx

# Dependency to other Microservice
async def get_profile(cookie_dict):
    if not cookie_dict:
        raise Exception('No cookie provided')
    cookie = httpx.Cookies(cookie_dict)
    headers = {
        'Content-Type': 'application/json',
    }
    async with httpx.AsyncClient() as client:
        response = await client.get("http://usermanagement:8000/um/profile", headers=headers, cookies=cookie_dict) # NOTE: fetches more then just the name
        if response.status_code != 200:
            raise Exception('Error getting displayname from UM')
        data = response.json()
        return data.get("displayname"), data.get("image")

# PROVING: global_connection_list = []

class LobbiesConsumer(AsyncWebsocketConsumer):
    update_lock = asyncio.Lock()
    room_queues = {}
    
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.user = None
        self.current_room = None
        self.client_group = None
        # Tournament vars
        self.queue = None
        self.in_game = False

    
    async def set_instance_values(self):
        self.user = Player(channel_name=self.channel_name)
        self.user.id = self.scope["user_id"]
        name, image = await get_profile(self.scope.get("cookies"))
        self.user.name = name
        self.user.image = image
        # Communication between consumers
        self.client_group = f"client_{self.user.id}"
        
    
    async def connect(self):
        try:
            await self.set_instance_values()
        except Exception as e:
            print(f"Exception: {e}")
            await self.disconnect(1008)
            return
        
        await self.accept()
        await self.channel_layer.group_add(self.client_group, self.channel_name)
        await self.channel_layer.group_add(AVA_ROOMS, self.channel_name)

        #time.sleep(100) # no one can do anything with the consumer for the time 
        #await asyncio.sleep(10) # others can still connect instantly, but the client connecting has to wait T time for messages following connect to be handled
        #asyncio.sleep(10) # doesnt do anything
        

    async def disconnect(self, close_code):
        if self.current_room:
            await self.leave_room()
        
        await self.channel_layer.group_discard(self.client_group, self.channel_name)
        await self.channel_layer.group_discard(AVA_ROOMS, self.channel_name)
        await super().disconnect(close_code)

    async def receive(self, text_data):
        """WEBSOCKET MESSAGE HANDLER"""
        try:
            dict_data = json.loads(text_data) # convert message from client to dict
            type = dict_data.get("type")

            # handle websocket message from client
            if type == T_CREATE_ROOM:
                await self.create_room(dict_data)

            elif type == T_JOIN_ROOM:
                await self.join_room(dict_data)

            elif type == T_LEAVE_ROOM:
                await self.leave_room()

            elif type == T_GET_ROOM_INFO:
                await self.send_room_info(dict_data)

            elif type == T_GET_TOURNAMENT_LIST:
                await self.get_tournament_list()

        except Exception as e:
            print(f"Exception: {e}")


    ### Client MESSAGES ###
    async def create_room(self, dict_data):
        if self.current_room:
            await self.send_error(Errors.ALREADY_IN_ROOM)
            return
        
        form = CreateTournamentForm(dict_data)
        if form.is_valid():
            room_name = form.cleaned_data.get("room_name")
            points_to_win = form.cleaned_data.get("points_to_win")
            max_player_num = form.cleaned_data.get("max_player_num")
        else:
            await self.send_error(Errors.ROOM_NAME_INVALID)
            return 

        async with self.update_lock:
            available_rooms = cache.get(AVA_ROOMS, {})
            if room_name in available_rooms or room_name in cache.get(FULL_ROOMS, {}):
                await self.send_error(Errors.ROOM_NAME_TAKEN)
                return
        
            # Add the new room to the list of available_rooms
            room = TournamentRoom(
                name            = room_name,
                creator         = self.user.to_dict(),
                points_to_win   = points_to_win,
                max_player_num  = max_player_num
            )

            available_rooms[room_name] = room.to_dict()
            cache.set(AVA_ROOMS, available_rooms)
            self.current_room = room_name

        await self.group_switch(AVA_ROOMS, get_room_group(room_name))
        await self.send_success(room_name)
        await self.group_send_AvailableTournaments(T_NEW_ROOM, room)


    async def join_room(self, dict_data):
        room_name = dict_data.get("room_name")

        async with self.update_lock:
            available_rooms = cache.get(AVA_ROOMS, {})
            if self.current_room is not None:
                await self.send_error(Errors.ALREADY_IN_ROOM)
                return
            
            if room_name not in available_rooms: # SHOULD NEVER HAPPEN
                await self.send_error(Errors.ROOM_DOES_NOT_EXIST)
                return
            
            await self.add_player_to_room(room_name, available_rooms)

       
    async def leave_room(self):
        """Helper method to remove a user from a lobby."""
        if self.current_room is None: # SHOULD NEVER HAPPEN with our Frontend
            await self.send_error(Errors.NO_CURRENT_ROOM)
            return
        
        async with self.update_lock:
            available_rooms = cache.get(AVA_ROOMS, {})
            full_rooms = cache.get(FULL_ROOMS, {})

            room_dict = get_room_dict(self.current_room, available_rooms, full_rooms)
            if room_dict is None:
                raise ValueError(Errors.ROOM_DOES_NOT_EXIST) # SHOULD NEVER HAPPEN
            
            room = TournamentRoom.from_dict(room_dict)
            if self.user not in room.players:
                raise ValueError(Errors.NOT_IN_ROOM) # SHOULD NEVER HAPPEN
            
            room.remove_player(self.user)

            if room.status == TournamentRoom.AVAILABLE:
                if room.is_empty():
                    del_room_from_cache(room.name, AVA_ROOMS, available_rooms)
                    await self.group_send_AvailableTournaments(T_DELETE_ROOM, room)
                else:
                    update_or_add_room_to_cache(room.to_dict(), AVA_ROOMS, available_rooms)
                    await self.group_send_AvailableTournaments(T_ROOM_SIZE_UPDATE, room)             
            
            elif room.status == TournamentRoom.FULL: # just indicates that it was full at some point
                if room.is_empty():
                    del_room_from_cache(room.name, FULL_ROOMS, full_rooms)
                else:
                    update_or_add_room_to_cache(room.to_dict(), FULL_ROOMS, full_rooms)
            
        
        # CHANNELS: Remove user from the tournament room group
        await self.group_switch(get_room_group(self.current_room), AVA_ROOMS)
        await self.group_send_Room(T_PLAYER_LEFT_ROOM, room)
        self.current_room = None

        if self.queue:
            await self.leave_ongoing_tournament()
            
    async def leave_ongoing_tournament(self):
        if self.in_game:
            await self.queue.put({"type": T_DC_IN_GAME, "id": self.user.id})
        else:
            await self.queue.put({"type": T_DC_OUT_GAME, "id": self.user.id})

    async def get_tournament_list(self):
        """Sends the list of AVAILABLE tournament rooms to the client."""

        available_rooms = cache.get(AVA_ROOMS, {})
        TournamentRoom.clean_data(available_rooms)
        
        text_data=json.dumps({
            "type": T_TOURNAMENT_LIST,
            "tournaments": available_rooms
        })
        await self.send(text_data=text_data)
    

    async def send_room_info(self, dict_data):
        """
        Sends the information of a room to the client who joined a room and requested info.
        """
        room_name = dict_data.get("room_name")
        available_rooms = cache.get(AVA_ROOMS, {})
        full_rooms = cache.get(FULL_ROOMS, {})
        room = get_room_dict(room_name, available_rooms, full_rooms)
        room = TournamentRoom.from_dict(room)

        if room is None:
            await self.send_error(Errors.ROOM_DOES_NOT_EXIST)
            return

        await self.send(text_data=json.dumps({
            "type": T_ROOM_INFO,
            "room": room.to_data_for_client()
        }))


    # GROUP SENDS-------------------------------------------------    
    async def group_send_AvailableTournaments(self, type, room: TournamentRoom):
        if not isinstance(room, TournamentRoom):
            raise ValueError("room must be a TournamentRoom object.")

        if type == T_NEW_ROOM:
            await self.channel_layer.group_send(
                AVA_ROOMS,
                {
                    "type": type,
                    "room": room.to_data_for_client()
                })
            
        elif type == T_DELETE_ROOM:
            await self.channel_layer.group_send(
                AVA_ROOMS,
                {
                    "type": type,
                    "room_name": room.name
                })
            
        elif type == T_ROOM_SIZE_UPDATE:
            await self.channel_layer.group_send(
                AVA_ROOMS,
                {
                    "type": type,
                    "room_name": room.name,
                    "cur_player_num": room.cur_player_num
                })

    async def group_send_Room(self, type, room: TournamentRoom):
        if not isinstance(room, TournamentRoom):
            raise ValueError("room must be a TournamentRoom object.")            
        if type == T_PLAYER_JOINED_ROOM:
            await self.channel_layer.group_send(
                get_room_group(room.name),
                {
                    "type": type,
                    "displayname": self.user.name,
                    "image": self.user.image,
                    "cur_player_num": room.cur_player_num,
                }
            )
        elif type == T_PLAYER_LEFT_ROOM:
            await self.channel_layer.group_send(
                get_room_group(room.name),
                {
                    "type": type,
                    "displayname": self.user.name,
                    "cur_player_num": room.cur_player_num,
                }
            )

    ### EVENTS - each Websocket in the group sends message to it's client ###
    async def new_room(self, event):
        await self.send(text_data=json.dumps(event))

    async def delete_room(self, event):
        await self.send(text_data=json.dumps(event))

    async def room_size_update(self, event):
        await self.send(text_data=json.dumps(event))
        
    async def player_joined_room(self, event):
        await self.send(text_data=json.dumps(event))

    async def player_left_room(self, event):
        await self.send(text_data=json.dumps(event))
    
    async def tournament_bracket(self, event):
        """Sends the list of matches to the client."""
        self.queue = LobbiesConsumer.room_queues[self.current_room]
        matches = event.get("matches")
        
        for match in matches:
            if match["player1"] == self.user.name or match["player2"] == self.user.name:
                match["type"] = T_TOURNAMENT_BRACKET
                await self.send(text_data=json.dumps(match))
                break
        self.in_game = True

    async def tournament_end(self, event):
        """Sends the winner of the tournament to the client."""
        self.queue = None
        await self.send(text_data=json.dumps(event))

    async def free_win(self, event):
        """Sends the winner of the tournament to the client."""
        await self.send(text_data=json.dumps(event))

    async def match_result(self, event):
        """
        Triggered by GameConsumer
        Puts match result from  game consumer into 
        shared queue for tournament task
        """
        
        await self.queue.put(event)
        self.in_game = False

    async def display_match_result(self, event):
        await self.send(text_data=json.dumps(event))

    ## Messages to client but not triggered like events ##
    async def send_success(self, room_name: str):
        await self.send(text_data=json.dumps({
            "type": T_SUCCESS,
            "room_name": room_name
        }))
        

    async def send_error(self, error: Enum):
        await self.send(text_data=json.dumps({
            "type": T_ERROR,
            "error": error.value,
        }))


    # Helper----------------------------------------------------------------
    async def add_player_to_room(self, room_name, available_rooms):
        room = TournamentRoom.from_dict(available_rooms[room_name])
        
        if room.is_full():
            await self.send_error(Errors.ROOM_FULL) # NOTE: could happen with many clients if 2 want to join as the last person i guess
            return
        try:
            room.add_player(self.user)
            self.current_room = room.name
        except AlreadyInRoom as e:
            await self.send_error(Errors.ALREADY_IN_ROOM)
            return
        
        # CHANNELS: Add user to the room group
        await self.group_send_Room(T_PLAYER_JOINED_ROOM, room) # NOTE: send all in group the msg before adding the user to group
        await self.group_switch(AVA_ROOMS, get_room_group(room.name))
        await self.send_success(room.name)
        
        if room.is_full():
            del_room_from_cache(room.name, AVA_ROOMS, available_rooms)
            update_or_add_room_to_cache(room.to_dict(), FULL_ROOMS)
            await self.group_send_AvailableTournaments(T_DELETE_ROOM, room)
            self.start_tournament(room)
        else:
            update_or_add_room_to_cache(room.to_dict(), AVA_ROOMS, available_rooms)
            await self.group_send_AvailableTournaments(T_ROOM_SIZE_UPDATE, room)
        return room

    def start_tournament(self, room: TournamentRoom):
        LobbiesConsumer.room_queues[room.name] = asyncio.Queue()
        task = asyncio.create_task(tournament_loop(room, LobbiesConsumer.room_queues[room.name]))
        task.add_done_callback(lambda t: self.cleanup_tournament_task(room.name))

    def cleanup_tournament_task(self, room_name):
        queue = LobbiesConsumer.room_queues.pop(room_name, None)
        

    async def group_remove(self, group_name: str):
        """
        Remove the channel from the specified channel group.
        """
        await self.channel_layer.group_discard(group_name, self.channel_name)

    async def group_add(self, group_name: str):
        """
        Add the channel to the specified channel group.
        """
        await self.channel_layer.group_add(group_name, self.channel_name)

    async def group_switch(self, switch_from, switch_to):
        """
        Switch the channel from one group to another.
        """
        await self.group_remove(switch_from)
        await self.group_add(switch_to)
