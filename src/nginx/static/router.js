import { TournamentLobbyPage } from './js/TournamentLobbyPage.js';

const validateToken = async () => {
	try {
		// check if the token is valid
		const response = await fetch("/registration/verify_token", {
			method: "GET",
			headers: {
				"Content-Type": "application/json"
			},
			credentials: "include"
		});

		if (response.status !== 200) {
			const errorData = await response.json();
			if (errorData.detail === "No access token provided") {
				console.log("No access token provided");
				return false;
			}
			throw new Error(errorData.detail || "Token is invalid");
		}

		return true;
	} catch (error) {
		console.log("Error validating token, trying to refresh: ", error.message);

		try {
			const refreshResponse = await fetch("/registration/refresh_token", {
				method: "GET",
				headers: {
					"Content-Type": "application/json"
				},
				credentials: "include"
			});

			if (refreshResponse.status !== 200) {
				throw new Error("Error refreshing token");
			}
			return true;
		} catch (refreshError) {
			console.error("Error refreshing token:", refreshError.message);
			return false;
		}
	}
}

/** Checks if the displayname is already set. If not it asks the um server for it and if the user hasn't chosen one yet, they get reroutet to /display */
const getUserData = async () => {
	if (window.app.userData.username && window.app.userData.profileImage) // if the displayname is already set we don't need to fetch it
		return;

	try {
		// Check if the user already has a displayname
		const response = await fetch ('/um/profile', {
			method: 'GET',
			headers: {
				'Content-Type': 'application/json'
			}
		});
		
		// Redirects to the home page if the user already has a displayname or to the select displayname page if they don't
		if (!response.ok) {
			window.app.router.go('/displayname', false);
		} else {
			const responseData = await response.json();
			window.app.userData.username = responseData.displayname;
			window.app.userData.profileImage = responseData.image;
			app.router.go('/', false);
		}
	} catch (error) {
		console.error('Error getting userdata (router):', error);
	}
}

const checkQueryParams = async () => {
	try {
		const code = localStorage.getItem("oauthCode");
		const state = localStorage.getItem("oauthState");
		if (code && state) {
			const response = await fetch("/registration/oauthtwo_exchange_code_against_access_token", {
				method: "POST",
				headers: {
					"Content-Type": "application/json"
				},
				body: JSON.stringify({ code: code, state: state })
			});

			if (response.status === 200) {
				localStorage.removeItem("oauthCode");
				localStorage.removeItem("oauthState");
				return true;
			} else {
				throw new Error("Error exchanging code against access token");
			}
		} else {
			return false;
		}
	} catch (error) {
		console.error("Error checking query params: ", error.message);
		return false;
	}
}

