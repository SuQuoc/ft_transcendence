//import Store from './services/Store.js';
//import API from './services/API.js';
//import { loadData } from './services/Menu.js';
import Router from '../../router.js';

// link my web components
import { PlayMenu } from '../../js/PlayMenu.js';


// to make Store global
window.app = {}
//app.store = Store;
app.router = Router;


console.log("global");
// it's better to wait for the DOM to load before running any JS
window.addEventListener("DOMContentLoaded", async () => {
	//loadData();
	console.log("DOM loaded");
	// adds event listeners for routing
	app.router.init();
});

