import { TournamentLobbyPage } from "./js/TournamentLobbyPage.js";

const validateToken = async () => {
	try {
		// check if the token is valid
		const response = await fetch("/registration/verify_token", {
			method: "GET",
			headers: {
				"Content-Type": "application/json",
			},
			credentials: "include",
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
					"Content-Type": "application/json",
				},
				credentials: "include",
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
};

/** Checks if the displayname is already set. If not it asks the um server for it and if the user hasn't chosen one yet, they get reroutet to /display */
const getUserData = async () => {
	if (window.app.userData.username && window.app.userData.profileImage)
		// if the displayname is already set we don't need to fetch it
		return;

	try {
		// Check if the user already has a displayname
		const response = await fetch("/um/profile", {
			method: "GET",
			headers: {
				"Content-Type": "application/json",
			},
		});

		// Redirects to the home page if the user already has a displayname or to the select displayname page if they don't
		if (!response.ok) {
			window.app.router.go("/displayname", false);
		} else {
			const responseData = await response.json();
			window.app.userData.username = responseData.displayname;
			window.app.userData.profileImage = responseData.image;
			app.router.go("/", false);
		}
	} catch (error) {
		console.error("Error getting userdata (router):", error);
	}
};

const checkQueryParams = async () => {
	try {
		const code = localStorage.getItem("oauthCode");
		const state = localStorage.getItem("oauthState");
		if (code && state) {
			const response = await fetch(
				"/registration/oauthtwo_exchange_code_against_access_token",
				{
					method: "POST",
					headers: {
						"Content-Type": "application/json",
					},
					body: JSON.stringify({ code: code, state: state }),
				}
			);

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
};

const Router = {
	init: async () => {
		// adding event listeners
		// event handler for navigation links
		document.querySelectorAll("a.nav-link").forEach((a) => {
			a.addEventListener("click", Router.handleNavLinks);
			a.addEventListener("keydown", Router.handleNavLinkKeydown);
		});
		// event handler for url changes (back/forward)
		window.addEventListener("popstate", Router.handlePopstate);

		// !!! everything in this function below this line needs to stay at the bottom of the init function
		// !!! if not, the event listeners might not be added

		// check if the user is logged in
		if (
			location.pathname !== "/login" &&
			location.pathname !== "/signup" &&
			location.pathname !== "/forgot-password"
		) {
			const tokenValid = await validateToken();
			const queryParamsValid = await checkQueryParams();
			if (!tokenValid && !queryParamsValid) {
				Router.go("/login", false);
				return;
			}
		}
		getUserData();

		// check initial URL
		Router.go(location.pathname, false); // we push an initial state to the history in app.js
	},

	/** Opens and returns a new websocket if the one passed is closed. If it isn't, it is returned instead. */
	makeWebSocket: (socket, endpoint) => {
		if (socket)
			return socket;
		let ws_scheme = window.location.protocol == "https:" ? "wss" : "ws"; // shouldn't it always be wss with ws-only i get a 400 bad request
		let ws_path = ws_scheme + "://" + window.location.host + endpoint;
		let new_socket = new WebSocket(ws_path);

		// add event listeners
		console.log("socket created");

		new_socket.onopen = () => {
			console.log("socket opened");
		};
		return new_socket;
	},

	/** Closes the socket if it is open.
	 *
	 * Returns null. */
	closeWebSocket: (socket) => {
		// function name should be changed
		if (socket) {
			socket.onopen = null; // removes the onopen event handler (copilot says it prevents memory leaks)
			socket.close();
			console.log("socket closed");
		}
		return null;
	},

	//hides or shows the navbar and footer depending on the route
	hideOrShowNavbarAndFooter: (route) => {
		if (
			route === "/login" ||
			route === "/signup" ||
			route === "/displayname" ||
			route === "/forgot-password" ||
			route === "/tournament-lobby"
		) {
			document.getElementById("navbar").style.display = "none";
			document.getElementById("footer").style.display = "none";
		} else {
			document.getElementById("navbar").style.display = "";
			document.getElementById("footer").style.display = "";
			if (window.app.userData.profileImage) {
				document.getElementById("userProfileButton").src =
					window.app.userData.profileImage;
			} else {
				const response = fetch("/um/profile", {
					method: "GET",
					headers: { "Content-Type": "application/json" },
				});
				response
					.then((data) => data.json())
					.then((data) => {
						if (data.image) {
							window.app.userData.profileImage = data.image;
							document.getElementById("userProfileButton").src = data.image;
						}
					});
			}
		}
	},

	// changes the page main content and update the URL
	go: async (route, addToHistory = true, tournamentName = "") => {
		// the tournamentName is only needed for the tournamentLobbyPage
		console.log(`Going to ${route}`, " | addToHistory: ", addToHistory);
		let pageElement = null; // the new page element

		if (route !== "/login" && route !== "/signup" && route !== "/forgot-password") {
			const tokenValid = await validateToken();
			if (!tokenValid) {
				window.app.online_socket.close();
				route = "/login";
				addToHistory = false;
			}
			window.app.online_socket.make("/um/online_status/");
		} else {
			window.app.online_socket.close();
			app.userData = {};
			localStorage.removeItem("userData");
			
			// closing the user profile so it's gone when you get to the home page again
			const closeButton = document.getElementById("userProfileClose");
			if (closeButton)
				closeButton.click();
		}

		Router.hideOrShowNavbarAndFooter(route);

		// create the new page element depending on the route
		switch (route) {
			case "/":
				pageElement = document.createElement("play-menu-home-page");
				break;
			case "/tournament":
				if (addToHistory === true) {
					window.app.socket = Router.closeWebSocket(window.app.socket);
					window.app.socket = Router.makeWebSocket(window.app.socket, "/game/tournament");
				}
				pageElement = document.createElement("join-tournament-page");
				break; 
			case "/tournament-lobby":
				window.app.pong_socket = Router.closeWebSocket(window.app.pong_socket);
				window.app.pong_socket = Router.makeWebSocket(window.app.pong_socket, "/game/match");
				pageElement = new TournamentLobbyPage(tournamentName);
				break;
			case "/match":
				console.log("match page created");
				window.app.pong_socket = Router.closeWebSocket(window.app.pong_socket);
				window.app.pong_socket = Router.makeWebSocket(window.app.pong_socket, "/game/match");
				window.app.match_socket = Router.closeWebSocket(window.app.match_socket);
				window.app.match_socket = Router.makeWebSocket(window.app.match_socket, "/game/matchmaking/");
				pageElement = document.createElement("match-page");
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
			case "/stats":
				pageElement = document.createElement("statistics-page");
				break;
			case "/friends":
				const fragment = document.createDocumentFragment();
				fragment.appendChild(document.createElement("friend-list"));
				fragment.appendChild(document.createElement("friend-search"));
				pageElement = fragment;
				console.log("friends page created");
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
		if (!route.startsWith("/tournament") && !route.startsWith("/match")) {
			window.app.socket = Router.closeWebSocket(window.app.socket); // checks if the socket is open before closing
		}
		if (route !== "/tournament-lobby" && route !== "/match") {
			window.app.pong_socket = Router.closeWebSocket(window.app.pong_socket);
		}
		if (route !== "/match") {
			window.app.match_socket = Router.closeWebSocket(window.app.match_socket);
		}

		// adds the route to the history, so the back/forward buttons work
		if (addToHistory) history.pushState({ route }, "", route);
	},

	/// ----- Event Handlers ----- ///

	handleNavLinks(event) {
		event.preventDefault();

		const url = event.target.getAttribute("href");
		Router.go(url);
	},

	handleNavLinkKeydown(event) {
		if (event.key === "Enter" || event.key === " ") {
			event.preventDefault();
			const url = event.target.getAttribute("href");
			Router.go(url);
		}
	},

	handlePopstate(event) {
		event.preventDefault();
		Router.go(event.state.route, false);
	},
};

export default Router;
