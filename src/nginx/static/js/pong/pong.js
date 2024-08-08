// Basic Pong game with remote players
// create the game with gameArea.js class

// if daphne is separate how to connect?
//window.location.host

function startPong()
{
    var roomName = document.getElementById("room").value;
    let ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
    let ws_path = ws_scheme + '://' + window.location.host + "/daphne/pong/" + roomName + "/";
    let chatSocket = new WebSocket(ws_path);

    var refresh_rate = 10;   // set refresh rate of the game
    var width = 800;         // set size of the game area
    var height = 600;

    let game_area = new GameArea(width, height, refresh_rate);

    let player1 = new Player(id=0, y=300, x=0, width=20, height=100, "Lenox");
    let player2 = new Player(id=0, y=300, x=100, width=20, height=100, "Eule");
    let ball = new Player(id="ball", y=0, x=0, width=10, height=10, "Ball");

    chatSocket.onmessage = (e) => {
        update_game_data(player1, player2, ball, e);
    };

    game_area.start(player1, player2, ball);
    let keys_handler = new key_event_handler(player1, player2, chatSocket);
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

    ball.update_game_count(data.match_points_left,
        data.match_points_right
    ) // update the match points here and create the vars

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
    game_data.draw_middle_line("black", 6, 30, 1.5);
    game_data.player1.update(game_data, "black");
    game_data.player2.update(game_data, "black");
    game_data.ball.update(game_data, "black");
    game_data.draw_counter();
    //console.log(game_data.player1);
    //a.player.;
}
