import { ComponentBaseClass } from "./componentBaseClass.js";

export class FriendList extends ComponentBaseClass {
	static get observedAttributes() {
		return ['friends', 'requested'];
	}

	constructor() {
		super();

		this.friends = new Map();
		this.requested = new Map();
		this.received = new Map();
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
			<div class="p-3 rounded-3 bg-dark">
				<div class="btn-group" role="toolbar" aria-label="Element to switch between friends and requests">
					<button type="button" class="btn btn-primary" id="friends-button">Friends</button>
					<button type="button" class="btn btn-primary" id="requested-button">Requests</button>
				</div>
				<ul class="list-group bg-dark" id="list"></ul>
			</div>`
		return template;
	}

	connectedCallback() {
		super.connectedCallback();

		const buttons = this.shadowRoot.querySelectorAll('.btn');
		buttons.forEach((button) => {
			button.addEventListener('click', (event) => {
				const clickedButton = event.target;
				buttons.forEach(btn => btn.classList.remove('active'));
				clickedButton.classList.add('active');
				clickedButton.setAttribute('aria-current','page');
				
				console.log(this);
				if (clickedButton.id === 'friends-button') {
					this.removeAttribute('requested');
					this.setAttribute('friends', '');
				} else if (clickedButton.id === 'requested-button') {
					this.removeAttribute('friends');
					this.setAttribute('requested', '');
				}
			});
		});
		this.fetchFriendList();
	}

	attributeChangedCallback(name, oldValue, newValue) {
		if (oldValue !== newValue) {
		  this.fetchFriendList();
		}
	}
	
	updateFriends(listElement) {
		this.shadowRoot.getElementById('friends-button').classList.add('active');

		if (this.friends.size < 1) {
			const item = document.createElement('li');
			item.className = 'list-group-item d-flex justify-content-around w-100';
			item.innerHTML = `<span class="text-muted">No friends yet</span>`
			listElement.appendChild(item);
			return;
		}
		
		this.friends.forEach((request, key) => {
			const item = document.createElement('li');
			item.className = 'list-group-item d-flex justify-content-around w-100';
			item.innerHTML = `
				<button class="btn btn-danger btn-sm">X</button>
				<div class="friend-img-container">
					<img src="${request.img}" alt="Profile image of ${request.name}" class="friend-img">
					<span class="friend-status ${request.online ? 'online' : 'offline'}"></span>
				</div>
				<span>${request.name}</span>
			`;
			item.querySelector('.btn-danger').addEventListener('click', () => {
				//TODO: add API call to remove friend
				this.friends.delete(key);
				listElement.removeChild(item);
				if (this.friends.size < 1) {
					const empty = document.createElement('li');
					empty.className = 'list-group-item d-flex justify-content-around w-100';
					empty.innerHTML = `<span class="text-muted">No friends</span>`
					listElement.appendChild(empty);
				}
			});
			listElement.appendChild(item);
		});
	}
	
	updateRequested(listElement) {
		this.shadowRoot.getElementById('requested-button').classList.add('active');
		
		if (this.requested.size < 1 && this.received.size < 1) {
			const item = document.createElement('li');
			item.className = 'list-group-item d-flex justify-content-around w-100';
			item.innerHTML = `<span class="text-muted">No friends yet</span>`
			listElement.appendChild(item);
			return;
		}

		this.requested.forEach((request, key) => {
			const item = document.createElement('li');
			item.className = 'list-group-item d-flex justify-content-around w-100';
			item.innerHTML = `
				<button class="btn btn-success btn-sm disabled">✓</button>
				<button class="btn btn-danger btn-sm">X</button>
				<span>${request.name}</span>
			`;
			item.querySelector('.btn-danger').addEventListener('click', () => {
				//TODO: add API call to remove friend request
				this.requested.delete(key);
				listElement.removeChild(item);
				if (this.received.size < 1 && this.requested.size < 1) {
					const empty = document.createElement('li');
					empty.className = 'list-group-item d-flex justify-content-around w-100';
					empty.innerHTML = `<span class="text-muted">No requests</span>`
					listElement.appendChild(empty);
				}
			});
			listElement.appendChild(item);
		});
		this.received.forEach((request, key) => {
			const item = document.createElement('li');
			item.className = 'list-group-item d-flex justify-content-around w-100';
			item.innerHTML = `
			<button class="btn btn-success btn-sm">✓</button>
			<button class="btn btn-danger btn-sm">X</button>
			<span>${request.name}</span>
			`;
			item.querySelectorAll('button').forEach(button => {
				button.addEventListener('click', (event) => {
					const button = event.target;
					if (button.classList.contains('btn-success')) {
						// TODO: add API call to accept friend request
						this.friends.set(key, this.received.get(key));
						this.received.delete(key);
					} else if (button.classList.contains('btn-danger')) {
						// TODO: add API call to remove friend request
						this.received.delete(key);
					}
					listElement.removeChild(item);
					if (this.received.size < 1 && this.requested.size < 1) {
						const empty = document.createElement('li');
						empty.className = 'list-group-item d-flex justify-content-around w-100';
						empty.innerHTML = `<span class="text-muted">No requests</span>`
						listElement.appendChild(empty);
					}
				});
			});
			listElement.appendChild(item);
		});
	}
	
	async fetchFriendList() {
		try {
			//substitute with endpoint instead of dummy JSON
			const response = await fetch('./js/friends.json');
			const data = await response.json();
			data.map(item => {
				if (item.is_friend === true)
					this.friends.set(item.uid, { "name": item.displayname, "img": item.img, "online": item.onlinestatus });
				else if (item.is_pending_sender === true)
					this.requested.set(item.uid, { "name": item.displayname, "img": item.img });
				else if (item.is_pending_receiver === true)
					this.received.set(item.uid, { "name": item.displayname, "img": item.img });
			});
			this.updateList();
		} catch (e) {
		  	console.error('Error fetching friend list:', e);
		}
	}
	
	updateList() {
		const listElement = this.shadowRoot.getElementById('list');
		listElement.innerHTML = '';
	
		if (this.hasAttribute('friends') || !this.hasAttribute('requested')) {
			this.updateFriends(listElement);
		} else if (this.hasAttribute('requested')) {
			this.updateRequested(listElement);
		}
	}
}

customElements.define('friends-list', FriendList);