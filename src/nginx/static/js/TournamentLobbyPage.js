import { ComponentBaseClass } from "./componentBaseClass.js";

import { TournamentLobbyPlayerElement } from "./TournamentLobbyPlayerElement.js";

export class TournamentLobbyPage extends ComponentBaseClass {
	constructor() {
		super();
		// Binds the method to this class instance so it can be used in the event listener
		this.handleRecievedMessageVar = this.handleRecievedMessage.bind(this);
	}
	connectedCallback() {
		super.connectedCallback();

		// getting elements (can't do this in constructor because the shadow DOM isn't created yet)
		this.player_list = this.root.getElementById("lobbyPlayerList");
		this.leave_button = this.root.getElementById("lobbyLeaveButton");

		// adding event listeners
		this.leave_button.addEventListener("click", this.handleLeaveLobby);
		window.app.socket.addEventListener("message", this.handleRecievedMessageVar);

		// gets the player list when the page is loaded
		window.app.socket.send(JSON.stringify({type: "getUpdateLobbyPlayerList"}));
	}

	disconnectedCallback() {
		super.disconnectedCallback();

		// removing event listeners
		this.leave_button.removeEventListener("click", this.handleLeaveLobby);
		window.app.socket.removeEventListener("message", this.handleRecievedMessageVar);
	}


	/// ----- Methods ----- ///

	addPlayerElement(player_name) {
		let element = new TournamentLobbyPlayerElement();

		this.player_list.appendChild(element);
		element.querySelector("[name='lobby_player_name']").innerText = player_name;
	}


	/// ----- Event Handlers ----- ///

	// TODO: arrow keys!!!!??
	handleLeaveLobby(event) {
		window.app.socket.send(JSON.stringify({type: "leaveTournament"}));
		window.app.router.go("/tournament");
	}

	/** gets called when the websocket receives a message */
	handleRecievedMessage(event) {
		const data = JSON.parse(event.data);
		
		console.log("data: ", data);
		
		this.root.getElementById("lobbyPlayerList").innerHTML = "";
		if (data.type === "updateLobbyPlayerList") {
			for (let key in data) {
				if (data[key].player_name)
					this.addPlayerElement(data[key].player_name);
			}
		}
	}

	getElementHTML() {
		const template = document.getElementById("tournamentLobbyPageTemplate")
		/* const template = document.createElement('template');
		template.innerHTML = `
			<scripts-and-styles></scripts-and-styles>
			<h1>Tournament Lobby<h1>
		`; */
		return template;
	}
}

customElements.define('tournament-lobby-page', TournamentLobbyPage);