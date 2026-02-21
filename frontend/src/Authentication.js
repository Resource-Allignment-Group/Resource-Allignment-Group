import { useEffect, createContext, useContext, useState } from "react";
import { API_BASE } from "./config";
const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
	const [user, setUser] = useState(null);
	const [role, setRole] = useState(null);
	const [isLoading, setIsLoading] = useState(true);

	useEffect(() => {
		const checkSession = async () => {
			try {
				const res = await fetch(`http://${API_BASE}:5000/check-session`, {
					//checks to see if user is loged in with Flask sessions
					method: "GET",
					credentials: "include",
				});

				// If the server returns 401, the user doesn't exist anymore
				// Clear their session
				if (res.status === 401) {
					setUser(null);
					setRole(null);
					return;
				}

				const data = await res.json();
				if (data.result) {
					setUser({ email: data.user });
					setRole(data.role); // <-- store role
				} else {
					setUser(null);
					setRole(null);
				}
			} catch (err) {
				setUser(null);
				setRole(null);
			} finally {
				setIsLoading(false);
			}
		};

		checkSession();
	}, []);

	const login = async (email, password) => {
		try {
			const res = await fetch(`http://${API_BASE}:5000/authenticate`, {
				//logis in the user and starts their session
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify({ email, password }),
				credentials: "include",
			});

			const data = await res.json();
			if (res.ok && data.message === "success") {
				setUser({ email });
				setRole(data.role || null);
				return { success: true };
			} else {
				return { success: false, message: data.message };
			}
		} catch (err) {
			return { success: false, message: "Server Connection Failed" };
		}
	};

	const logout = async () => {
		try {
			await fetch(`http://${API_BASE}:5000/logout`, {
				//Logs the user out, will need tro impliment into pack end
				method: "POST",
				credentials: "include",
			});
		} catch (err) {
			console.error("Logout failed", err);
		} finally {
			setUser(null);
			setRole(null);
			return true;
		}
	};

	return (
		<AuthContext.Provider value={{ user, role, login, logout, isLoading }}>
			{children}
		</AuthContext.Provider>
	);
};

export const useAuth = () => useContext(AuthContext);
