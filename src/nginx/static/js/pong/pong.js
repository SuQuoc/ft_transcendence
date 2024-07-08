// Basic Pong game with remote players
// create the game with gameArea.js class

// if daphne is separate how to connect?
//window.location.host
roomName = "1"
let ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
let ws_path = ws_scheme + '://' + window.location.host + "/daphne/pong/" + roomName + "/";
let chatSocket = new WebSocket(ws_path);

function startPong() 
{
    game_area = new GameArea();
    
    let player1 = new Player(id=0, y=300, x=0, width=20, height=100, "Lenox");
    let player2 = new Player(id=0, y=300, x=100, width=20, height=100, "Eule");
    let ball = new Player(id="ball", y=0, x=0, width=20, height=20, "Ball");

    chatSocket.onmessage = function(e)
    {
        update_game_data(player1, player2, ball, e);
    };

    game_area.start(player1, player2, ball);
    let keys_handler = new key_event_handler(player1, player2);
    keys_handler.key_event();
    // if i recv message
}

function update_game_data(player1, player2, ball, e)
{
    const data = JSON.parse(e.data)
    if (data.type === "playerId")
    {
        player1.id = data.playerId;
        return ;
    }
    ball.y = data.ball_y;
    ball.x = data.ball_x;
    if(data.playerId === player1.id)
    {
        player1.y = data.y;
        player1.x = data.x;
        return ;
    }
    player2.y = data.y;
    player2.x = data.x;
}

//clear the frame and update it
//gets called all x times from the game_area class
function updateGameArea(game_data)
{
    game_data.clear();
    game_data.player1.update(game_data);
    game_data.player2.update(game_data);
    game_data.ball.update(game_data);
    //console.log(game_data.player1);
    //a.player.;
}

/* chatSocket.onopen = function(e)
{
    console.log("connected");
} */
/* chatSocket.send(JSON.stringify({
    'message': message
})); */
