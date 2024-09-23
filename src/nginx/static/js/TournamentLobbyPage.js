import { ComponentBaseClass } from "./componentBaseClass.js";
import { TournamentLobbyPlayerElement } from "./TournamentLobbyPlayerElement.js";
import { PongCanvasElement } from "./fiona_pong/PongCanvasElement.js";

export class TournamentLobbyPage extends ComponentBaseClass {
	constructor() {
		super();
		// Binds the method to this class instance so it can be used in the event listener
		this.handleRecievedMessage_var = this.handleRecievedMessage.bind(this);
		this.handlePongFullScreen_var = this.handlePongFullScreen.bind(this);
	}
	connectedCallback() {
		super.connectedCallback();

		// adding classes
		this.classList.add("d-flex", "flex-lg-row", "flex-column-reverse", "w-100", "h-100");

		// getting elements (can't do this in constructor because the shadow DOM isn't created yet)
		this.navbar = document.getElementById('navbar');
		this.footer = document.getElementById('footer');
		this.canvas = this.root.querySelector("pong-canvas-element");
		this.player_sidebar = this.root.getElementById("lobbyPlayerSidebar");
		this.player_list = this.root.getElementById("lobbyPlayerList");
		this.leave_button = this.root.getElementById("lobbyLeaveButton");

		// adding event listeners
		this.canvas.addEventListener("dblclick", this.handlePongFullScreen_var);
		this.leave_button.addEventListener("click", this.handleLeaveLobby);
		window.app.socket.addEventListener("message", this.handleRecievedMessage_var);

		// gets the player list when the page is loaded
		window.app.socket.send(JSON.stringify({type: "getUpdateLobbyPlayerList"}));
	}

	disconnectedCallback() {
		super.disconnectedCallback();

		// removing event listeners
		this.canvas.removeEventListener("dblclick", this.handlePongFullScreen_var); // maybe we need an extra event for touchscreens !!!!!???
		this.leave_button.removeEventListener("click", this.handleLeaveLobby);
		window.app.socket.removeEventListener("message", this.handleRecievedMessage_var);
	}


	/// ----- Methods ----- ///

	addPlayerElement(player_name) {
		let element = new TournamentLobbyPlayerElement();

		this.player_list.appendChild(element);
		element.querySelector("[name='lobby_player_name']").innerText = player_name;

		//TODO: change avatar
	}


	/// ----- Event Handlers ----- ///

	handleLeaveLobby(event) {
		window.app.socket.send(JSON.stringify({type: "leaveTournament"}));
		window.app.router.go("/tournament", false); // isn't added to the history
	}

	/** gets called when the websocket receives a message */
	handleRecievedMessage(event) {
		const data = JSON.parse(event.data);
		
		console.log("received message in tournament-lobby-page: ", data);
		
		this.root.getElementById("lobbyPlayerList").innerHTML = "";
		if (data.type === "updateLobbyPlayerList") {
			for (let key in data) {
				if (data[key].player_name)
					this.addPlayerElement(data[key].player_name);
			}
		}
	}

	handlePongFullScreen() {
		if (this.navbar.style.display === "none") {
			this.navbar.style.display = "";
			this.footer.style.display = "";
			this.player_sidebar.style.display = "";
			this.player_sidebar.classList.add('d-flex');
		} else {
			this.navbar.style.display = "none";
			this.footer.style.display = "none";
			this.player_sidebar.style.display = "none";
			this.player_sidebar.classList.remove('d-flex'); // if this class isn't removed, the display: none; is overwritten as flex
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
			<pong-canvas-element class="d-flex flex-grow-1 w-100 h-100 p-lg-4 p-md-3"></pong-canvas-element>
		`;
		return template;
	}
}

customElements.define('tournament-lobby-page', TournamentLobbyPage);