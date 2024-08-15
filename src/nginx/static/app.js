import Router from './router.js';

// link custom web components
import { JoinTournamentPage } from './js/JoinTournamentPage.js';
import { LoginPage } from './js/LoginPage.js';
import { PlayMenuHomePage } from './js/PlayMenuHomePage.js';
import { ScriptsAndStyles } from './js/ScriptsAndStyles.js';
import { SignupPage } from './js/SignupPage.js';
import { TournamentLobbyPage } from './js/TournamentLobbyPage.js';
import { TournamentWaitingRoomPage } from './js/TournamentWaitingRoomPage.js';

// global
window.app = {}
app.router = Router;
app.socket = null;

console.log("app.js loaded");
// it's better to wait for the DOM to load before running any JS
window.addEventListener("DOMContentLoaded", async () => {
	// adds event listeners for routing
	app.router.init();
});