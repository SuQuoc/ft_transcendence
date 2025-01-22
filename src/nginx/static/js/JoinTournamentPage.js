import { ComponentBaseClass } from "./componentBaseClass.js";
import { JoinTournamentElement } from "./JoinTournamentElement.js";
import { ErrorToastElement } from "./ErrorToastElement.js";

export class JoinTournamentPage extends ComponentBaseClass {
	constructor() {
		super();
		
		// Binds the method to this class instance so it can be used in the event listener
		this.handleReceivedMessage_var = this.handleReceivedMessage.bind(this);
		this.handleRangeDisplay_var = this.handleRangeDisplay.bind(this);
		this.handleTournamentCreation_var = this.handleTournamentCreation.bind(this);
		this.handleHideTournamentNameError_var = this.handleHideTournamentNameError.bind(this);
		
		// getting elements
		this.join_tournament_elements = this.root.getElementById("joinTournamentElements");
		this.waiting_for_permission = this.root.getElementById("joinWaitingForPermission");
		this.no_tournaments_to_join = this.root.getElementById("joinNoTournaments");
		this.join_tournament_page = this.root.getElementById("joinTournamentPage");
		this.create_tournament_form = this.root.getElementById("createTournamentForm");
		this.tournament_name_error = this.root.getElementById("createTournamentNameError");
		this.tournament_name_input = this.root.getElementById("createNameInput");
		this.range_display = this.root.getElementById("createPointsToWinDisplay");
		this.display_lane = this.root.getElementById("createDisplayLane");
		this.input_range = this.root.getElementById("createPointsToWin");
		this.toast_container = this.root.querySelector(".toast-container");
		
		// making the "lane" the display div moves in the same width as the middle of the thumb from end to end of the range input (so the percentage is correct)
		this.thumb_width = 16; // it's also defined in template.css, so if you change it here, change it there as well
		this.display_lane.style.paddingLeft = `${this.thumb_width / 2}px`;
		this.display_lane.style.paddingRight = `${this.thumb_width / 2}px`;

		// making error toasts
		this.room_full_toast = new ErrorToastElement("This room is already full, you were too slow...");
		this.already_in_room_toast = new ErrorToastElement("You are already in a room");
		this.room_does_not_exist_toast = new ErrorToastElement("This room does not exist, if you see this message something went wrong");
		this.toast_container.append(this.room_full_toast, this.already_in_room_toast, this.room_does_not_exist_toast);

		// adding event listeners
		if (window.app.socket)
			window.app.socket.addEventListener("message", this.handleReceivedMessage_var);
		this.join_tournament_elements.addEventListener("click", this.handleJoinTournament);
		this.create_tournament_form.addEventListener("submit", this.handleTournamentCreation_var);
		this.tournament_name_input.addEventListener("input", this.handleHideTournamentNameError_var);
		this.input_range.addEventListener("input", this.handleRangeDisplay_var);

		// getting the list of tournaments
		this.getTournamentList();
	};

	connectedCallback() {
		super.connectedCallback();

		// calling the method to set the initial position of the display
		setTimeout(() => { // needs to happen in setTimeout, to give the browser enough time to render everything before we can calculate the correct position
			this.handleRangeDisplay({target: this.input_range});
		}, 0);
	};

	disconnectedCallback() {
		super.disconnectedCallback();
		
		// removing event listeners
		if (window.app.socket)
			window.app.socket.removeEventListener("message", this.handleReceivedMessage_var);
		this.join_tournament_elements.removeEventListener("click", this.handleJoinTournament);
		this.create_tournament_form.removeEventListener("submit", this.handleTournamentCreation_var);
		this.tournament_name_input.removeEventListener("input", this.handleHideTournamentNameError_var);
		this.input_range.removeEventListener("input", this.handleRangeDisplay_var);
	};
	

	/// ----- Methods ----- ///

