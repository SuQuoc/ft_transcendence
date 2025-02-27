import { ComponentBaseClass } from "./componentBaseClass.js";
import { StatisticTournamentElement } from "./StatisticTournamentElement.js";
import { ErrorToastElement } from "./ErrorToastElement.js";

export class StatisticsPage extends ComponentBaseClass {
	/** 
	 * @param {string} user_data - is used when a user looks up another user. If the user looks up themselves, it should be empty ("").
	*/
	constructor(user_data) {
		super();

		if (!user_data || user_data === "") {
			this.user_id = "";
			this.root.getElementById("statsProfileImage").src = window.app.userData.profileImage;
			this.root.getElementById("statsDisplayname").innerText = window.app.userData.username;
		}
		else {
			this.user_id = user_data.id;
			this.root.getElementById("statsProfileImage").src = user_data.image;
			this.root.getElementById("statsDisplayname").innerText = user_data.name;
		}
	}

	async connectedCallback() {
		// adding classes
		this.classList.add("d-flex", "flex-column", "align-items-center", "w-100");
		
		// getting elements
		this.tournament_elements = this.root.getElementById("statsTournamentElements");
		this.toast_container = this.root.querySelector(".toast-container");

		// making error toasts
		this.couldnt_fetch_data_toast = new ErrorToastElement("Something went wrong, couldn't fetch data");
		this.toast_container.append(this.couldnt_fetch_data_toast);

		const stats = await this.fetchStats(this.user_id);
		this.setStats(stats);
	}

	disconnectedCallback() {
		// remove event listeners
	}


	/// ----- Methods ----- ///

	async fetchStats(user_id) {
		try {
			let stats = null;
			if (!user_id || user_id === "")
				stats = await this.apiFetch("game/get_game_stats/", { method: "GET" });
			else
				stats = await this.apiFetch(`game/get_game_stats?profile_id=${user_id}`, { method: "GET" });
			return (stats);
		} catch (error) {
			this.couldnt_fetch_data_toast.show();
		}
		return (null);
	}


	setStats(stats) {
		if (stats === null || stats === undefined) // user hasn't played any matches yet or there is an error
			return;
		const lost_percent = stats.losses / stats.total_matches * 100;
		const won_percent = stats.wins / stats.total_matches * 100;
		const lost_bar = this.root.getElementById("statsLostBar");
		const won_bar = this.root.getElementById("statsWonBar");

		this.root.getElementById("statsNoGamesPlayed").classList.add("d-none");
		this.root.getElementById("statsLastGames").classList.remove("d-none");
		this.root.getElementById("statsTotalGamesPlayed").innerText = stats.total_matches;
		this.root.getElementById("statsTotalGamesLost").innerText = stats.losses;
		this.root.getElementById("statsTotalGamesWon").innerText = stats.wins;
		this.root.getElementById("statsLostPercent").innerText = Number.parseFloat(lost_percent.toFixed(2)) + "%";
		this.root.getElementById("statsWonPercent").innerText = Number.parseFloat(won_percent.toFixed(2)) + "%"
		lost_bar.style.width = lost_percent + "%";
		lost_bar.setAttribute("aria-valuenow", Number.parseFloat(lost_percent.toFixed(2)));
		won_bar.style.width = won_percent + "%";
		won_bar.setAttribute("aria-valuenow", Number.parseFloat(won_percent.toFixed(2)));

		for (let key in stats.last_matches) {
			const tournament = stats.last_matches[key];
			const element = new StatisticTournamentElement(tournament.loser,
															tournament.winner,
															tournament.loser_score,
															tournament.winner_score,
															tournament.timestamp.split('T')[0]);
			element.highlightUser();
			this.tournament_elements.appendChild(element);
		}
	}


	getElementHTML() {
		const template = document.createElement("template");
		template.innerHTML = `
			<scripts-and-styles></scripts-and-styles>
			<!-- Toasts -->
			<div class="toast-container d-flex flex-column gap-1 position-fixed bottom-0 end-0 p-3">
				<!-- Error toasts will be added here -->
			</div>

			<div class="d-flex flex-column align-items-center w-100 m-4 gap-4">
				<!-- profile picture and displayname -->
				<div class="d-flex bg-dark rounded-4 mx-4 p-2 gap-1">
					<img src="/media_url/profile_images/default_avatar.png"
					class="big-profile-image m-0 p-0"
					id="statsProfileImage"
					alt="Profile Image"
					onerror='this.src = "/media_url/profile_images/default_avatar.png"'
					>
					<div class="d-flex flex-column align-items-center h-auto p-1">
						<div class="d-flex align-items-center h-50">
							<span id="statsDisplayname" class="text-break text-white fs-4 lh-1">displayname</span>
						</div>

						<hr class="w-75 text-secondary m-0">

						<!-- total games -->
						<div class="d-flex flex-column align-items-center justify-content-around h-50">
							<div class="d-flex flex-column align-items-center">
								<span id="statsTotalGamesPlayed" class="text-white fs-1 lh-1">0</span>
								<span class="text-nowrap text-secondary">Total Games played</span>
							</div>
						</div>
					</div>
				</div>

				<!-- lost/won percentage bar -->
				<div class="d-flex align-items-center bg-dark w-75 rounded-3 gap-2 p-2">
					<div class="d-flex flex-column align-items-center lh-1">
						<span class="text-secondary mx-auto small">lost</span>
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
						<span class="text-secondary mx-auto small">won</span>
						<span id="statsTotalGamesWon" class="text-white fs-4">0</span>
					</div>
				</div>
			</div>

			<hr class="w-75 text-secondary m-0">
			
			<div id="statsTournamentElements" class="d-flex flex-column m-4 gap-2 w-75">
				<div id="statsNoGamesPlayed" class="text-center text-white fw-bold fs-1 w-100">No games played yet</div>
				<span id="statsLastGames" class="d-none text-white">Last Games:</span>
				<!-- Stat Tournament elements will be added here -->
			</div>
		`;
		return template;
	}
}

customElements.define('statistics-page', StatisticsPage);