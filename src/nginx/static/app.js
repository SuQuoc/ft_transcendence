import Router from './router.js';

// global
window.app = {
	router: Router,
	socket: null,
	userData: {}
};

// link custom web components
import { FindOpponentPage } from './js/FindOpponentPage.js';
import { LoginPage } from './js/LoginPage.js';
import { SignupPage } from './js/SignupPage.js';
import { UserProfile } from './js/UserProfile.js';
import { JoinTournamentPage } from './js/JoinTournamentPage.js';
import { PlayMenuHomePage } from './js/PlayMenuHomePage.js';
import { PongPage } from './js/PongPage.js';
import { ScriptsAndStyles } from './js/ScriptsAndStyles.js';
import { FriendList } from './js/FriendList.js';
import { FriendSearch } from './js/FriendSearch.js';
import { TournamentLobbyPage } from './js/TournamentLobbyPage.js';
import { TournamentWaitingRoomPage } from './js/TournamentWaitingRoomPage.js';


console.log("app.js loaded");
// it's better to wait for the DOM to load before running any JS
window.addEventListener("DOMContentLoaded", async () => {
	// replaces the "null" state the browser pushes to the history when the page is loaded
	if (!history.state)
		history.replaceState({route: location.pathname}, "", location.pathname);

	// adds event listeners for routing
	await app.router.init();
});