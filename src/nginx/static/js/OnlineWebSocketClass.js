export class OnlineWebSocketClass {
	constructor () {
		this.socket = null;
		this.online_friends = [];
	}

	addEventListeners () {
		this.socket.addEventListener("message", this.handleReceivedMessage); // probably need to bind this !!

	}

	removeEventListeners () {
		this.socket.removeEventListener("message", this.handleReceivedMessage); // probably need to bind this !!
	}

	//opens the window.app.socket if it is closed
	make (endpoint) {
		//if (!window.app.socket) { // needs to happen one level up !!!
			let ws_scheme = window.location.protocol == "https:" ? "wss" : "ws"; // shouldn't it always be wss with ws-only i get a 400 bad request
			let ws_path = ws_scheme + '://' + window.location.host + endpoint;
			this.socket = new WebSocket(ws_path);

			// add event listeners
			this.addEventListeners();
			//this.socket.addEventListener("close", Router.handleSocketUnexpectedDisconnect); // do we need to make an extra function for unexpected disconnect ???!!!
			console.log("socket created");
		//};

		this.socket.onopen = () => {
			console.log("socket opened");
		};
	}

	/** closes the this.socket if it is open */
	close () {
		if (this.socket) {
			this.removeEventListeners();
			this.socket.onopen = null; // removes the onopen event handler (copilot says it prevents memory leaks)
			this.socket.close();
			this.socket = null;
			console.log("socket closed");
		}
	}


	/// ----- Event Handlers ----- ///

	/** gets called when the websocket receives a message */
	handleReceivedMessage(event) {
		const data = JSON.parse(event.data);
		console.log("OnlineWebSocket: handleReceivedMessage: ", data);
				
		if (data.type === "online_status") {
		}
		else if (data.type === "error") {
			console.error("Error: handleReceivedMessage: ", data.error);
		}
		else {
			console.error("Error: handleReceivedMessage: unknown type: ", data.type);
		}
	}
}