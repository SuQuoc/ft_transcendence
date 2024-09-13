import { GameArea } from './gameArea.js';
import { Player } from './player.js';
import { key_event_handler } from './keyEvents.js';

// Basic Pong game with remote players
// create the game with gameArea.js class

// if daphne is separate how to connect?
//window.location.host

export function startPong(chatSocket) {
	/* var room_name = document.getElementById("room-name").value;
    var room_size = document.getElementById("room-size").value; */

	/* let ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
    let ws_path = ws_scheme + '://' + window.location.host + "/daphne/pong/" + room_name + "/";
    let chatSocket = new WebSocket(ws_path); */

	//sendRoomSizeMessage(chatSocket, room_size);

	var refresh_rate = 10; // set refresh rate of the game
	var width = 800; // set size of the game area
	var height = 600;

	let game_area = new GameArea(width, height, refresh_rate);

	let player1 = new Player(0, 300, 0, 20, 100, 'Lenox');
	let player2 = new Player(0, 300, 100, 20, 100, 'Eule');
	let ball = new Player('ball', 0, 0, 10, 10, 'Ball');

	console.log('startPong');

	chatSocket.onmessage = function (e) {
		const data = JSON.parse(e.data);
		update_game_data(chatSocket, game_area, player1, player2, ball, data);
	};

	game_area.start(player1, player2, ball);
	let keys_handler = new key_event_handler(player1, player2, chatSocket);
	keys_handler.key_event();

	/* game_area.start(player1, player2, ball);
    let keys_handler = new key_event_handler(player1, player2, chatSocket);
    keys_handler.key_event(); */
	// if i recv message
}

function update_game_data(chatSocket, game_area, player1, player2, ball, data) {
	console.log(data);
	if (data.type === 'playerId') {
		player1.id = data.player1;
		player2.id = data.player2;
		return;
	}

	if (data.type === 'update') {
		ball.update_game_count(data.match_points_left, data.match_points_right); // update the match points here and create the vars

		ball.y = data.ball_y;
		ball.x = data.ball_x;
		if (data.playerId === player1.id) {
			player1.y = data.y;
			player1.x = data.x;
			return;
		}
		player2.y = data.y;
		player2.x = data.x;
		return;
	}

	/* if(data.type === "startGame" && data.startGame === true)
    {
        game_area.start(player1, player2, ball);
        let keys_handler = new key_event_handler(player1, player2, chatSocket);
        keys_handler.key_event();
    } */
}

//clear the frame and update it
//gets called all x times from the game_area class
export function updateGameArea(game_data) {
	game_data.clear();
	game_data.draw_middle_line('black', 6, 30, 1.5);
	game_data.player1.update(game_data, 'black');
	game_data.player2.update(game_data, 'black');
	game_data.ball.update(game_data, 'black');
	game_data.draw_counter();
	//console.log(game_data.player1);
	//a.player.;
}
