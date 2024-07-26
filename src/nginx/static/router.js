const Router = {
	init: () => {
		document.querySelectorAll("a.nav-link").forEach(a => {
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

		// check initial URL
		Router.go(location.pathname);
	},

	// changes the page main content and update the URL
	go: (route, addToHistory = true) => {
		console.log(`Going to ${route}`);
		let pageElement = null; // the new page element

		// 
		if (addToHistory) {
			history.pushState({route}, "", route);
		}
		// create the new page element depending on the route
		switch (route) {
			case "/prototypes/template.html":
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
			default:
				// homepage
				pageElement = document.createElement("play-menu");
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