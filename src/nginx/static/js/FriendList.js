import { ComponentBaseClass } from "./componentBaseClass.js";

export class FriendList extends ComponentBaseClass {
	static get observedAttributes() {
		return ["friends", "requested"];
	}

	constructor() {
		super();
		this.friends = new Map();
		this.requested = new Map();
		this.received = new Map();
		this.result = [];
		this.debouncedFetchFriendList = this.debounce(
			this.fetchFriendList.bind(this),
			10,
		);
	}

	getElementHTML() {
		const template = document.createElement("template");
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
		const buttons = this.shadowRoot.querySelectorAll(".btn");
		for (const button of buttons) {
			if (
				(button.id === "friends-button" &&
					(this.hasAttribute("friends") || this.attributes.length === 0)) ||
				(button.id === "requested-button" && this.hasAttribute("requested"))
			) {
				button.classList.add("active");
			}
			button.addEventListener("click", (event) => {
				const clickedButton = event.target;
				for (const btn of buttons) {
					btn.classList.remove("active");
					btn.removeAttribute("aria-current");
				}
				clickedButton.classList.add("active");
				clickedButton.setAttribute("aria-current", "page");

				if (clickedButton.id === "friends-button") {
					this.removeAttribute("requested");
					this.setAttribute("friends", "");
				} else if (clickedButton.id === "requested-button") {
					this.removeAttribute("friends");
					this.setAttribute("requested", "");
				}
			});
		}
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
			this.result = await this.apiFetch("/um/friends/", {
				method: "GET",
				cache: "no-store",
			});
			//this.processFriendData(response);
			this.updateList();
		} catch (e) {
			console.error("Error fetching friend list:", e.message);
		}
	}

	updateList() {
		const listElement = this.shadowRoot.getElementById("list");
		listElement.innerHTML = "";

		if (this.hasAttribute("friends") || !this.hasAttribute("requested")) {
			this.updateItems(
				listElement,
				"No friends",
				this.createFriendListItem.bind(this),
				["friend"],
			);
		} else if (this.hasAttribute("requested")) {
			this.updateItems(
				listElement,
				"No friend requests",
				this.createRequestItem.bind(this),
				["requested", "received"],
			);
		}
	}

	updateItems(listElement, emptyMessage, createListItem, types) {
		const fragment = document.createDocumentFragment();
		let n = 0;
		for (const item of this.result) {
			if (types.includes(item.relationship)) {
				const itemElement = createListItem(item);
				fragment.appendChild(itemElement);
				n++;
			}
		}
		if (n === 0) {
			const item = document.createElement("li");
			item.className =
				"list-group-item d-flex justify-content-start w-100 bg-dark";
			item.innerHTML = `<span class="text-white">${emptyMessage}</span>`;
			fragment.appendChild(item);
		}
		listElement.appendChild(fragment);
	}

	createFriendListItem(itemData) {
		const item = document.createElement("li");
		item.className =
			"list-group-item d-flex justify-content-start w-100 bg-dark";
		item.innerHTML = `
      <button class="btn btn-danger btn-sm">X</button>
      <div class="friend-img-container">
        <img src="${itemData.image}" alt="Profile image of ${itemData.displayname}" class="friend-img" onerror='this.style.display = "none"'>
        <span class="friend-status ${itemData.online ? "online" : "offline"}"></span>
      </div>
      <span class="text-white">${itemData.displayname}</span>
    `;
		item.querySelector(".btn-danger").addEventListener("click", () => {
			this.changeFriendRequest(itemData.friend_request_id, "unfriend");
		});
		return item;
	}

	createRequestItem(itemData, action) {
		const item = document.createElement("li");
		item.className =
			"list-group-item d-flex justify-content-start w-100 bg-dark";
		item.innerHTML = `
	  		<button class="btn btn-success btn-sm">✓</button>
	  		<button class="btn btn-danger btn-sm">X</button>
	  		<span class="text-white">${itemData.displayname}</span>
		`;
		if (action === "received") {
			item.querySelector(".btn-success").addEventListener("click", () => {
				this.changeFriendRequest(itemData.friend_request_id, "accept");
			});
			item.querySelector(".btn-danger").addEventListener("click", () => {
				this.changeFriendRequest(itemData.friend_request_id, "decline");
			});
		} else if (action === "requested") {
			item.querySelector(".btn-success").classList.add("disabled");
			item.querySelector(".btn-danger").classList.add("disabled");
		}
		return item;
	}

	async changeFriendRequest(fid, newStatus) {
		const response = await this.apiFetch("/um/friends/answer", {
			method: "POST",
			body: JSON.stringify({ friend_request_id: fid, action: newStatus }),
		});
		if (response.error) {
			console.error("Error changing friend request:", response.error);
			return;
		}

		for (const user of this.result) {
			if (user.friend_request_id === fid) {
				if (newStatus === "decline" || newStatus === "unfriend") {
					user.relationship = "stranger";
				} else if (newStatus === "accept") {
					user.relationship = "friend";
				}
			}
		}
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

customElements.define("friend-list", FriendList);
