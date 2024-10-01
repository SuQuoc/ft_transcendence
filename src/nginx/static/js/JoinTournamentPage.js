import { ComponentBaseClass } from "./componentBaseClass.js";
import { JoinTournamentElement } from "./JoinTournamentElement.js";

export class JoinTournamentPage extends ComponentBaseClass {
	constructor() {
		super();
		
		// Binds the method to this class instance so it can be used in the event listener
		this.handleReceivedMessageVar = this.handleReceivedMessage.bind(this);
		this.handleRangeDisplayVar = this.handleRangeDisplay.bind(this);
		this.handleTournamentCreationVar = this.handleTournamentCreation.bind(this);
	};

	connectedCallback() {
		super.connectedCallback();

		// getting elements (can't do this in constructor because the shadow DOM isn't created yet)
		this.join_tournament_elements = this.root.getElementById("joinTournamentElements");
		this.create_tournament_form = this.root.getElementById("createTournamentForm");
		this.range_display = this.root.getElementById("createPointsToWinDisplay");
		this.display_lane = this.root.getElementById("createDisplayLane");
		this.input_range = this.root.getElementById("createPointsToWin");
		
		// making the "lane" the display div moves in the same width as the middle of the thumb from end to end of the range input (so the percentage is correct)
		this.thumb_width = 16; // it's also defined in template.css, so if you change it here, change it there as well
		this.display_lane.style.paddingLeft = `${this.thumb_width / 2}px`;
		this.display_lane.style.paddingRight = `${this.thumb_width / 2}px`;

		// adding event listeners
		if (window.app.socket)
			window.app.socket.addEventListener("message", this.handleReceivedMessageVar);
		this.create_tournament_form.addEventListener("submit", this.handleTournamentCreationVar);
		this.input_range.addEventListener("input", this.handleRangeDisplayVar);
		
		// calling the method to set the initial position of the display
		this.handleRangeDisplay({target: this.input_range});

		// getting the list of tournaments
		/* if (!window.app.socket)
			console.error("socket is not open");
		window.app.socket.send(JSON.stringify({"type": "get_tournament_list"})); */
		this.getTournamentList();
	};

	disconnectedCallback() {
		super.disconnectedCallback();
		
		// removing event listeners
		if (window.app.socket)
			window.app.socket.removeEventListener("message", this.handleReceivedMessageVar);
		this.create_tournament_form.removeEventListener("submit", this.handleTournamentCreationVar);
		this.input_range.removeEventListener("input", this.handleRangeDisplayVar);
	};
	

	/// ----- Methods ----- ///
	
	/** creates a new joinTournamentElement and appends it to the joinTournamentElements div */
	createJoinTournamentElement(tournament_name, creator_name, points_to_win, current_player_num, max_player_num) {
		let element = new JoinTournamentElement();

		element.setAttribute('name', tournament_name);
		this.join_tournament_elements.appendChild(element);

		element.querySelector("[name='join_name']").innerHTML = tournament_name;
		element.querySelector("[name='join_creator']").innerHTML = creator_name;
		element.querySelector("[name='join_points_to_win']").innerHTML = points_to_win;
		element.querySelector("[name='join_current_player_num']").innerHTML = current_player_num;
		element.querySelector("[name='join_max_player_num']").innerHTML = max_player_num;
		
		//this.noTournamentsToJoin();
	};

	/** deletes a joinTournamentElement */
	deleteJoinTournamentElement(tournament_name) {
		let element = this.join_tournament_elements.querySelector(`join-tournament-element[name="${tournament_name}"]`);
		console.log('delete join tournament element: ', element);
		
		this.join_tournament_elements.removeChild(element);
		//this.noTournamentsToJoin();
	};
	
	/** hides or shows a text that says "no tournaments to join" */
	noTournamentsToJoin() { // not working!!!!! TODO: fix this
		const tournament_elements = this.root.querySelectorAll("join-tournament-element");
		console.log("tournament_elements: ", tournament_elements);

		if (tournament_elements === null || tournament_elements.length === 0) {
			this.root.getElementById("noTournamentsToJoin").style.display = "";
		}
		else {
			this.root.getElementById("noTournamentsToJoin").style.display = "none";
		}
	};
	
	getTournamentList() {
		if (!window.app.socket) {
			console.error("socket is not open");
			window.app.router.go("/"); // goes to the home page
		}

		if (window.app.socket.readyState === WebSocket.OPEN) {
			window.app.socket.send(JSON.stringify({"type": "get_tournament_list"}));
			console.log('websocket is open');
		} else {
			window.app.socket.addEventListener('open', () => {
				window.app.socket.send(JSON.stringify({"type": "get_tournament_list"}));
			}, { once: true });
			console.log('websocket adding event listener on open')
		}
	}
	

	/// ----- Event Handlers ----- ///

	/** gets called when the websocket receives a message */
	handleReceivedMessage(event) {
		const data = JSON.parse(event.data);
		
		console.log("handleReceivedMessage: data: ", data);
		
		if (data.type === "get_tournament_list") {
			console.log("get_tournament_list");
			for (let tournament_name in data.lobbies) {
				const tournament = data.lobbies[tournament_name];
				this.createJoinTournamentElement(tournament_name,
												tournament.creator_name,
												0/* tournament.points_to_win */,
												tournament.size, // current_player_num
												1/* tournament.max_player_num */);
			}
		}
		if (data.type === "new_room") {
			console.log("new_room: ", data.room_name);
			console.log('new room: join tournament elements: ', this.join_tournament_elements.children);
			this.createJoinTournamentElement(data.room_name, // tournament_name
											data.creator_name,
											0/* data.points_to_win */,
											data.size, // current_player_num
											1/* data.max_player_num */);
		}


		if (data.type === "room_size_update") {
			console.log("room_size_update");
		}


		if (data.type === "delete_room") {
			console.log("delete_room: ", data.room_name);
			this.deleteJoinTournamentElement(data.room_name);
		}
	}

