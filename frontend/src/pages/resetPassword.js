import { useSearchParams, useNavigate } from "react-router-dom";
import { useState } from "react";
import "../styles/resetPassword.css";
import { API_BASE } from "../config";

// Allows users to reset their password

function ResetPassword() {
	const [params] = useSearchParams();
	const token = params.get("token");
	const [password, setPassword] = useState("");
	const [message, setMessage] = useState(""); // for error/success messages
	const navigate = useNavigate();

	// Password validation
	const PASSWORD_REGEX =
		/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9])[^\s]{8,}$/;

	const isValidPassword = (password) => PASSWORD_REGEX.test(password);

	const submit = async () => {
		if (!password) {
			setMessage("Please enter a new password.");
			return;
		}

		// Ensure valid password before acceptance
		if (!isValidPassword(password)) {
			setMessage(
				"Password must be at least 8 characters and include uppercase, lowercase, a number, and a symbol (no spaces).",
			);
			return;
		}

		try {
			const res = await fetch(`http://${API_BASE}:5000/reset_password`, {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify({ token, password }),
			});

			const data = await res.json();
			// Result messages
			if (data.result) {
				setMessage("Password reset successfully! Redirecting to login...");
				setTimeout(() => navigate("/login"), 1500);
			} else {
				setMessage(data.message || "Failed to reset password.");
			}
		} catch (err) {
			setMessage("Server error. Please try again later.");
		}
	};

	return (
		<div className="reset-password-container">
			<div className="reset-password-card">
				<h2>Reset Your Password</h2>
				<p>Enter a new password to continue.</p>
				<div className="reset-password-form">
					<label htmlFor="password">New Password</label>
					<input
						id="password"
						type="password"
						value={password}
						onChange={(e) => setPassword(e.target.value)}
						placeholder="Enter new password"
					/>
					<button className="reset-password-button" onClick={submit}>
						Reset Password
					</button>
				</div>
				<div className="reset-password-message">{message}</div>
			</div>
		</div>
	);
}

export default ResetPassword;
