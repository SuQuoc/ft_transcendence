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
			throw new Error("Token is invalid");
		}

		return true;
	} catch (error) {
		console.error("Error validating token: ", error.message);

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
const getDisplayname = async () => {
	if (window.app.userData.username) // if the displayname is already set we don't need to fetch it
		return;

	try {
		// Check if the user already has a displayname
		const response = await fetch ('/um/profile/', {
			method: 'GET',
			headers: {
				'Content-Type': 'application/json'
			}
		});
		
		// Redirects to the home page if the user already has a displayname or to the select displayname page if they don't
		if (!response.ok) {
			window.app.router.go('/displayname', false);
			console.log('displayname not ok:', response);
		} else {
			const responseData = await response.json();
			window.app.userData.username = responseData.displayname;
			//window.app.userData.<image?> = responseData.image;
			app.router.go('/', false); // maybe this should be set to false?
		}
	} catch (error) {
		console.error('Error getting displayname (router):', error);
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
		if (location.pathname !== "/login" && location.pathname !== "/signup") {
			const tokenValid = await validateToken();
			if (!tokenValid) {
				Router.go("/login", false);
				return;
			}
		}
		getDisplayname(); // not sure if it needs to be asked here too or if it will fix itself later on ??!!
		// TODO: we need to get email and profile image as well
		
		// check initial URL
		Router.go(location.pathname, false); // we push an initial state to the history in app.js
	},

	//opens the window.app.socket if it is closed
	makeWebSocket: (type) => {
		let channel_name = "tournament";

		if (type === "onFindOpponentPage")
			channel_name = "match";

		if (!window.app.socket) {
			let ws_scheme = window.location.protocol == "https:" ? "wss" : "ws"; // shouldnt it always be wss with ws only i get a 400 bad request
			// comment old version let ws_path = ws_scheme + '://' + window.location.host + "/daphne/pong/" + channel_name + "/";
			let ws_path = ws_scheme + '://' + window.location.host + "/daphne/lobbies";
			window.app.socket = new WebSocket(ws_path);

			// add event listeners
			//window.app.socket.addEventListener("close", Router.handleSocketUnexpectedDisconnect);
			console.log("socket created");
		};

		window.app.socket.onopen = () => {
			window.app.socket.send(JSON.stringify({"type": type, "displayname": window.app.userData.username}));
			window.app.socket.send(JSON.stringify({"type": "getTournamentList"}));
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

	//hides or shows the navbar and footer depending on the route
	hideOrShowNavbarAndFooter: (route) => {
		if (route === "/login" || route === "/signup" || route === "/displayname") {
			document.getElementById("navbar").style.display = "none";
			document.getElementById("footer").style.display = "none";
		}
		else {
			document.getElementById("navbar").style.display = "";
			document.getElementById("footer").style.display = "";
		}
	},


	// changes the page main content and update the URL
	go: async (route, addToHistory = true) => {
		console.log(`Going to ${route}`, " | addToHistory: ", addToHistory);
		let pageElement = null; // the new page element

		//comment out to add token check
		if (route !== "/login" && route !== "/signup") {
			const tokenValid = await validateToken();
			if (!tokenValid) {
				route = "/login";
				addToHistory = false;
			}
		}

		Router.hideOrShowNavbarAndFooter(route);

		// check for external links maybe??!! (if first character is not a slash)

		// create the new page element depending on the route
		switch (route) {
			case "/":
				pageElement = document.createElement("play-menu-home-page");
				break;
			case "/tournament":
				Router.closeWebSocket(); //only closes the socket if it is open
				Router.makeWebSocket("onTournamentPage");
				pageElement = document.createElement("join-tournament-page");
				break;
			case "/tournament-lobby":
				//protection (what if the socket is not open??!!!!)
				pageElement = document.createElement("tournament-lobby-page");
				break;
			case "/tournament-waiting-room":
				//protection (what if the socket is not open??!!!!)
				pageElement = document.createElement("tournament-waiting-room-page");
				break;
			case "/match":
				console.log("match page created");
				Router.closeWebSocket(); //only closes the socket if it is open
				Router.makeWebSocket("onFindOpponentPage");
				pageElement = document.createElement("find-opponent-page");
				break;
			case "/pong":
				pageElement = document.createElement("pong-page");
				pageElement.innerHTML = "Pong Game";
				break;
			case "/login":
				pageElement = document.createElement("login-page");
				break;
			case "/signup":
				pageElement = document.createElement("signup-page");
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
		if (!route.startsWith("/tournament") && !route.startsWith("/match") && !route.startsWith("/pong")) {
			Router.closeWebSocket(); // checks if the socket is open before closing
		}

		// adds the route to the history, so the back/forward buttons work
		if (addToHistory)
			history.pushState({route}, "", route);
	},


	/// ----- Event Handlers ----- ///

	/** !!! Use this only with the "once" option when adding the Event Listener !!!
	 * 
	 *  Add this as a "message" event listener to window.app.socket.
	 *  It changes the route (page) depending on the message received from the server */
	handleSocketMessageChangeRoute(event) {
		const data = JSON.parse(event.data);

		switch (data.type) {
			case "joinTournament":
				if (data.joined === "true")
					Router.go("/tournament-lobby", false); // false means it doesn't get added to the history
				else
					Router.go("/tournament", false); // should probably be false ??
				break;
			default:
				console.log("unknown message type: ", data.type);
				break;
		}
	},

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