	/** get's called when someone creates a tournament */
	handleTournamentCreation(event) {
		event.preventDefault();
		
		const	tournament_name = event.target.create_name.value;
		const	number_of_players = event.target.number_of_players.value;
		const	points_to_win = event.target.points_to_win.value;

		// sends the tournament details to the game server
		window.app.socket.send(JSON.stringify({"type": "create_tournament",
											"tournament_name": tournament_name,
											"creator_name": window.app.userData.username,
											"points_to_win": points_to_win,
											"max_player_num": number_of_players}));
		
		console.log("tournament created");
		// goes to the tournament lobby
		window.app.router.go("/tournament-lobby", false); // false means it doesn't get added to the history
		// TODO: should go to the tournament waiting room first !!
	};


	// does this even get called???!!!
	handleJoinTournament(event) {
		console.log("join tournament button clicked in joinTournamentPage");
		let tournament_name = event.target.parentElement.querySelector("[name='join_name']").innerHTML;
		
		window.app.socket.send(JSON.stringify({"type": "join_tournament",
										"tournament_name": tournament_name}));
		window.app.router.go("/tournament-waiting-room", false); // false means it doesn't get added to the history
	}



	/** moves the "display" of the range input to the correct position (above the thumb) and changes the value displayed */
	handleRangeDisplay(event) {
		const min = event.target.min || 0;
		const max = event.target.max || 100;
		const range_width = event.target.offsetWidth - this.thumb_width;
		const thumb_position = ((event.target.value - min) / (max - min)) * range_width;
		const display_position = thumb_position - (this.range_display.offsetWidth / 2);
		
		this.range_display.style.marginLeft = `${display_position}px`;
		this.range_display.innerHTML = event.target.value;
	};
	

	getElementHTML() {
		const template = document.createElement('template');
		template.innerHTML = `
		<scripts-and-styles></scripts-and-styles>
		
		<!-- Tournaments to join -->
			<div class="d-flex flex-column-reverse flex-md-row
						justify-content-center justify-content-evenly
						align-items-md-start
						vw-100 gap-3 row-gap-4 p-4"
			>

		
				<div class="flex-grow-1 tournament-max-width d-flex flex-column row-gap-2"
					id="joinTournamentElements"
				>
					<!-- No tournaments to join (should only appear when there are no tournaments available -->
					<!-- <div id="noTournamentsToJoin" class="text-center text-dark fw-bold fs-1 w-100">No tournaments to join</div> -->
					
					<!-- Join Tournament elements will be added here -->
				</div>
					
				<!-- Create Tournament Form -->
				<div class="flex-shrink-0 flex-grow-0 align-self-center align-self-md-start bg-dark rounded-3 p-3">
				<form id="createTournamentForm">
				<h3 class="text-center text-white fs-4 fw-semibold">Create a Tournament</h3>
					
					<!-- Tournament name -->
					<label for="createName" class="form-label text-white-50">Tournament Name:</label>
					<input name="create_name"
					id="createName"
					type="text"
					class="form-control mb-3"
					placeholder="tournament name"
					value="tournament"
					>
					
					<!-- Number of Players -->
					<label for="createNumberOfPlayers" class="form-label text-white-50">Number of Players:</label>
					<div class="d-flex justify-content-around  mb-3" id="createNumberOfPlayers" role="group">
						<input
						type="radio"
						value="4"
						class="btn-check"
						name="number_of_players"
						id="create4PlayerInput"
						autocomplete="off"
						checked
						>
						<label class="btn btn-outline-custom w-25" for="create4PlayerInput">4</label>
						
						<input
						type="radio"
						value="8"
						class="btn-check"
						name="number_of_players"
						id="create8PlayerInput"
						autocomplete="off"
						>
						<label class="btn btn-outline-custom w-25" for="create8PlayerInput">8</label>
						
						<input
						type="radio"
						value="16"
						class="btn-check"
						name="number_of_players"
						id="create16PlayerInput"
						autocomplete="off"
						>
						<label class="btn btn-outline-custom w-25" for="create16PlayerInput">16</label>
					</div>
					
					<!-- Points required to win one round -->
					<div class="d-flex flex-column mb-3">
						<label for="createPointsToWin" class="form-label text-nowrap text-white-50 mb-4">Points to win one game:</label>
						<div id="createDisplayLane" class="position-absolute mt-4">
							<div id="createPointsToWinDisplay" class="text-white-50 d-inline-block">5</div>
						</div>
						<input type="range"
						class="form-range range-input-slider"
						id="createPointsToWin"
						name="points_to_win"
						min="1"
						max="25"
						step="1"
						value="5"
						>
					</div>
					
					<!-- Submit the form (create a tournament) -->
					<button id="createTournamentButton" type="submit" class="btn btn-custom w-100">create</button>
				</form>
			</div>
		</div>
		`;
		return template;
	}
}

customElements.define('join-tournament-page', JoinTournamentPage);