const login_form = document.querySelector('#loginForm'); // Select the form

// validates data from login form
function validateInputs(login_form) {
	const email = login_form.email.value;
	const password = login_form.password.value;

	if (email === '') {
		console.log('Email is blank');
		return false;
	}
	if (password === '') {
		console.log('Password is blank');
		return false;
	}
	return true;
}

// Event listener when "Login" button is clicked
// checks if form data is valid (not yet implemented)
login_form.addEventListener('submit', (e) => {
	e.preventDefault(); // Prevents the default action (in this case submitting the form)

	const validated = validateInputs(login_form); //returns bool

	if (validated === true) {
		console.log('Form is valid');
		alert('correct');
		window.location.href = 'template.html'; // TEMPORARY!!!
		//history.pushState(null, '', '/prototypes/template.html');
		//history.go(); //refreshes page
	} else if (!validated) {
		console.log('Form is invalid');
		alert('incorrect');
	}
});
