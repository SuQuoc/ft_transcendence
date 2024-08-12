import { ComponentBaseClass } from "./componentBaseClass.js";
import { JoinTournamentElement } from "./JoinTournamentElement.js";

export class JoinTournamentPage extends ComponentBaseClass {	
	connectedCallback() {
		super.connectedCallback();
		


		// Binds the method to this class instance so it can be used in the event listener
		this.handleRangeDisplay = this.handleRangeDisplay.bind(this);
		this.handleTournamentCreation = this.handleTournamentCreation.bind(this); // temporary !!!!!

		// getting elements
		this.create_tournament_form = this.root.getElementById("createTournamentForm");
		this.range_display = this.root.getElementById("createPointsToWinDisplay");
		this.display_lane = this.root.getElementById("createDisplayLane");
		this.input_range = this.root.getElementById("createPointsToWin");
		
		// making the "lane" the display div moves in the same width as the middle of the thumb from end to end of the range input (so the percentage is correct)
		this.thumb_width = 16; // it's also defined in template.css, so if you change it here, change it there as well
		this.display_lane.style.paddingLeft = `${this.thumb_width / 2}px`;
		this.display_lane.style.paddingRight = `${this.thumb_width / 2}px`;

		// adding event listeners
		this.create_tournament_form.addEventListener("submit", this.handleTournamentCreation);
		this.input_range.addEventListener("input", this.handleRangeDisplay);

		// calling the method to set the initial position of the display
		this.handleRangeDisplay({target: this.input_range});
	};

	disconnectedCallback() {
		super.disconnectedCallback();
		
		// removing event listeners
		this.create_tournament_form.removeEventListener("submit", this.handleTournamentCreation);
		this.input_range.removeEventListener("input", this.handleRangeDisplay);
	};
	



	/// ----- Methods ----- ///
	createJoinTournamentElement(name, points_to_win, max_player_num, current_player_num = 1) {
		let element = new JoinTournamentElement(); // protect new ???!!!!??
		this.root.getElementById("joinTournamentElements").appendChild(element);
		
		element.querySelectorAll("[name='join_name']")[0].innerHTML = name;
		element.querySelectorAll("[name='join_creator']")[0].innerHTML = "creator name"; // temporary !!!!! (should be the name of the display name of the client)
		element.querySelectorAll("[name='join_points_to_win']")[0].innerHTML = points_to_win;
		element.querySelectorAll("[name='join_current_player_num']")[0].innerHTML = current_player_num;
		element.querySelectorAll("[name='join_max_player_num']")[0].innerHTML = max_player_num;

		this.noTournamentsToJoin();
	};

	/** hides or shows a text that says "no tournaments to join" */
	noTournamentsToJoin() {
		const tournament_elements = this.root.querySelectorAll("join-tournament-element");
		console.log("tournament_elements: ", tournament_elements);

		if (tournament_elements === null || tournament_elements.length === 0) {
			this.root.getElementById("noTournamentsToJoin").style.display = "";
		}
		else {
			this.root.getElementById("noTournamentsToJoin").style.display = "none";
		}
	};




	/// ----- Event Handlers ----- ///
	/** get's called when someone creates a tournament, doesn't do anything yet */
	handleTournamentCreation(event) {
		event.preventDefault();

		const	number_of_players = event.target.number_of_players.value;
		const	points_to_win = event.target.points_to_win.value;
		let		tournament_name = event.target.create_name.value;

		if (tournament_name === "") {
			tournament_name = "tournament";
		}
		console.log("tournament name: ", tournament_name,
					"\nnumber of players: ", number_of_players,
					"\npoints to win: ", points_to_win);

		// console.log("event: ", event);
		this.createJoinTournamentElement(tournament_name, points_to_win, number_of_players);
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

	getElementHTML() {
		//const template = document.getElementById('joinTournamentPageTemplate');

		const template = document.createElement('template');
		template.innerHTML = `
			<scripts-and-styles></scripts-and-styles>

			<!-- Tournaments to join -->
				<!-- align-items-end because flex-wrap-reverse reverses that as well. The elements are at the top -->
			<div class="d-flex flex-row flex-wrap-reverse align-items-end
						justify-content-center justify-content-evenly
						vw-100 gap-3 gap-row-4 p-4"
			>

		
				<div class="flex-grow-1 tournament-max-width d-flex flex-column row-gap-2"
					id="joinTournamentElements"
				>
					<!-- No tournaments to join (should only appear when there are no tournaments available -->
					<div id="noTournamentsToJoin" class="text-center text-dark fw-bold fs-1 w-100">No tournaments to join</div>
					
					<!-- Join Tournament elements will be added here -->
				</div>
		
				<!-- Create Tournament Form -->
				<div class="p-3 rounded-3 bg-dark">
					<form id="createTournamentForm">
						<h3 class="text-center text-white">Create a Tournament</h3>
						
						<!-- Tournament name -->
						<label for="createName" class="form-label text-white-50">Tournament Name:</label>
						<input name="create_name"
						id="createName"
						type="text"
						class="form-control mb-3"
						placeholder="tournament name"
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
							<label class="btn btn-outline-secondary w-25" for="create4PlayerInput">4</label>
							
							<input
							type="radio"
							value="8"
							class="btn-check"
							name="number_of_players"
							id="create8PlayerInput"
							autocomplete="off"
							>
							<label class="btn btn-outline-secondary w-25" for="create8PlayerInput">8</label>
							
							<input
							type="radio"
							value="16"
							class="btn-check"
							name="number_of_players"
							id="create16PlayerInput"
							autocomplete="off"
							>
							<label class="btn btn-outline-secondary w-25" for="create16PlayerInput">16</label>
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
						<button type="submit" class="btn btn-secondary w-100">create</button>
					</form>
				</div>
			</div>
		`;
		return template;
	}
}

customElements.define('join-tournament-page', JoinTournamentPage);