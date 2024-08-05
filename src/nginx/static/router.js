const Router = {
	init: () => {
		document.querySelectorAll("a").forEach(a => { // maybe we should select a.nav-links instead, but it should work this way as well
			a.addEventListener("click", event => {
				event.preventDefault();
				console.log("link clicked");
				
				const url = event.target.getAttribute("href");
				Router.go(url);
			});
		});

		// event handler for url changes (back/forward)
		window.addEventListener("popstate", event => {
			Router.go(event.state.route, false);
		});

		// somewhere here we should check if the user is logged in and redirect to the login page if not
		
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

		// show/hide navbar and footer (not happy, maybe there is a better solution)
	/* 	if (route === "/login" || route === "/signup") {
			document.getElementById("navbar").style.display = "none";
			document.getElementById("footer").style.display = "none";
			console.log("hide navbar and footer");
		}
		else {
			document.getElementById("navbar").style.display = "";
			document.getElementById("footer").style.display = "";
		} */


		// create the new page element depending on the route
		switch (route) {
			case "/":
				pageElement = document.createElement("play-menu");
				break;
			case "/play":
				pageElement = document.createElement("h1");
				pageElement.textContent = "Play";
				break;
			case "/user":
				pageElement = document.createElement("h1");
				pageElement.textContent = "User";
				break;
			case "/login":
				pageElement = document.createElement("login-page");
				console.log("login page created");
				break;
			case "/signup":
				pageElement = document.createElement("signup-page");
				console.log("signup page created");
				break;
			default:
				// homepage
				pageElement = document.createElement("play-menu");
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