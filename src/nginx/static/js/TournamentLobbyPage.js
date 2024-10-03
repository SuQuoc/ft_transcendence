import { ComponentBaseClass } from "./componentBaseClass.js";
import { TournamentLobbyPlayerElement } from "./TournamentLobbyPlayerElement.js";
import { PongCanvasElement } from "./fiona_pong/PongCanvasElement.js";

export class TournamentLobbyPage extends ComponentBaseClass {
	constructor(tournament_name) {
		super();

		this.tournament_name = tournament_name;

		// Binds the method to this class instance so it can be used in the event listener
		this.handleReceivedMessage_var = this.handleReceivedMessage.bind(this);
		this.handlePongFullScreen_var = this.handlePongFullScreen.bind(this);
	}
	connectedCallback() {
		super.connectedCallback();

		// adding classes
		this.classList.add("d-flex", "flex-lg-row", "flex-column-reverse", "w-100", "h-100");

		// getting elements (can't do this in constructor because the shadow DOM isn't created yet)
		this.canvas = this.root.querySelector("pong-canvas-element");
		this.player_list = this.root.getElementById("lobbyPlayerList");
		this.leave_button = this.root.getElementById("lobbyLeaveButton");
		this.current_player_num = this.root.getElementById("lobbyCurrentPlayerNum");

		// adding event listeners
		this.canvas.addEventListener("dblclick", this.handlePongFullScreen_var);
		this.leave_button.addEventListener("click", this.handleLeaveLobby);
		window.app.socket.addEventListener("message", this.handleReceivedMessage_var);

		// sending a request to the server to join the tournament
		window.app.socket.send(JSON.stringify({type: "join_tournament", room_name: this.tournament_name}));
	}

	disconnectedCallback() {
		super.disconnectedCallback();

		// removing event listeners
		this.canvas.removeEventListener("dblclick", this.handlePongFullScreen_var);
		this.leave_button.removeEventListener("click", this.handleLeaveLobby);
		window.app.socket.removeEventListener("message", this.handleReceivedMessage_var);
	}


	/// ----- Methods ----- ///

	initLobby(points_to_win, max_player_num) {
		this.root.getElementById("lobbyTournamentName").innerText = this.tournament_name;
		this.root.getElementById("lobbyPointsToWin").innerText = points_to_win;
		this.root.getElementById("lobbyMaxPlayerNum").innerText = max_player_num;

	}

	addPlayerElement(player_name) { // needs the avatar too !!!
		let element = new TournamentLobbyPlayerElement();

		element.setAttribute('name', player_name);
		this.player_list.appendChild(element);
		element.querySelector("[name='lobby_player_name']").innerText = player_name;

		//TODO: change avatar
	}

	deletePlayerElement(player_name) {
		let element = this.player_list.querySelector(`tournament-lobby-player-element[name="${player_name}"]`);
		if (!element) {
			console.error("Error: deletePlayerElement: element to delete not found");
			return;
		}

		this.join_tournament_elements.removeChild(element);
		//this.noTournamentsToJoin();
	}

	updateCurrentPlayerNum(new_player_num) {
		this.current_player_num.innerText = new_player_num;
	}


	/// ----- Event Handlers ----- ///

	/** gets called when the websocket receives a message */
	handleReceivedMessage(event) {
		const data = JSON.parse(event.data);
		
		console.log("received message on tournament-lobby-page: ", data);
		
		if (data.type === "new_player") {
			this.addPlayerElement(data.displayname); // needs the avatar too !!!
		}
		else if (data.type === "player_left") {
			this.deletePlayerElement(data.displayname);
		}
		else if (data.type === "update_current_player_num") {
			this.current_player_num.innerText = data.current_player_num;
		}
		else if (data.type === "updateLobbyPlayerList") {
			for (let key in data) {
				if (data[key].player_name)
					this.addPlayerElement(data[key].player_name);
			}
		}
	}

	handleLeaveLobby(event) {
		window.app.socket.send(JSON.stringify({type: "leave_tournament"}));
		window.app.router.go("/tournament", false); // isn't added to the history
	}

	handlePongFullScreen() {
		if (this.canvas.requestFullscreen) {
			this.canvas.requestFullscreen();
		} else if (this.canvas.mozRequestFullScreen) { // Firefox
			this.canvas.mozRequestFullScreen();
		} else if (this.canvas.webkitRequestFullscreen) { // Chrome, Safari and Opera
			this.canvas.webkitRequestFullscreen();
		} else if (this.canvas.msRequestFullscreen) { // IE/Edge
			this.canvas.msRequestFullscreen();
		}

		this.canvas.handleCanvasResize();
		this.canvas.handleBackgroundCanvasResize();
	}


	getElementHTML() {
		const template = document.createElement('template');
		template.innerHTML = `
			<scripts-and-styles></scripts-and-styles>
			
			<!-- lobby player sidebar -->
			<div class="d-flex flex-lg-column flex-row
						justify-content-between
						lobby-player-sidebar-lg
						overflow-auto
						bg-dark shadow text-white
						h-lg-100 p-2 gap-lg-0 gap-5"
				id="lobbyPlayerSidebar"
			>
				<!-- tournament name -->
				<p id="lobbyTournamentName" class="text-break text-wrap mb-1">TournabmentNamjkkkkkkkkkkkke</p>
				<hr class="mt-0 mb-3"></hr>

				<!-- points to win -->
				<div class="d-flex flex-row align-items-center w-lg-100 order-lg-1">
					<span class="d-lg-block d-none fs-4">PTW:</span>
					<div class="d-flex ms-lg-auto">
						<span id="lobbyPointsToWin" class="fs-4">0</span>
					</div>
				</div>

				<!-- leave button -->
				<hr class="d-lg-block d-none mt-auto mb-2 order-lg-3"></hr>
				<button id="lobbyLeaveButton" class="btn btn-custom px-4 order-lg-3"><Label>leave</Label></button>

				<!-- number of players -->
				<div class="d-flex flex-row align-items-center w-lg-100 order-lg-1">
					<span class="d-lg-block d-none fs-4">Players:</span>
					<div class="d-flex ms-lg-auto">
						<span id="lobbyCurrentPlayerNum" class="fs-4">1</span>
						<span class="fs-4">/</span>
						<span id="lobbyMaxPlayerNum" class="fs-4">4</span>
					</div>
				</div>

				<!-- player list -->
				<hr class="d-lg-block d-none mt-2 mb-3 order-lg-2"></hr>
				<div id="lobbyPlayerList"
					class="d-flex flex-lg-column flex-row
							align-self-lg-start align-self-center
							gap-3 row-gap-2
							order-lg-2"
				>
					<!-- tournament-lobby-player-elements: -->
					
				</div>

			</div>
			<!-- game -->
			<pong-canvas-element class="d-flex flex-grow-1 bg-custom w-100 h-100 p-lg-4 p-md-3 p-1"></pong-canvas-element>
		`;
		return template;
	}
}

customElements.define('tournament-lobby-page', TournamentLobbyPage);