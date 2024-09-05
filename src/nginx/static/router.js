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

const Router = {
	init: async () => {
		// check if the user is logged in
		if (location.pathname !== "/login" && location.pathname !== "/signup") {
			const tokenValid = await validateToken();
			if (!tokenValid) {
				Router.go("/login", false);
				return;
			}
		}
		document.querySelectorAll("a").forEach(a => { // maybe we should select a.nav-links instead, but it should work this way as well
			a.addEventListener("click", (event) => {
				event.preventDefault();
				
				const url = event.target.getAttribute("href");
				Router.go(url);
			});
		});

		// event handler for url changes (back/forward)
		window.addEventListener("popstate", (event) => {
			event.preventDefault(); // not sure if needed
			Router.go(event.state.route, false);
		});

		// somewhere here we should check if the user is logged in and redirect to the login page if not
		// load event can be used to listen for initial page load. Don't know if it has the right timing here though
		
		// check initial URL
		Router.go(location.pathname, false); // we push an initial state to the history in app.js
	},

	//opens the window.app.socket if it is closed
	makeWebSocket: (type) => {
		let channel_name = "tournament";

		if (type === "onFindOpponentPage")
			channel_name = "match";

		if (!window.app.socket) {
			let ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
			let ws_path = ws_scheme + '://' + window.location.host + "/daphne/pong/" + channel_name + "/";
			window.app.socket = new WebSocket(ws_path);

			// add event listeners
			//window.app.socket.addEventListener("close", Router.handleSocketUnexpectedDisconnect);
			console.log("socket created");
		};

		window.app.socket.onopen = () => {
			window.app.socket.send(JSON.stringify({"type": type, "user_id": window.app.userData.username}));
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
		if (route === "/login" || route === "/signup") {
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
			case "/tournament-waiting-room": // TODO: shouldn't log to history!!!!!
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
		console.log("history: ", history);
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
					Router.go("/tournament");
				break;
			default:
				console.log("unknown message type: ", data.type);
				break;
		}
	},


	// !!! when the socket closes normally, you also get sent to the home page
	/** You get sent back to the home poge in case the Socket disconnects unexpectedly */
	/* handleSocketUnexpectedDisconnect(event) {
		console.log("socket unexpectdedly disconnected");
		Router.go("/");
	} */
}

export default Router;