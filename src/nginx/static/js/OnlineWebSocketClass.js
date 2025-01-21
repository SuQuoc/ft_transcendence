export class OnlineWebSocketClass {
	constructor () {
		this.socket = null;
		this.online_friends = [];
		this.handleReceivedMessage_var = this.handleReceivedMessage.bind(this);
	}

	addEventListeners () {
		console.log("this: add event listener: ", this);
		this.socket.addEventListener("message", this.handleReceivedMessage_var);
	}

	removeEventListeners () {
		console.log("this: remove event listener: ", this);
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
			console.log("ONLINE socket created");
		};

		this.socket.onopen = () => {
			console.log("ONLINE socket opened");
		};
	}

	/** closes the this.socket if it is open */
	close () {
		if (this.socket) {
			this.removeEventListeners();
			this.socket.onopen = null; // removes the onopen event handler (copilot says it prevents memory leaks)
			this.socket.close();
			this.socket = null;
			console.log("ONLINE socket closed");
		}
	}


	friendWentOnline (friend_id) {
		this.online_friends.push(friend_id);
		console.log("friend went online socket class: friends: ", this.online_friends);
	}

	friendWentOffline (friend_id) {
		const index = this.online_friends.indexOf(friend_id);
		if (index > -1) {
			this.online_friends.splice(index, 1);
		}
		console.log("friend went offline socket class: friends: ", this.online_friends);
	}


	/// ----- Event Handlers ----- ///

	/** gets called when the websocket receives a message */
	handleReceivedMessage (event) {
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