const Router = {
	init: () => {
		document.querySelectorAll("a").forEach(a => { // maybe we should select a.nav-links instead, but it should work this way as well
			a.addEventListener("click", (event) => {
				event.preventDefault();
				console.log("link clicked");
				
				const url = event.target.getAttribute("href");
				Router.go(url);
			});
		});

		// event handler for url changes (back/forward)
		window.addEventListener("popstate", (event) => {
			console.log("popstate event");
			event.preventDefault(); // not sure if needed
			Router.go(event.state.route, false);
		});

		// Listen for custom events from shadow DOMs
        document.addEventListener("change-route-custom-event", (event) => {
            const url = event.detail.url;
            Router.go(url);
        });

		// somewhere here we should check if the user is logged in and redirect to the login page if not
		// load event can be used to listen for initial page load. Don't know if it has the right timing here though
		
		// check initial URL
		Router.go(location.pathname);
	},


	/** opens the window.app.socket if it is closed */
	makeWebSocket: () => {
		if (!window.app.socket) {
			let ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
			let ws_path = ws_scheme + '://' + window.location.host + "/daphne/pong/" + "tournaments" + "/";
			window.app.socket = new WebSocket(ws_path);
			console.log("socket created");
		};

		// does it make sense to have this here??
		window.app.socket.onopen = () => {
			window.app.socket.send(JSON.stringify({"type": "newClient", "user_id": "123456"}));
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

	// changes the page main content and update the URL
	go: (route, addToHistory = true) => {
		console.log(`Going to ${route}`);
		let pageElement = null; // the new page element

		// adds the route to the history, so the back/forward buttons work
		if (addToHistory) {
			history.pushState({route}, "", route);
		}

		// show/hide navbar and footer (not happy, maybe there is a better solution!?)
		if (route === "/login" || route === "/signup") {
			document.getElementById("navbar").style.display = "none";
			document.getElementById("footer").style.display = "none";
			console.log("hide navbar and footer");
		}
		else {
			document.getElementById("navbar").style.display = "";
			document.getElementById("footer").style.display = "";
		}

		// check for external links maybe??!! (if first character is not a slash)

		// create the new page element depending on the route
		switch (route) {
			case "/":
				//Router.closeWebSocket();
				pageElement = document.createElement("play-menu-home-page");
				break;
			case "/play":
				//Router.closeWebSocket();
				pageElement = document.createElement("h1");
				pageElement.textContent = "Play";
				break;
			case "/tournament":
				Router.makeWebSocket();
				pageElement = document.createElement("join-tournament-page");
				break;
			case "/tournament-lobby":
				Router.makeWebSocket();
				pageElement = document.createElement("tournament-lobby-page");
				break;
			case "/login":
				//Router.closeWebSocket();
				pageElement = document.createElement("login-page");
				break;
			case "/signup":
				//Router.closeWebSocket();
				pageElement = document.createElement("signup-page");
				break;
			default:
				// homepage
				//Router.closeWebSocket();
				pageElement = document.createElement("play-menu-home-page");
				console.log("default in router");
				break;
		}
		if (pageElement) {
			document.querySelector("main").innerHTML = ""; //empty main the quick and dirty way
			document.querySelector("main").appendChild(pageElement); //append the new element
			// scroll to top
			window.scrollX = 0;
			window.scrollY = 0;

			// close websocket if we leave tournament pages
			if (route != "/tournament" && route != "/tournament-lobby") {
				Router.closeWebSocket(); // checks if the socket is open before closing
			}
		}
	}
}

export default Router;