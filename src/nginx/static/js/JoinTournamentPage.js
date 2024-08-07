import { ComponentBaseClass } from "./componentBaseClass.js";

export class JoinTournamentPage extends ComponentBaseClass {
	constructor() {
		super(); // always call super() (it calls the constructor of the parent class)
	};	

	connectedCallback() {
		super.connectedCallback();
		
		this.handleRangeDisplay = this.handleRangeDisplay.bind(this); // Binds the method to this class instance
		
		this.range_display = this.root.getElementById("tournamentPointsToWinDisplay");
		this.input_range = this.root.getElementById("tournamentPointsToWin");
		this.input_range.addEventListener("input", this.handleRangeDisplay);
	};

	disconnectedCallback() {
		super.disconnectedCallback();
		
		this.removeEventListener("input", this.handleRangeDisplay);
	};
	
	// 
	handleRangeDisplay(event) {
		const range_width = event.target.offsetWidth;
		const max = event.target.max || 100;
		const min = event.target.min || 0;

		console.log(((event.target.value - min) / (max - min)) * range_width);
		this.range_display.style.left = `${((event.target.value - min) / (max - min)) * range_width}px`; // calculates the position of the thumb so the number is above it
		this.range_display.innerHTML = event.target.value;
	};

	getElementHTML() { // maybe this should be a static method?!
		const template = document.getElementById('joinTournamentPageTemplate');
		/* template.innerHTML = `
			
		`; */
		return template;
	}
}

customElements.define('join-tournament-page', JoinTournamentPage);