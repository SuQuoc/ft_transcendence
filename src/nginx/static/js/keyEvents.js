// handling key event here
// function gets called from event listener in pong.js
// write class or function both would work!

class key_event_handler
{
    constructor(player1, player2)
    {
        this.player1 = player1;
        this.player2 = player2;
        this.up = false; // move it into player
        this.down = false; // move it into player
    }

    // Here the Event Listener catches the key inputs
    // Calls the key Down function that will send data to backend
    key_event()
    {
        let player1 = this.player1;
        var down = this.down;
        var up = this.up;

        document.addEventListener("keydown", key_down)
        function key_down(e)
        {
            if(e.key === "w")
            {
                up = true;
                down = false;
            }
            if(e.key === "s")
            {
                up = false;
                down = true;
            }
            chatSocket.send(JSON.stringify({
                "playerId": player1.id, "up": up, "down": down,
            }));
            console.log(player1.id)
        }
        document.addEventListener("keyup", key_up)
        function key_up(e)
        {
            if(e.key === "w")
                up = false;
            if(e.key === "s")
                down = false;
            chatSocket.send(JSON.stringify({
                "playerId": player1.id, "up": up, "down": down,
            }));

        }
    }

    keyDown(e)
    {
        //var up = 1;
        console.log(this.up)
        if(e.code === "w")
        {
            this.up = "1";
            this.down = "0";
        }
        if(e.code === "s")
        {
            this.up = "0";
            this.down = "1";
        }
        chatSocket.send(JSON.stringify({
            "up": this.player1
        }));
        console.log(this.player1, e)
        //send from here to backend
        //send every tick/refresh?
        //we are fucked xD
    }
}
