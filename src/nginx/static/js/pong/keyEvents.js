// handling key event here
// function gets called from event listener in pong.js
// write class or function both would work!

function send_key_status(id, up_down)
{
    chatSocket.send(JSON.stringify({
        "playerId": id, "up": up_down[0], "down": up_down[1],
    }));
}

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
        let up_down = [this.up, this.down];

        document.addEventListener("keydown", key_down)
        function key_down(e)
        {
            if(e.key === "w")
                up_down = [true, false]
            if(e.key === "s")
                up_down = [false, true]
            send_key_status(player1.id, up_down);
        }

        document.addEventListener("keyup", key_up)
        function key_up(e)
        {
            if(e.key === "w")
                up_down[0] = false;
            if(e.key === "s")
                up_down[1] = false;
            send_key_status(player1.id, up_down);
        }
    }

}
