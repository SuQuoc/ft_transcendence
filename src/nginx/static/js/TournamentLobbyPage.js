import { ComponentBaseClass } from "./componentBaseClass.js";
import { TournamentLobbyPlayerElement } from "./TournamentLobbyPlayerElement.js";
import { PongCanvasElement } from "./pong/PongCanvasElement.js";

export class TournamentLobbyPage extends ComponentBaseClass {
	constructor(tournament_name) {
		super();

		this.tournament_name = tournament_name;
		this.timeout_id = -1;

		// Binds the method to this class instance so it can be used in the event listener
		this.handleReceivedMessage_var = this.handleReceivedMessage.bind(this);

		// adding this here to avoid having a gap where the match bracket message can't be recieved
		window.app.socket.addEventListener("message", this.handleReceivedMessage_var);
	}
	
	connectedCallback() {
		super.connectedCallback();

		// adding classes
		this.classList.add("d-flex", "flex-row", "w-100", "h-100");

		// getting elements
		this.canvas = this.root.querySelector("pong-canvas-element");
		this.player_list = this.root.getElementById("lobbyPlayerList");
		this.leave_button = this.root.getElementById("lobbyLeaveButton");
		this.current_player_num = this.root.getElementById("lobbyCurrentPlayerNum");

		// adding event listeners
		this.leave_button.addEventListener("click", this.handleLeaveLobby);

		// sending a request to the server to get the room info
		window.app.socket.send(JSON.stringify({type: "get_room_info", room_name: this.tournament_name}));

		// work through events that are in the socket_event_queue
		this.workThoughEventQueue();
	}

	disconnectedCallback() {
		super.disconnectedCallback();

		if (this.timeout_id > 0)
			clearTimeout(this.timeout_id);

		// removing event listeners
		this.leave_button.removeEventListener("click", this.handleLeaveLobby);
		window.app.socket.removeEventListener("message", this.handleReceivedMessage_var);
	}


	/// ----- Methods ----- ///

	workThoughEventQueue() {
		let event;
		while ((event = window.app.socket_event_queue.get()) !== null)
			this.handleReceivedMessage(event);
	}

	sendMatchId(match_id) {
		if (!window.app.pong_socket) {
			console.error("pong socket is not open");
			window.app.router.go("/"); // goes to the home page !!??
		}

		if (window.app.pong_socket.readyState === WebSocket.OPEN) {
			window.app.pong_socket.send(JSON.stringify({"type": "connect_to_match", "match_id": match_id}));
			console.log('pong websocket is open');
		} else {
			window.app.pong_socket.addEventListener('open', () => {
				window.app.pong_socket.send(JSON.stringify({"type": "connect_to_match", "match_id": match_id}));
			}, { once: true });
			console.log('pong websocket adding event listener on open')
		}
	}

	initLobby(data) {
		this.root.getElementById("lobbyTournamentName").innerText = this.tournament_name;
		this.root.getElementById("lobbyPointsToWin").innerText = data.points_to_win;
		this.root.getElementById("lobbyMaxPlayerNum").innerText = data.max_player_num;
		this.current_player_num.innerText = data.cur_player_num;

		for (let i in data.players) {
			this.addPlayerElement(data.players[i]);
		}
	}

	displayMatchResult(winner, loser) {
		let winner_element = this.player_list.querySelector(`tournament-lobby-player-element[name="${winner}"]`);
		let loser_element = this.player_list.querySelector(`tournament-lobby-player-element[name="${loser}"]`);
		if (winner_element) {
			winner_element.incrementWins();	
		} else {console.error("Error: displayMatchResult: winner element not found");}
		if (loser_element) {
			loser_element.greyOutPlayer();
		} else {console.error("Error: displayMatchResult: loser element not found");}
	}

	addPlayerElement(player_name) { // needs the avatar too !!!
		let element = new TournamentLobbyPlayerElement();

		element.setAttribute('name', player_name);
		this.player_list.appendChild(element);
		element.querySelector("[name='lobby_player_name']").innerText = player_name;
		if (player_name === window.app.userData.username)
			element.makeNameBold();
		//TODO: change avatar
	}

