import Router from './router.js';

// global
const storedUserData = JSON.parse(localStorage.getItem('userData')) || {
	username: null, // maybe this should be changed to displayname
	email: null,
	profileImage: null,
};

window.app = {
	router: Router,
	socket: null,
	pong_socket: null,
	userData: storedUserData,
};

// Save userData to localStorage whenever it changes
window.addEventListener('beforeunload', () => {
	localStorage.setItem('userData', JSON.stringify(window.app.userData));
});

// link custom web components
import { MatchPage } from './js/MatchPage.js';
import { LoginPage } from './js/LoginPage.js';
import { SelectDisplaynamePage } from './js/SelectDisplaynamePage.js';
import { SignupPage } from './js/SignupPage.js';
import { UserProfile } from './js/UserProfile.js';
import { JoinTournamentPage } from './js/JoinTournamentPage.js';
import { PlayMenuHomePage } from './js/PlayMenuHomePage.js';
import { ScriptsAndStyles } from './js/ScriptsAndStyles.js';
import { FriendList } from './js/FriendList.js';
import { FriendSearch } from './js/FriendSearch.js';
import { TournamentLobbyPage } from './js/TournamentLobbyPage.js';
import { ForgotPassword} from './js/ForgotPassword.js'


console.log("app.js loaded");
// it's better to wait for the DOM to load before running any JS
window.addEventListener("DOMContentLoaded", async () => {
	//required to parse the parameters received from OAuth callback
	const queryParams = new URLSearchParams(window.location.search);
	if (queryParams.has("code") && queryParams.has("state")) {
		localStorage.setItem("oauthCode", queryParams.get("code"));
		localStorage.setItem("oauthState", queryParams.get("state"));
	}
	// replaces the "null" state the browser pushes to the history when the page is loaded
	if (!history.state)
		history.replaceState({route: location.pathname}, "", location.pathname);

	// adds event listeners for routing
	await app.router.init();
});