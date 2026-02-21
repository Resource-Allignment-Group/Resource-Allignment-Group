import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../Authentication";
import "../styles/login.css";
import { API_BASE } from "../config";

function Login() {
	const [email, setEmail] = useState("");
	const [password, setPassword] = useState("");
	const { login } = useAuth();
	const navigate = useNavigate();

	const handleLogin = async (e) => {
		if (e) e.preventDefault();
		try {
			// Call login function in AuthProvider.js
			const result = await login(email, password);

			if (result.success) {
				navigate("/home");
			} else {
				alert(result.message || "Invalid email or password");
			}
		} catch (error) {
			alert("Something went wrong");
		}
	};

	const ForgotPassword = async (e) => {
		if (e) e.preventDefault();
		try {
			if (!email) {
				alert("Please Enter Email");
			} else {
				const res = await fetch(`http://${API_BASE}:5000/forgot_password`, {
					method: "POST",
					credentials: "include",
					headers: { "Content-Type": "application/json" },
					body: JSON.stringify({
						email: email,
					}),
				});
				const data = await res.json();
				if (data.result) {
					alert("Password recovery email sent to " + email);
				} else {
					alert("Something Went Wrong");
				}
			}
		} catch (error) {
			alert("Something Went Wrong");
		}
	};

	return (
		<div className="container">
			<div className="image-side">
				<img
					src="/static/mafes-webstie-photos-66.jpg"
					alt="Ship Yard"
					className="background-image"
				/>
			</div>

			<div className="login-side">
				<h2 className="title">Login</h2>

				<form className="form">
					<label>Email</label>
					<input
						type="text"
						id="email"
						placeholder="Enter your email"
						value={email}
						onChange={(e) => setEmail(e.target.value)}
					/>

					<label>Password</label>
					<input
						type="password"
						id="password"
						placeholder="Enter your password"
						value={password}
						onChange={(e) => setPassword(e.target.value)}
					/>

					<button type="submit" onClick={handleLogin}>
						Sign In
					</button>
					<div className="form-links">
						<button
							type="button"
							className="link-button"
							onClick={() => navigate("/register")}
						>
							Sign Up
						</button>

						<button
							type="button"
							className="link-button"
							onClick={ForgotPassword}
						>
							Forgot Password
						</button>
					</div>
				</form>
			</div>
		</div>
	);
}
export default Login;
