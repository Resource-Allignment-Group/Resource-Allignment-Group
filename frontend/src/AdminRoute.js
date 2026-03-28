import { Navigate } from "react-router-dom";
import { useAuth } from "./Authentication";

// Admin protected routes
const AdminRoute = ({ children }) => {
	const { user, role, isLoading } = useAuth();

	if (isLoading)
		return (
			<div>
				<p>Loading...</p>
			</div>
		);
	// Role 'a' = admin
	return user && role === "a" ? children : <Navigate to="/home" />;
};

export default AdminRoute;