	deletePlayerElement(player_name) {
		let element = this.player_list.querySelector(`tournament-lobby-player-element[name="${player_name}"]`);
		if (!element) {
			console.error("Error: deletePlayerElement: element to delete not found");
			return;
		}
		
		this.player_list.removeChild(element);
	}

	updateCurrentPlayerNum(new_player_num) {
		this.current_player_num.innerText = new_player_num;
	}

	setGoBackTimeout() {
		this.timeout_id = setTimeout(() => {
			this.timeout_id = -1;
			this.handleLeaveLobby();
		}, 30000);
	}


	/// ----- Event Handlers ----- ///

	handleLeaveLobby() {
		window.app.socket.send(JSON.stringify({type: "leave_room"}));
		window.app.router.go("/tournament", false); // isn't added to the history
	}

	/** gets called when the websocket receives a message */
	handleReceivedMessage(event) {
		const data = JSON.parse(event.data);
		console.log("TournamentLobbyPage: handleReceivedMessage: ", data);
				
		if (data.type === "player_joined_room") {
			this.addPlayerElement(data.displayname); // needs the avatar too !!!
			this.current_player_num.innerText = data.cur_player_num;
		}
		else if (data.type === "player_left_room") {
			this.deletePlayerElement(data.displayname);
			this.current_player_num.innerText = data.cur_player_num;
		}
		else if (data.type === "room_info") {
			this.initLobby(data.room);
		}
		else if (data.type === "tournament_bracket") {
			let match_id = null;

			for (let match of data.matches) {
				if (match.player1 === window.app.userData.username) {
					match_id = match.match_id;
					break;
				}
				else if (match.player2 === window.app.userData.username) {
					match_id = match.match_id;
					break;
				}
			}
			if (match_id)
				this.sendMatchId(match_id);
		}
		else if (data.type === "display_match_result") {
			this.displayMatchResult(data.match_result.winner, data.match_result.loser);
		}
		else if (data.type === "tournament_end") {
			console.log("tournament end");
			this.canvas.clearTextForeground();
			this.canvas.writeTextForeground(data.winner + " won!");
			this.setGoBackTimeout();
		}
		else if (data.type === "error") {
			console.error("Error: handleReceivedMessage: ", data.error);
		}
		else {
			console.error("Error: handleReceivedMessage: unknown type: ", data.type);
		}
	}


	getElementHTML() {
		const template = document.createElement('template');
		template.innerHTML = `
			<scripts-and-styles></scripts-and-styles>

			<!-- lobby player sidebar -->
			<div class="d-flex flex-column
						justify-content-between
						lobby-player-sidebar
						bg-dark shadow text-white
						h-100 p-2 gap-0"
				id="lobbyPlayerSidebar"
			>
				<!-- tournament name -->
				<p id="lobbyTournamentName" class="text-break text-wrap mb-1">tournament name</p>
				<hr class="mt-0 mb-0"></hr>

				<!-- points to win -->
				<div class="d-flex flex-row align-items-center w-100 mb-2">
					<span class="fs-5">Points to win:</span>
					<div class="d-flex ms-auto">
						<span id="lobbyPointsToWin" class="fs-5">0</span>
					</div>
				</div>

				<!-- number of players -->
				<div class="d-flex flex-row align-items-center w-100">
					<span class="fs-5">Players:</span>
					<div class="d-flex ms-auto">
						<span id="lobbyCurrentPlayerNum" class="fs-5">1</span>
						<span class="fs-5">/</span>
						<span id="lobbyMaxPlayerNum" class="fs-5">4</span>
					</div>
				</div>

				<!-- player list -->
				<hr class="mt-1 mb-3"></hr>
				<div id="lobbyPlayerList"
					class="d-flex flex-column
							align-self-start
							overflow-auto
							w-100 h-100 gap-3 row-gap-2
						"
				>
					<!-- tournament-lobby-player-elements: -->
					
				</div>

				<!-- leave button -->
				<hr class="mt-auto mb-2"></hr>
				<button id="lobbyLeaveButton" class="btn btn-custom px-4"><Label>leave</Label></button>

			</div>
			<!-- game -->
			<pong-canvas-element class="d-flex flex-grow-1 bg-custom w-100 h-100 p-lg-4 p-md-3 p-1"></pong-canvas-element>
		`;
		return template;
	}
}

customElements.define('tournament-lobby-page', TournamentLobbyPage);