import { ComponentBaseClass } from "./componentBaseClass.js";

export class FriendList extends ComponentBaseClass {
	static get observedAttributes() {
		return ['friends', 'requested', 'received'];
	}

	constructor() {
		super();

		this.friends = [];
		this.requested = [];
		this.search = [];
	}

	getElementHTML() {
		const template = document.createElement('template');
		template.innerHTML = `
			<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH" crossorigin="anonymous">
  			<style>
				.friend-status {
					display: inline-block;
					width: 10px;
					height: 10px;
					border-radius: 50%;
					position: absolute;
					bottom: 0;
					right: 0;
				}
				.online {
					background-color: green;
				}
				.offline {
					background-color: lightgray;
					border: 1px solid gray;
				}
				.friend-img-container {
					width: 40px;
					height: 40px;
					margin-right: 10px;
					position: relative;
				}
				.friend-img {
					width: 40px;
					height: 40px;
					border-radius: 50%;
				}
				.btn {
					margin-right: 0.25rem;
				}
			</style>
			<div class="container">
				<div class="row">
				<div class="col">
					<h4 id="title"></h4>
					<ul class="list-group" id="list"></ul>
				</div>
				</div>
			</div>`
	}

	connectedCallback() {
		super.connectedCallback();

		this.fetchFriendList();
	}

	attributeChangedCallback(name, oldValue, newValue) {
		if (oldValue !== newValue) {
		  this.fetchFriendList();
		}
	}
	
	updateFriends({titleElement, listElement}) {
		titleElement.textContent = 'Friends';
		if (this.friends.length < 1) {
			const item = document.createElement('li');
			item.className = 'list-group-item d-flex align-items-center';
			item.innerHTML = `<span class="text-muted">No friends yet</span>`
			listElement.appendChild(item);
			return;
		}
		this.friends.map(friend => {
			const item = document.createElement('li');
			item.className = 'list-group-item d-flex align-items-center';
			item.innerHTML = `
				<button class="btn btn-danger btn-sm">X</button>
				<div class="friend-img-container">
					<img src="${friend.imgURL}" alt="Profile image of ${friend.displayname}" class="friend-img">
					<span class="friend-status ${friend.onlinestatus ? 'online' : 'offline'}"></span>
				</div>
				<span>${friend.displayname}</span>
			`;
			item.querySelector('button').addEventListener('click', () => {
				//TODO: add API call to remove friend request
				listElement.removeChild(item);
			});
			listElement.appendChild(item);
		});
	}
	
	updateRequested({titleElement, listElement}) {
		titleElement.textContent = 'Friend Requests';
		this.received.map(user => {
		  const item = document.createElement('li');
		  item.className = 'list-group-item d-flex justify-content-between align-items-center';
		  item.innerHTML = `
			  <button class="btn btn-success btn-sm">✓</button>
			  <button class="btn btn-danger btn-sm">X</button>
			  <span>${user.displayname}</span>`;
		  item.querySelector('button.btn-success').addEventListener('click', () => {
			//TODO: add API call to accept friend request, include to friend list
			listElement.removeChild(item);
		  });
		  item.querySelector('button.btn-danger').addEventListener('click', () => {
			//TODO: add API call to remove friend request
			listElement.removeChild(item);
		  });
		  listElement.appendChild(item);
		});
		this.requested.map(request => {
			const item = document.createElement('li');
			item.className = 'list-group-item d-flex justify-content-between align-items-center';
			item.innerHTML = `
				<button class="btn btn-danger btn-sm">X</button>
				<span>${request.displayname}</span>
			`;
			item.querySelector('button').addEventListener('click', () => {
				//TODO: add API call to remove friend request
				listElement.removeChild(item);
			});
			listElement.appendChild(item);
		});
	}
	
	async fetchFriendList() {
		try {
			//substitute with endpoint instead of dummy JSON
			const response = await fetch('./getfriendlist.json');
			const data = await response.json();
			this.friends = data[0].friends;
			this.requested = data[0].requested;
			this.received = data[0].received;
			/*
			this.friends = dummyData[0].friends;
			this.requested = dummyData[0].requested;
			this.received = dummyData[0].received;
			*/
			this.updateList();
		} catch (e) {
		  	console.error('Error fetching friend list:', e);
		}
	}
	
	updateList() {
		const listElement = this.shadowRoot.getElementById('list');
		const titleElement = this.shadowRoot.getElementById('title');
		listElement.innerHTML = '';
	
		if (this.hasAttribute('friends') || !this.hasAttribute('requested')) {
			this.updateFriends({listElement, titleElement});
		} else if (this.hasAttribute('requested')) {
			this.updateRequested({listElement, titleElement});
		}
	}
}

customElements.define('friends-list', FriendList);