	/** handles all known errors recieved from the message event handler */
	tournamentErrors(error) {
		this.waitingForPermission(false); // shows the join tournament elements and the create tournament form
		if (error === "room_name_taken") {
			this.tournament_name_error.innerText = "Tournament name already taken";
			this.tournament_name_error.style.display = "";
		}
		else if (error === "room_full") {
			this.room_full_toast.show();
		}
		else if (error === "already_in_room") {
			this.already_in_room_toast.show();
		}
		else if (error === "room_does_not_exist") {
			this.room_does_not_exist_toast.show();
		}
		else if (error === "room_name_invalid") {
			this.tournament_name_error.innerText = "Tournament name not valid";
			this.tournament_name_error.style.display = "";
		}
		else
			console.error("Error: tournamentError: unknown error: ", error);
	};

	/** hides or shows a text that says "no tournaments to join" */
	noTournamentsToJoin() {
		const tournament_elements = this.join_tournament_elements.querySelectorAll("join-tournament-element");

		if (tournament_elements === null || tournament_elements.length === 0) {
			this.no_tournaments_to_join.style.display = "";
			this.join_tournament_elements.classList.add("align-self-center");
		} else {
			this.no_tournaments_to_join.style.display = "none";
			this.join_tournament_elements.classList.remove("align-self-center");
		}
	};

	/** hides the join tournament elements and the create tournament form and shows the waiting for permission message.
	 * @param {boolean} waiting - (optional: if true (default), it shows the waiting for permission message, if false, it shows the join tournament elements and the create tournament form)
	 */
	waitingForPermission(waiting=true) {
		if (waiting) {
			this.join_tournament_page.style.display = "none";
			this.join_tournament_page.classList.remove("d-flex"); // need to remove this so it hides
			this.waiting_for_permission.style.display = "";	
			return;
		}
		if (!this.join_tournament_page.classList.contains("d-flex")) {
			this.join_tournament_page.style.display = "";
			this.join_tournament_page.classList.add("d-flex");
			this.waiting_for_permission.style.display = "none";
		}
	}

	/** creates a new joinTournamentElement and appends it to the joinTournamentElements div */
	createJoinTournamentElement(tournament_name, creator_name, points_to_win, current_player_num, max_player_num) {
		let element = new JoinTournamentElement();
		if (!element)
			return;

		element.setAttribute('name', tournament_name);
		this.join_tournament_elements.appendChild(element);

		element.querySelector("[name='join_name']").innerHTML = tournament_name;
		element.querySelector("[name='join_creator']").innerHTML = creator_name;
		element.querySelector("[name='join_points_to_win']").innerHTML = points_to_win;
		element.querySelector("[name='join_current_player_num']").innerHTML = current_player_num;
		element.querySelector("[name='join_max_player_num']").innerHTML = max_player_num;
		
		this.noTournamentsToJoin();
	};

	/** deletes a joinTournamentElement */
	deleteJoinTournamentElement(tournament_name) {
		let element = this.join_tournament_elements.querySelector(`join-tournament-element[name='${tournament_name}']`);
		if (!element)
			return;

		this.join_tournament_elements.removeChild(element);
		this.noTournamentsToJoin();
	};

	/** updates the 'current_player_num' of the 'join-tournament-element' with the tournament_name passed */
	updateCurrentPlayerNum(tournament_name, current_player_num) {
		let element = this.join_tournament_elements.querySelector(`join-tournament-element[name='${tournament_name}']`);
		if (!element)
			return;

		element.querySelector("[name='join_current_player_num']").innerHTML = current_player_num;
	}
	
	/** sends a message to the server to get the list of tournaments */
	getTournamentList() {
		if (!window.app.socket) {
			window.app.router.go("/"); // goes to the home page
		}

		if (window.app.socket.readyState === WebSocket.OPEN) {
			window.app.socket.send(JSON.stringify({"type": "get_tournament_list"}));
		} else {
			window.app.socket.addEventListener('open', () => {
				window.app.socket.send(JSON.stringify({"type": "get_tournament_list"}));
			}, { once: true });
		}
		this.noTournamentsToJoin();
	}
	

	/// ----- Event Handlers ----- ///

	/** hides the tournament name error message */
	handleHideTournamentNameError(event) {
		if (this.tournament_name_error.style.display === "") {
			this.tournament_name_error.style.display = "none";
			this.tournament_name_error.innerText = "";
		}
	}

