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
        document.addEventListener("change-route-from-shadow", (event) => {
            const url = event.detail.url;
            Router.go(url);
        });

		// somewhere here we should check if the user is logged in and redirect to the login page if not
		// load event can be used to listen for initial page load. Don't know if it has the right timing here though
		
		// check initial URL
		Router.go(location.pathname);
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
				pageElement = document.createElement("join-tournament-page");
				break;
			case "/login":
				pageElement = document.createElement("login-page");
				console.log("login page created");
				break;
			case "/signup":
				pageElement = document.createElement("signup-page");
				console.log("signup page created");
				break;
			case "/friends":
				pageElement = document.createElement("friends-list");
				pageElement.setAttribute("requested", "");
				console.log("friends list created");
				break;
			default:
				// homepage
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
		}
	}
}

export default Router;