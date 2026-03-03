import { Navigate } from "react-router-dom";
import { useAuth } from "./Authentication";

// Protects routes that require Admin or Superintendent roles
const AdminOrSuperintendentRoute = ({ children }) => {
	const { user, role, isLoading } = useAuth();

	if (isLoading)
		return (
			<div>
				<p>Loading...</p>
			</div>
		);
	return user && (role === "a" || role === "s") ? (
		children
	) : (
		<Navigate to="/home" />
	);
};

export default AdminOrSuperintendentRoute;
