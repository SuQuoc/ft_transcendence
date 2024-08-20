from channels.layers import get_channel_layer

# Here we create a match were the players can play pong
# Start the game and manage the players
class Match:

    def __init__(self, player1=None, player2=None, task=None, name=None) -> None:
        self.player1 = player1
        self.player2 = player2
        self.task = task
        self.name = name
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
            if player.id != self.player1.id:
                print("Opponent found", player.channel_name)
                return await self.addPlayer(player, player.channel_name)
        print("No opponent found")
        return False
