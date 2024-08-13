import Router from './router.js';

// link custom web components
import { JoinTournamentPage } from './js/JoinTournamentPage.js';
import { LoginPage } from './js/LoginPage.js';
import { PlayMenuHomePage } from './js/PlayMenuHomePage.js';
import { ScriptsAndStyles } from './js/ScriptsAndStyles.js';
import { SignupPage } from './js/SignupPage.js';

// global
window.app = {}
app.router = Router;

console.log("app.js loaded");
// it's better to wait for the DOM to load before running any JS
window.addEventListener("DOMContentLoaded", async () => {
	// adds event listeners for routing
	app.router.init();
});