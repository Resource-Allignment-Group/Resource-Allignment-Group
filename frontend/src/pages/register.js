import { useState } from "react";
import { useNavigate } from "react-router-dom";
import "../styles/register.css";
import { API_BASE } from "../config";

function Register() {
	const [email, setEmail] = useState("");
	const [password, setPassword] = useState("");
	const [fname, setFirstName] = useState("");
	const [lname, setLastName] = useState("");
	const [phone_number, setPhoneNumber] = useState("");
	const navigate = useNavigate();

	// Frontend regex cases to check user-input, for quick error handling
	// These exist more extensively in the backend to ensure proper formats
	const isValidEmail = (email) => EMAIL_REGEX.test(email);
	const isValidPhone = (phone) => PHONE_REGEX.test(phone);
	const isValidPassword = (password) => PASSWORD_REGEX.test(password);
	const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
	const PHONE_REGEX = /^(\+1\s?)?(\(?\d{3}\)?[\s.-]?)\d{3}[\s.-]?\d{4}$/;
	const PASSWORD_REGEX =
		/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{8,}$/;

	const handleRegister = async (e) => {
		if (e) e.preventDefault();

		// Validate user input
		if (!fname || !lname) {
			alert("Please enter your first and last name");
			return;
		}

		if (!isValidEmail(email)) {
			alert("Please enter a valid email address");
			return;
		}

		if (!isValidPassword(password)) {
			alert(
				"Password must be at least 8 characters and include uppercase, lowercase, a number, and a symbol",
			);
			return;
		}

		if (!isValidPhone(phone_number)) {
			alert("Please enter a valid phone number");
			return;
		}

		// If initial checks pass, got to backend (run regex again there)
		try {
			const res = await fetch(`http://${API_BASE}:5000/register`, {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify({
					email: email,
					password: password,
					fname: fname,
					lname: lname,
					phone: phone_number,
				}),
				credentials: "include",
			});
			const data = await res.json();

			if (data.result) {
				alert("Account Request has been sent to Admin\nAwaiting Approval");
				navigate("/login");
			} else {
				console.log(data.message)
				alert("Rugh Rough Raggy, something is wrong");
			}
		} catch (error) {
			console.error("Login error:", error);
			alert("Something went wrong");
		}
	};

	return (
		<div className="container">
			<div className="image-side">
				<img
					src="/static/mafes-webstie-photos-35.jpg"
					alt="Forrest #2"
					className="background-image"
				/>
			</div>

			<div className="register-side">
				<h2 className="title">Register</h2>

				<form className="form">
					<label>First Name</label>
					<input type="text" onChange={(e) => setFirstName(e.target.value)} />

					<label>Last Name</label>
					<input type="text" onChange={(e) => setLastName(e.target.value)} />

					<label>Email</label>
					<input type="email" onChange={(e) => setEmail(e.target.value)} />

					<label>Password</label>
					<input
						type="password"
						onChange={(e) => setPassword(e.target.value)}
					/>

					<label>Phone Number</label>
					<input type="tel" onChange={(e) => setPhoneNumber(e.target.value)} />

					<button type="submit" onClick={handleRegister}>
						Sign Up
					</button>
				</form>
			</div>
		</div>
	);
}

export default Register;