const Router = {
	init: async () => {
		// adding event listeners
			// event handler for navigation links
		document.querySelectorAll("a.nav-link").forEach(a => {
			a.addEventListener("click", Router.handleNavLinks);
		});
			// event handler for url changes (back/forward)
		window.addEventListener("popstate", Router.handlePopstate);


		// !!! everything in this function below this line needs to stay at the bottom of the init function
		// !!! if not, the event listeners might not be added

		// check if the user is logged in
		if (location.pathname !== "/login" && location.pathname !== "/signup" && location.pathname !== "/forgot-password") {
			const tokenValid = await validateToken();
			const queryParamsValid = await checkQueryParams();
			if (!tokenValid && !queryParamsValid) {
				Router.go("/login", false);
				return;
			}
		}
		getUserData(); // not sure if it needs to be asked here too or if it will fix itself later on ??!!
		// TODO: we need to get profile image as well
		
		// check initial URL
		Router.go(location.pathname, false); // we push an initial state to the history in app.js
	},

	//opens the window.app.socket if it is closed
	makeWebSocket: (type) => {
		if (!window.app.socket) {
			let ws_scheme = window.location.protocol == "https:" ? "wss" : "ws"; // shouldn't it always be wss with ws-only i get a 400 bad request
			let ws_path = ws_scheme + '://' + window.location.host + "/daphne/tournament";
			window.app.socket = new WebSocket(ws_path);

			// add event listeners
			//window.app.socket.addEventListener("close", Router.handleSocketUnexpectedDisconnect);
			console.log("socket created");
		};

		window.app.socket.onopen = () => {
			console.log("socket opened");
			window.app.socket.send(JSON.stringify({"type": type, "displayname": window.app.userData.username}));
		};
	},

	/** closes the window.app.socket if it is open */
	closeWebSocket: () => {
		if (window.app.socket) {
			window.app.socket.onopen = null; // removes the onopen event handler (copilot says it prevents memory leaks)
			window.app.socket.close();
			window.app.socket = null;
			console.log("socket closed");
		}
	},

	//opens the window.app.pong_socket if it is closed
	/** creates a Websocket connection to backend using a match id */
	makePongWebSocket: () => {
		
		if (!window.app.pong_socket) {
			let ws_scheme = window.location.protocol == "https:" ? "wss" : "ws"; // shouldn't it always be wss with ws-only i get a 400 bad request
			let ws_path = ws_scheme + '://' + window.location.host + "/daphne/match";
			window.app.pong_socket = new WebSocket(ws_path);

			// add event listeners
			//window.app.pong_socket.addEventListener("close", Router.handleSocketUnexpectedDisconnect);
			console.log("pong socket created");
		};

		window.app.pong_socket.onopen = () => {
			console.log("pong socket opened");
			// NOTE: window.app.pong_socket.send(JSON.stringify({"type": type, "displayname": window.app.userData.username}));
		};
	},

	/** closes the window.app.pong_socket if it is open */
	closePongWebSocket: () => {
		if (window.app.pong_socket) {
			window.app.pong_socket.onopen = null; // removes the onopen event handler (copilot says it prevents memory leaks)
			window.app.pong_socket.close();
			window.app.pong_socket = null;
			console.log("pong socket closed");
		}
	},

	//opens the window.app.match_socket if it is closed
	/** creates a Websocket connection to backend using a match id */
	makeMatchWebSocket: () => {
		
		if (!window.app.match_socket) {
			let ws_scheme = window.location.protocol == "https:" ? "wss" : "ws"; // shouldn't it always be wss with ws-only i get a 400 bad request
			let ws_path = ws_scheme + '://' + window.location.host + "/daphne/matchmaking";
			window.app.match_socket = new WebSocket(ws_path);

			// add event listeners
			//window.app.match_socket.addEventListener("close", Router.handleSocketUnexpectedDisconnect);
			console.log("match socket created");
		};

		window.app.match_socket.onopen = () => {
			console.log("match socket opened");
			// NOTE: window.app.match_socket.send(JSON.stringify({"type": type, "displayname": window.app.userData.username}));
		};
	},

	/** closes the window.app.match_socket if it is open */
	closeMatchWebSocket: () => {
		if (window.app.match_socket) {
			window.app.match_socket.onopen = null; // removes the onopen event handler (copilot says it prevents memory leaks)
			window.app.match_socket.close();
			window.app.match_socket = null;
			console.log("match socket closed");
		}
	},

	//hides or shows the navbar and footer depending on the route
	hideOrShowNavbarAndFooter: (route) => {
		if (route === "/login" || route === "/signup" || route === "/displayname" || route === "/forgot-password" || route === "/tournament-lobby") {
			document.getElementById("navbar").style.display = "none";
			document.getElementById("footer").style.display = "none";
		}
		else {
			document.getElementById("navbar").style.display = "";
			document.getElementById("footer").style.display = "";
			if (window.app.userData.profileImage) {
				document.getElementById('userDropdown').src = window.app.userData.profileImage;
			} else {
				const response = fetch('/um/profile', { method: 'GET', headers: { 'Content-Type': 'application/json' } });
				response.then(data => data.json()).then(data => {
					if (data.image) {
						window.app.userData.profileImage = data.image;
						document.getElementById('userDropdown').src = data.image;
					}
				});
			}
		}
	},


	// changes the page main content and update the URL
	go: async (route, addToHistory = true, tournamentName = "") => { // the tournamentName is only needed for the tournamentLobbyPage
		console.log(`Going to ${route}`, " | addToHistory: ", addToHistory);
		let pageElement = null; // the new page element

		if (route !== "/login" && route !== "/signup" && route !== "/forgot-password") {
			const tokenValid = await validateToken();
			if (!tokenValid) {
				route = "/login";
				addToHistory = false;
			}
		} else {
			app.userData = {};
			localStorage.removeItem("userData");
		}

		Router.hideOrShowNavbarAndFooter(route);

		// check for external links maybe??!! (if first character is not a slash)

		// create the new page element depending on the route
		switch (route) {
			case "/":
				pageElement = document.createElement("play-menu-home-page");
				break;
			case "/tournament":
				if (addToHistory === true) {
					Router.closeWebSocket(); //only closes the socket if it is open
					Router.makeWebSocket("on_tournament_page");
				}
				pageElement = document.createElement("join-tournament-page");
				break;
			case "/tournament-lobby":
				//protection (what if the socket is not open??!!!!)
				Router.closePongWebSocket(); //only closes the socket if it is open
				Router.makePongWebSocket();
				pageElement = new TournamentLobbyPage(tournamentName);
				break;
			case "/match":
				console.log("match page created");
				Router.closePongWebSocket(); //only closes the socket if it is open
				Router.makePongWebSocket();
				Router.closeMatchWebSocket(); //only closes the socket if it is open
				Router.makeMatchWebSocket();
				pageElement = document.createElement("match-page");
				break;
			case "/pong": // needed??!!!
				pageElement = document.createElement("pong-page");
				pageElement.innerHTML = "Pong Game";
				break;
			case "/login":
				pageElement = document.createElement("login-page");
				break;
			case "/signup":
				pageElement = document.createElement("signup-page");
				break;
			case "/forgot-password":
				pageElement = document.createElement("forgot-password");
				break;
			case "/displayname":
				pageElement = document.createElement("select-displayname-page");
				break;
			case "/friends":
				const fragment = document.createDocumentFragment();
				fragment.appendChild(document.createElement("friend-list"));
				fragment.appendChild(document.createElement("friend-search"));
				pageElement = fragment;
				console.log("friends page created");
				break;
			case "/logout":
				//TODO: add API call to registration/logout endpoint
				//redirect to login page
				route = "/login";
				break;
			default:
				// homepage
				pageElement = document.createElement("play-menu-home-page");
				route = "/";
				console.log("default in router");
				break;
		}
		if (pageElement) {
			document.querySelector("main").innerHTML = ""; //empty main the quick and dirty way
			document.querySelector("main").appendChild(pageElement); //append the new element
			// scroll to top
			window.scrollX = 0;
			window.scrollY = 0;
		}

		// close websocket if we leave tournament pages
		if (!route.startsWith("/tournament") && !route.startsWith("/match") && !route.startsWith("/pong")) { // pong needed??!!!
			Router.closeWebSocket(); // checks if the socket is open before closing
		}
		if (route !== "/tournament-lobby" && route !== "/match") {
			Router.closePongWebSocket();
		}

		// adds the route to the history, so the back/forward buttons work
		if (addToHistory)
			history.pushState({route}, "", route);
	},


	/// ----- Event Handlers ----- ///

	handleNavLinks(event) {
		event.preventDefault();
				
		const url = event.target.getAttribute("href");
		Router.go(url);
	},

	handlePopstate(event) {
		event.preventDefault();
		Router.go(event.state.route, false);
	},

	// !!! when the socket closes normally, you also get sent to the home page
	/** You get sent back to the home poge in case the Socket disconnects unexpectedly */
	/* handleSocketUnexpectedDisconnect(event) {
		console.log("socket unexpectdedly disconnected");
		Router.go("/");
	} */
}

export default Router;
