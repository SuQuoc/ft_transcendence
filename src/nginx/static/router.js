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

		if (!response.status !== 200) {
			throw new Error("Error verifying token");
		}
		return true;
	} catch (error) {
		console.error("Error validating token:", error.message);
		return false;
	}
}

const Router = {
	init: () => {
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
		Router.go(location.pathname);
	},

	//opens the window.app.socket if it is closed
	makeWebSocket: (type) => {
		if (!window.app.socket) {
			let ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
			let ws_path = ws_scheme + '://' + window.location.host + "/daphne/pong/" + "tournaments" + "/";
			window.app.socket = new WebSocket(ws_path);
			console.log("socket created");
		};

		// does it make sense to have this here??
		window.app.socket.onopen = () => {
			window.app.socket.send(JSON.stringify({"type": type, "user_id": "123456"}));
		};
	},

	//closes the window.app.socket if it is open
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
	go: (route, addToHistory = true) => {
		console.log(`Going to ${route}`);
		let pageElement = null; // the new page element

		//comment out to add token check
		/*
		const tokenValid = await validateToken();

		if (!tokenValid && route !== "/login" && route !== "/signup") {
			route = "/login";
		}
		*/
		
		Router.hideOrShowNavbarAndFooter(route);

		// check for external links maybe??!! (if first character is not a slash)

		// create the new page element depending on the route
		switch (route) {
			case "/":
				pageElement = document.createElement("play-menu-home-page");
				break;
				case "/play":
				pageElement = document.createElement("h1");
				pageElement.textContent = "Play";
				break;
			case "/tournament":
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
		if (!route.startsWith("/tournament")) {
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
					Router.go("/tournament-lobby");
				else
					Router.go("/tournament");
				break;
			default:
				console.log("unknown message type: ", data.type);
				break;
		}
	}
}

export default Router;