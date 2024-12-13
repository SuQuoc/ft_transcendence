export class OnlineWebSocketClass {
	constructor () {
		this.socket = null;
		this.online_friends = [];
	}

	addEventListeners () {
		console.log("this: add event listener: ", this);
		this.socket.addEventListener("message", this.handleReceivedMessage.bind(this)); // probably need to bind this !!

	}

	removeEventListeners () {
		console.log("this: remove event listener: ", this);
		this.socket.removeEventListener("message", this.handleReceivedMessage.bind(this)); // probably need to bind this !!
	}

	/** opens the window.app.socket if it is closed */
	make (endpoint) {
		if (!this.socket) {
			let ws_scheme = window.location.protocol == "https:" ? "wss" : "ws"; // shouldn't it always be wss with ws-only i get a 400 bad request
			let ws_path = ws_scheme + '://' + window.location.host + endpoint;
			this.socket = new WebSocket(ws_path);

			// add event listeners
			console.log("this: add event listener: ", this);
			this.addEventListeners();
			//this.socket.addEventListener("close", Router.handleSocketUnexpectedDisconnect); // do we need to make an extra function for unexpected disconnect ???!!!
			console.log("socket created");
		};

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


	friendWentOnline (friend_id) {
		this.online_friends.push(friend_id);
	}

	friendWentOffline (friend_id) {
		const index = this.online_friends.indexOf(friend_id);
		if (index > -1) {
			this.online_friends.splice(index, 1);
		}
	}


	/// ----- Event Handlers ----- ///

	/** gets called when the websocket receives a message */
	handleReceivedMessage(event) {
		//console.log("OnlineWebSocket: handleReceivedMessage: ", event);
		const data = JSON.parse(event.data);
		console.log("OnlineWebSocket: handleReceivedMessage: ", data);
				
		if (data.type === "online_status") {
			if (data.status === "online") {
				this.friendWentOnline(data.sender_id);
			}
			else if (data.status === "offline") {
				this.friendWentOffline(data.sender_id);
			}
		}
		else if (data.type === "error") {
			console.error("Error: handleReceivedMessage: ", data.error);
		}
		else {
			console.error("Error: handleReceivedMessage: unknown type: ", data.type);
		}
	}
}