	/** get's called when someone creates a tournament */
	handleTournamentCreation(event) {
		event.preventDefault();

		const	tournament_name = event.target.create_name.value;
		const	number_of_players = event.target.number_of_players.value;
		const	points_to_win = event.target.points_to_win.value;

		// sends the tournament details to the game server
		window.app.socket.send(JSON.stringify({"type": "create_room",
											"room_name": tournament_name,
											"points_to_win": points_to_win,
											"max_player_num": number_of_players}));
		
		this.waitingForPermission(); // waiting for permission to go to the tournament lobby
	};

	handleJoinTournament(event) {
		if (event.target.tagName !== "BUTTON")
			return;

		let tournament_name = event.target.parentElement.querySelector("[name='join_name']").innerHTML;
		
		window.app.socket.send(JSON.stringify({"type": "join_room", "room_name": tournament_name}));
	};

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
	
	/** gets called when the websocket receives a message */
	handleReceivedMessage(event) {
		const data = JSON.parse(event.data);
				
		if (data.type === "room_size_update") {
			this.updateCurrentPlayerNum(data.room_name, data.cur_player_num);
		}
		else if (data.type === "new_room") {
			this.createJoinTournamentElement(data.room.name, // tournament_name
											data.room.creator_name,
											data.room.points_to_win,
											data.room.cur_player_num, // current_player_num
											data.room.max_player_num);
		}
		else if (data.type === "delete_room") {
			this.deleteJoinTournamentElement(data.room_name);
		}
		else if (data.type === "success") {
			// going to the tournament lobby
			window.app.router.go("/tournament-lobby", false, data.room_name);
		}
		else if (data.type === "tournament_list") {
			for (let tournament_name in data.tournaments) {
				const tournament = data.tournaments[tournament_name];
				this.createJoinTournamentElement(tournament_name,
												tournament.creator_name,
												tournament.points_to_win,
												tournament.cur_player_num, // current_player_num
												tournament.max_player_num);
			}
		}
		else if (data.type === "tournament_bracket") {
			window.app.socket_event_queue.add(event);
		}
		else if (data.type === "error") {
			this.tournamentErrors(data.error);
		}
		else {
			console.error("Error: handleReceivedMessage: unknown data type: ", data.type);
		}
	};

	getElementHTML() {
		const template = document.createElement('template');
		template.innerHTML = `
			<scripts-and-styles></scripts-and-styles>

			<!-- Toasts -->
			<div class="toast-container d-flex flex-column gap-1 position-fixed bottom-0 end-0 p-3">
				<!-- Error toasts will be added here -->
			</div>

			<!-- Tournaments to join -->
			<div id="joinTournamentPage"
				class="d-flex flex-column-reverse flex-md-row
						justify-content-center justify-content-evenly
						align-items-md-start
						vw-100 gap-3 row-gap-4 p-4"
			>

		
				<div class="flex-grow-1 tournament-max-width d-flex flex-column row-gap-2"
					id="joinTournamentElements"
				>
					<!-- No tournaments to join (should only appear when there are no tournaments available -->
					<div id="joinNoTournaments" class="text-center text-dark fw-bold fs-1 w-100">No tournaments to join</div>
					
					<!-- Join Tournament elements will be added here -->
				</div>
					
				<!-- Create Tournament Form -->
				<div class="flex-shrink-0 flex-grow-0 align-self-center align-self-md-start bg-dark rounded-3 p-3">
					<form id="createTournamentForm">
					<h3 class="text-center text-white fs-4 fw-semibold">Create a Tournament</h3>
						
						<!-- Tournament name -->
						<label for="createNameInput" class="form-label text-white-50">Tournament Name:</label>
						<input name="create_name"
							id="createNameInput"
							type="text"
							class="form-control mb-2"
							placeholder="tournament name"
							maxlength="30"
							required
						>
						<div id="createTournamentNameError" class="text-danger" style="display: none"></div>
						
						<!-- Number of Players -->
						<label for="createNumberOfPlayers" class="form-label text-white-50 mt-2">Number of Players:</label>
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

			<!-- when waiting for permission to go to the tournament lobby -->
			<h1 id="joinWaitingForPermission" style="display: none">Waiting for permission to join the tournament...</H1>
			`;
			return template;
	}
}

customElements.define('join-tournament-page', JoinTournamentPage);