import { ComponentBaseClass } from "./componentBaseClass.js";

export class JoinTournamentPage extends ComponentBaseClass {	
	connectedCallback() {
		super.connectedCallback();
		
		// Binds the method to this class instance so it can be used in the event listener
		this.handleRangeDisplay = this.handleRangeDisplay.bind(this);
		
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
		const template = document.getElementById('joinTournamentPageTemplate');
		/* template.innerHTML = `
			
		`; */
		return template;
	}
}

customElements.define('join-tournament-page', JoinTournamentPage);