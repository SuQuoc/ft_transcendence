import API from './API.js';

// function needs to be async because of await
export async function loadData() {
	API.fetchMenu();
	app.store.meny = await API.fetchMenu();
}