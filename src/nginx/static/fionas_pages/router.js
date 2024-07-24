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
			case "/":
				pageElement = document.createElement("h1");
				pageElement.textContent = "Home";
				break;
			case "/play":
				pageElement = document.createElement("h1");
				pageElement.textContent = "Play";
				break;
		}
		if (pageElement) {
			document.querySelector("main").innerHTML = ""; //empty main
			document.querySelector("main").appendChild(pageElement); //append the new element
			// scroll to top
			window.scrollX = 0;
			window.scrollY = 0;
		}
	}
}

export default Router;