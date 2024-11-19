import { ComponentBaseClass } from "./componentBaseClass.js";
import { StatisticTournamentElement } from "./StatisticTournamentElement.js";
import { ErrorToastElement } from "./ErrorToastElement.js";

export class StatisticsPage extends ComponentBaseClass {
	constructor() {
		super();
		
	}

	async connectedCallback() {
		super.connectedCallback();

		// adding classes
		this.classList.add("d-flex", "flex-column", "align-items-center", "w-100");
		
		// getting elements
		this.tournament_elements = this.root.getElementById("statTournamentElements");
		this.toast_container = this.root.querySelector(".toast-container");

		// making error toasts
		this.couldnt_fetch_data_toast = new ErrorToastElement("Something went wrong, couldn't fetch data");
		this.toast_container.append(this.couldnt_fetch_data_toast);

		const stats = await this.getStats();
		this.setStats(stats);
	}

	disconnectedCallback() {
		super.disconnectedCallback();

		// remove event listeners
	}

	/// ----- Methods ----- ///

	async getStats() {
		try {
			const response = await fetch('/daphne/get_game_stats', {
				method: 'GET',
				headers: {
					'Content-Type': 'application/json'
				}
			});

			if (!response.ok) {
				const errorText = await response.text();
				throw new Error(`${errorText}`);
			}
			if (response.status === 200) { // ok
				const stats = await response.json();
				return (stats);
			}
			if (response.status === 204) { // no content
				return (null);
			}
			this.couldnt_fetch_data_toast.show();
		} catch (error) {
			this.couldnt_fetch_data_toast.show();
		}
		return (null);
	}

	setStats(stats) {
		if (stats === null) // user hasn't played any matches yet or there is an error (error gets handled in getStats())
			return;
		const lost_percent = stats.losses / stats.total_matches * 100;
		const won_percent = stats.wins / stats.total_matches * 100;
		const lost_bar = this.root.getElementById("statsLostBar");
		const won_bar = this.root.getElementById('statsWonBar');

		this.root.getElementById("statTotalGamesPlayed").innerText = stats.total_matches;
		this.root.getElementById("statsTotalGamesLost").innerText = stats.losses;
		this.root.getElementById("statsTotalGamesWon").innerText = stats.wins;
		this.root.getElementById("statsLostPercent").innerText = parseInt(lost_percent) + "%";
		this.root.getElementById("statsWonPercent").innerText = parseInt(won_percent) + "%"
		lost_bar.style.width = lost_percent + "%";
		lost_bar.setAttribute('aria-valuenow', parseInt(lost_percent));
		won_bar.style.width = won_percent + "%";
		won_bar.setAttribute('aria-valuenow', parseInt(won_percent));

		for (let key in stats.last_matches) {
			const tournament = stats.last_matches[key];
			const element = new StatisticTournamentElement(tournament.loser,
															tournament.winner,
															tournament.loser_score,
															tournament.winner_score,
															tournament.timestamp.split('T')[0]); // maybe put the time as well and not just the date ??!!
			element.highlightUser();
			this.tournament_elements.appendChild(element);
		}
	}


	getElementHTML() {
		const template = document.createElement('template');
		template.innerHTML = `
			<scripts-and-styles style="display: none"></scripts-and-styles>

			<!-- Toasts -->
			<div class="toast-container d-flex flex-column gap-1 position-fixed bottom-0 end-0 p-3">
				<!-- Error toasts will be added here -->
			</div>

			<div class="d-flex flex-column align-items-center w-100 m-4 gap-4">
				<!-- total games -->
				<div class="d-flex flex-column align-items-center bg-dark rounded-3 gap-2 p-2">
					<span id="statTotalGamesPlayed" class="text-white fs-1 lh-1 ">0</span>
					<span class="text-white-50">Total Games Played</span>

				</div>

				<!-- lost/won percentage bar -->
				<div class="d-flex align-items-center bg-dark w-75 rounded-3 gap-2 p-2">
					<div class="d-flex flex-column align-items-center lh-1">
						<span class="text-white-50 mx-auto small">lost</span>
						<span id="statsTotalGamesLost" class="text-white fs-4">0</span>
					</div>

					<div class="bg-dark progress-stacked w-100">
						<div id="statsLostBar"
							class="progress"
							role="progressbar"
							style="width: 0%"
							aria-label="Lost games in percent"
							aria-valuenow="0"
							aria-valuemin="0"
							aria-valuemax="100"
						>
							<div id="statsLostPercent" class="progress-bar bg-danger">0%</div>
						</div>
						<div id="statsWonBar"
							class="progress"
							role="progressbar"
							style="width: 0%"
							aria-label="Won games in percent"
							aria-valuenow="0"
							aria-valuemin="0"
							aria-valuemax="100"
						>
							<div id="statsWonPercent" class="progress-bar bg-success">0%</div>
						</div>
					</div>

					<div class="d-flex flex-column align-items-center lh-1">
						<span class="text-white-50 mx-auto small">won</span>
						<span id="statsTotalGamesWon" class="text-white fs-4">0</span>
					</div>
				</div>
			</div>

			<hr class="w-75 text-white-50 m-0">
			
			<div id="statTournamentElements" class="d-flex flex-column m-4 gap-2 w-75">
				<span class="text-white">Last Games:</span>
				<!-- Stat Tournament elements will be added here -->
			</div>
		`;
		return template;
	}
}

customElements.define('statistics-page', StatisticsPage);