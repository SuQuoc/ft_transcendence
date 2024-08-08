import { ComponentBaseClass } from "./componentBaseClass.js";

export class JoinTournamentPage extends ComponentBaseClass {	
	connectedCallback() {
		super.connectedCallback();
		
		// Binds the method to this class instance so it can be used in the event listener
		this.handleRangeDisplay = this.handleRangeDisplay.bind(this);
		
		// getting elements
		this.create_tournament_form = this.root.getElementById("createTournamentForm");
		this.range_display = this.root.getElementById("tournamentPointsToWinDisplay");
		this.display_lane = this.root.getElementById("tournamentDisplayLane");
		this.input_range = this.root.getElementById("tournamentPointsToWin");
		
		// making the "lane" the display div moves in the same width as the middle of the thumb from end to end of the range input (so the percentage is correct)
		this.thumb_width = 16; // it's also defined in template.css, so if you change it here, change it there as well
		this.display_lane.style.paddingLeft = `${this.thumb_width / 2}px`;
		this.display_lane.style.paddingRight = `${this.thumb_width / 2}px`;

		// adding event listener
		this.create_tournament_form.addEventListener("submit", this.handleTournamentCreation);
		this.input_range.addEventListener("input", this.handleRangeDisplay);

		// calling the method to set the initial position of the display
		this.handleRangeDisplay({target: this.input_range});
	};

	disconnectedCallback() {
		super.disconnectedCallback();
		
		this.removeEventListener("input", this.handleRangeDisplay);
	};
	
	/// ----- Event Handlers ----- ///

	handleTournamentCreation(event) {
		event.preventDefault();
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