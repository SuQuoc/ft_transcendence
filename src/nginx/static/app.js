import Router from './router.js';

// link custom web components
import { PlayMenu } from './js/PlayMenu.js';


// global
window.app = {}
app.router = Router;

console.log("app.js loaded");
// it's better to wait for the DOM to load before running any JS
window.addEventListener("DOMContentLoaded", async () => {
	// adds event listeners for routing
	app.router.init();
});