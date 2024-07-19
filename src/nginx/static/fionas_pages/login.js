const login_form = document.querySelector('#loginForm'); // Select the form

// const setError = (validateInputs = () => {
// 	const emailElement = document.getElementById("inputEmail");
// 	const passwordElement = document.getElementById("inputPassword");
	
// 	// Fetching values
// 	const emailValue = emailElement.value.trim();
// 	const passwordValue = passwordElement.value.trim();
	
// 	if (emailValue === "") {
// 		console.log("Email is blank");
// 	}
	
// 	if (passwordValue === "") {
// 		console.log("Password is blank");
// 	}
// });

function validateInputs(login_form) {
	const email = login_form.email.value;
	const password = login_form.password.value;
	
	if (email === "") {
		console.log("Email is blank");
		return false;
	}
	if (password === "") {
		console.log("Password is blank");
		return false;
	}
	return true;
};



login_form.addEventListener("submit", e => {
	e.preventDefault(); // Prevents the default action (in this case submitting the form)
	
	const validated = validateInputs(login_form); //returns bool

	if (validated === true) {
		console.log("Form is valid");
		alert("correct");
		window.location.href = "template.html";
	}
	else if (!validated) {
		console.log("Form is invalid");
		alert("incorrect");
	}
});