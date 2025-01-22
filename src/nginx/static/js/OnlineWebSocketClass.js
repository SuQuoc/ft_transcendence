export class OnlineWebSocketClass {
	constructor () {
		this.socket = null;
		this.online_friends = [];
		this.handleReceivedMessage_var = this.handleReceivedMessage.bind(this);
	}

	addEventListeners () {
		this.socket.addEventListener("message", this.handleReceivedMessage_var);
	}

	removeEventListeners () {
		this.socket.removeEventListener("message", this.handleReceivedMessage_var);
	}

	/** opens the window.app.socket if it is closed */
	make (endpoint) {
		if (!this.socket) {
			let ws_scheme = "wss";
			let ws_path = ws_scheme + '://' + window.location.host + endpoint;
			this.socket = new WebSocket(ws_path);

			// add event listeners
			this.addEventListeners();
		};
	}

	/** closes the this.socket if it is open */
	close () {
		if (this.socket) {
			this.removeEventListeners();
			this.socket.close();
			this.socket = null;
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
	handleReceivedMessage (event) {
		const data = JSON.parse(event.data);
				
		if (data.type === "online_status") {
			if (data.status === "online") {
				this.friendWentOnline(data.sender_id);
			}
			else if (data.status === "offline") {
				this.friendWentOffline(data.sender_id);
			}
		}
		else {
			console.error("Error: handleReceivedMessage: unknown type: ", data.type);
		}
	}
}