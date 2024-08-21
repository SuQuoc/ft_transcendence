from channels.layers import get_channel_layer
from .storageClasses import SlotXy
from .ball import GameBall
from .pongPlayer import PongPlayer
import asyncio

map_size = SlotXy(800, 600)
ball_width = 10
ball_height = 10
MOVE_SPEED = 10

# Here we create a match were the players can play pong
# Start the game and manage the players
class Match:

    def __init__(self, player1=None, player2=None, task=None, name=None) -> None:
        self.player1: PongPlayer = player1
        self.player2: PongPlayer = player2
        self.task = task
        self.name = name
        self.lock = asyncio.Lock()
        self.len = 0

    #  This is where we add the player to the match
    async def addPlayer(self, player, channel_name):
        if self.len == 2:
            return False
        if self.player1 is None:
            self.player1 = player
            channel_layer = get_channel_layer()
            # This is where we add the player to the group to send msgs to them
            await channel_layer.group_add(self.name, channel_name)
            self.len += 1
            return True
        if self.player2 is None:
            self.player2 = player
            channel_layer = get_channel_layer()
            # This is where we add the player to the group to send msgs to them
            await channel_layer.group_add(self.name, channel_name)
            self.len += 1
            return True
        return False

    # This is where we remove the player from the match
    # Also remove the player from the match chat group
    async def removePlayer(self, player, channel_name):
        if self.player1 == player:
            self.player1 = None
            self.len -= 1
            channel_layer = get_channel_layer()
            # This is where we remove the player from the group
            await channel_layer.group_discard(self.name, channel_name)
            return True
        if self.player2 == player:
            self.player2 = None
            self.len -= 1
            channel_layer = get_channel_layer()
            # This is where we remove the player from the group
            await channel_layer.group_discard(self.name, channel_name)
            return True
        return False

    async def findOpponent(self, players:dict) -> None:
        for player in players.values():
            player: PongPlayer
            if player.id != self.player1.id:
                print("Opponent found", player.channel_name)
                return await self.addPlayer(player, player.channel_name)
        print("No opponent found")
        return False

    async def startGame(self):
        self.task = asyncio.create_task(self.gameLoop())

    async def gameLoop(self):
        print("game loop started")
        ball = GameBall(x=(map_size.x / 2), y=(map_size.y / 2), map_size=map_size, width=ball_width, height=ball_height)
        while self.len == 2:
            ball.hitWall()
            ball.move()
            async with self.lock:
                await self.sendToClient(self.player1, ball)
                await self.sendToClient(self.player2, ball)
                # [await self.sendToClient(player, ball) for player in self.players[self.room_name].values()]
            await asyncio.sleep(0.05)

    async def sendToClient(self, player: PongPlayer, ball: GameBall):
        channel_layer = get_channel_layer()
        player.move(MOVE_SPEED)
        ball.paddlesHit(player)
        # Send to clients in django and then to JS
        await channel_layer.group_send(
            self.name,
            {
                "type": "chat.message",  # Massage type so js knows what he has to do with this strings
                "y": player.y,  # This will tell js where to draw the player
                "x": player.x,
                "playerId": player.id,  # Will tell js if it is the active player
                "ball_x": ball.x,  # This will tell js where to draw the ball
                "ball_y": ball.y,
                "match_points_left": ball.match_points["left"],
                "match_points_right": ball.match_points["right"],
            },
        )
