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
		this.debouncedFetchFriendList = this.debounce(this.fetchFriendList.bind(this), 10);
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
        .list-group-item {
          display: flex;
          align-items: center;
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
        .list-group-item > .btn {
          margin-right: 0.25rem;
          width: 30px;
          height: 30px;
          aspect-ratio: 1 / 1;
        }
        .list-group-item {
          min-height: 58px;
        }
        .container {
        width: 100%;
        max-width: 400px;
        margin: 0 auto;
      }
      </style>
      <div class="container">
      	<div class="p-3 rounded-3 bg-dark">
			<div class="btn-group w-100 mb-3" role="toolbar" aria-label="Element to switch between friends and requests">
			  <button type="button" class="btn btn-outline-primary" id="friends-button">Friends</button>
			  <button type="button" class="btn btn-outline-primary" id="requested-button">Requests</button>
			</div>
			<ul class="list-group bg-dark" id="list"></ul>
		</div>
      </div>
`;
		return template;
	}

	setupEventListeners() {
		const buttons = this.shadowRoot.querySelectorAll('.btn');
		buttons.forEach((button) => {
			if ((button.id === 'friends-button' && (this.hasAttribute('friends') || this.attributes.length == 0)) || (button.id === 'requested-button' && this.hasAttribute('requested'))) {
				button.classList.add('active');
			}
			button.addEventListener('click', (event) => {
				const clickedButton = event.target;
				buttons.forEach(btn => btn.classList.remove('active'));
				clickedButton.classList.add('active');
				clickedButton.setAttribute('aria-current', 'page');

				if (clickedButton.id === 'friends-button') {
					this.removeAttribute('requested');
					this.setAttribute('friends', '');
				} else if (clickedButton.id === 'requested-button') {
					this.removeAttribute('friends');
					this.setAttribute('requested', '');
				}
			});
		});
	}

	connectedCallback() {
		super.connectedCallback();
		this.setupEventListeners();
		this.debouncedFetchFriendList();
	}

	attributeChangedCallback(name, oldValue, newValue) {
		if (oldValue !== newValue) {
			this.debouncedFetchFriendList();
		}
	}

	async fetchFriendList() {
		try {
			const response = await fetch('./js/friends.json', { cache: 'no-store' });
			const data = await response.json();
			this.processFriendData(data);
			this.updateList();
		} catch (e) {
			console.error('Error fetching friend list:', e.message);
		}
	}

	processFriendData(data) {
		this.friends.clear();
		this.requested.clear();
		this.received.clear();
		console.log(data);
		data.forEach(item => {
			if (item.relationship === 'friend') {
				this.friends.set(item.user.uid, item);
			} else if (item.relationship === 'requested') {
				this.requested.set(item.user.uid, item);
			} else if (item.relationship === 'received') {
				this.received.set(item.user.uid, item);
			}
		});
	}

	updateList() {
		const listElement = this.shadowRoot.getElementById('list');
		listElement.innerHTML = '';

		if (this.hasAttribute('friends') || !this.hasAttribute('requested')) {
			this.updateItems(listElement, this.friends, 'No friends', this.createFriendListItem.bind(this));
		} else if (this.hasAttribute('requested')) {
			if (this.requested.size === 0 && this.received.size === 0) {
				const item = document.createElement('li');
				item.className = 'list-group-item d-flex justify-content-start w-100 bg-dark';
				item.innerHTML = `<span class="text-white">No friend requests</span>`;
				listElement.appendChild(item);
			} else {
				if (this.requested.size > 0) {
					this.updateItems(listElement, this.requested, '', this.createRequestedListItem.bind(this));
				}
				if (this.received.size > 0) {
					this.updateItems(listElement, this.received, '', this.createReceivedListItem.bind(this));
				}			}
		}
	}

	updateItems(listElement, items, emptyMessage, createListItem) {
		if (items.size < 1) {
			const item = document.createElement('li');
			item.className = 'list-group-item d-flex justify-content-start w-100 bg-dark';
			item.innerHTML = `<span class="text-white">${emptyMessage}</span>`;
			listElement.appendChild(item);
			return;
		}

		const fragment = document.createDocumentFragment();
		items.forEach((itemData, key) => {
			const item = createListItem(itemData);
			fragment.appendChild(item);
		});
		listElement.appendChild(fragment);
	}

	createFriendListItem(itemData) {
		const item = document.createElement('li');
		item.className = 'list-group-item d-flex justify-content-start w-100 bg-dark';
		item.innerHTML = `
      <button class="btn btn-danger btn-sm">X</button>
      <div class="friend-img-container">
        <img src="${itemData.user.img}" alt="Profile image of ${itemData.user.displayname}" class="friend-img">
        <span class="friend-status ${itemData.user.online ? 'online' : 'offline'}"></span>
      </div>
      <span class="text-white">${itemData.user.displayname}</span>
    `;
		item.querySelector('.btn-danger').addEventListener('click', () => {
			this.removeFriend(itemData.user.uid);
		});
		return item;
	}

	createRequestedListItem(itemData) {
		const item = document.createElement('li');
		item.className = 'list-group-item d-flex justify-content-start w-100 bg-dark';
		item.innerHTML = `
      <button class="btn btn-success btn-sm disabled">✓</button>
      <button class="btn btn-danger btn-sm">X</button>
      <span class="text-white">${itemData.user.displayname}</span>
    `;
		item.querySelector('.btn-danger').addEventListener('click', () => {
			this.removeFriendRequest(itemData.user.uid);
		});
		return item;
	}

	createReceivedListItem(itemData) {
		const item = document.createElement('li');
		item.className = 'list-group-item d-flex justify-content-start w-100 bg-dark';
		item.innerHTML = `
      <button class="btn btn-success btn-sm">✓</button>
      <button class="btn btn-danger btn-sm">X</button>
      <span class="text-white">${itemData.user.displayname}</span>
    `;
		item.querySelector('.btn-success').addEventListener('click', () => {
			this.acceptFriendRequest(itemData.user.uid);
		});
		item.querySelector('.btn-danger').addEventListener('click', () => {
			this.declineFriendRequest(itemData.user.uid);
		});
		return item;
	}

	async removeFriend(uid) {
		// TODO: Add API call to remove friend
		this.friends.delete(uid);
		this.updateList();
	}

	async removeFriendRequest(uid) {
		// TODO: Add API call to remove friend request
		this.requested.delete(uid);
		this.updateList();
	}

	async acceptFriendRequest(uid) {
		// TODO: Add API call to accept friend request
		this.received.delete(uid);
		this.updateList();
	}

	async declineFriendRequest(uid) {
		// TODO: Add API call to decline friend request
		this.received.delete(uid);
		this.updateList();
	}

	debounce(func, wait) {
		let timeout;
		return function (...args) {
			clearTimeout(timeout);
			timeout = setTimeout(() => func.apply(this, args), wait);
		};
	}
}

customElements.define('friend-list', FriendList);
