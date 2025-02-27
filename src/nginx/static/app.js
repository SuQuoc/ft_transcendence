import Router from './router.js';
import { EventQueue } from './js/eventQueueClass.js';
import { OnlineWebSocketClass } from './js/OnlineWebSocketClass.js';

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
	match_socket: null,
	online_socket: new OnlineWebSocketClass(),
	userData: storedUserData,
	socket_event_queue: new EventQueue()
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
import { StatisticsPage } from './js/StatisticsPage.js';


// it's better to wait for the DOM to load before running any JS
window.addEventListener('DOMContentLoaded', async () => {
	//required to parse the parameters received from OAuth callback
	const queryParams = new URLSearchParams(window.location.search);
	if (queryParams.has("code") && queryParams.has("state")) {
		localStorage.setItem("oauthCode", queryParams.get("code"));
		localStorage.setItem("oauthState", queryParams.get("state"));
	}
	// replaces the "null" state the browser pushes to the history when the page is loaded
	if (!history.state)
		history.replaceState({route: location.pathname}, "", location.pathname);

	// adding event handlers to add and remove the userprofile sidemenu
	const userProfileButton = document.getElementById("userProfileButton");
	const userProfileClose = document.getElementById("userProfileClose");
	const userProfile = document.getElementById("userProfile");
	if (!userProfileButton || !userProfileClose || !userProfile) // protect against null values (happens if we show error page)
		return;

	userProfileButton.addEventListener('click', handleAddUserProfile);
	userProfileClose.addEventListener('click', handleDeleteUserProfile);
	userProfile.addEventListener('hidden.bs.offcanvas', handleDeleteUserProfile);
	userProfileButton.addEventListener('keydown', (e) => {
		if (e.key === "Enter" || e.key === " ") {
			let bsOffcanvas = bootstrap.Offcanvas.getInstance(userProfile);
			if (!bsOffcanvas) {
				bsOffcanvas = new bootstrap.Offcanvas(userProfile);
			}
			if (userProfile.classList.contains('show')) {
				bsOffcanvas.hide();
				handleDeleteUserProfile();
			} else {
				handleAddUserProfile();
				bsOffcanvas.show();
			}
		}
	});

	// adds event listeners for routing
	await app.router.init();
});


/** Adding the user profile when the user profile button in the navbar is clicked */
function handleAddUserProfile() {
	const userProfileContainer = document.getElementById("userProfileContainer");
	userProfileContainer.appendChild(document.createElement("user-profile"));
};
/** Deleting the user profile when the user profile is closed */
function handleDeleteUserProfile() {
	const userProfileContainer = document.getElementById("userProfileContainer");
	if (userProfileContainer.innerHTML != "")
		userProfileContainer.innerHTML = "";
};
