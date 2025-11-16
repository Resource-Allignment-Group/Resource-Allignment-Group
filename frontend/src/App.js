import "./App.css";
import {
	BrowserRouter as Router,
	Routes,
	Route,
	Navigate,
} from "react-router-dom";
import Login from "./pages/login";
import Home from "./pages/home";
import Profile from "./pages/profile";
import { AuthProvider } from "./Authentication";
import ProtectedRoute from "./ProtectedRoute";
import Register from "./pages/register";
import MyRequests from "./pages/myrequests";
import MyEquipment from "./pages/myequipment";
import Dashboard from "./pages/dashboard";
import UserManagement from "./pages/usermanagement";
import Notifications from "./pages/notifications";

function App() {
	return (
		<Router>
			<AuthProvider>
				<Routes>
					<Route path="/" element={<Navigate to="/login" />} />
					<Route path="/register" element={<Register />} />
					<Route
						path="/profile"
						element={
							<ProtectedRoute>
								<Profile />
							</ProtectedRoute>
						}
					/>
					<Route path="/login" element={<Login />} />
					<Route
						path="/home"
						element={
							<ProtectedRoute>
								<Home />
							</ProtectedRoute>
						}
					/>
					<Route
						path="/myrequests"
						element={
							<ProtectedRoute>
								<MyRequests />
							</ProtectedRoute>
						}
					/>
					<Route
						path="/myequipment"
						element={
							<ProtectedRoute>
								<MyEquipment />
							</ProtectedRoute>
						}
					/>
					<Route
						path="/dashboard"
						element={
							<ProtectedRoute>
								<Dashboard />
							</ProtectedRoute>
						}
					/>
					<Route
						path="/usermanagement"
						element={
							<ProtectedRoute>
								<UserManagement />
							</ProtectedRoute>
						}
					/>
					<Route
						path="/notifications"
						element={
							<ProtectedRoute>
								<Notifications />
							</ProtectedRoute>
						}
					/>
				</Routes>
			</AuthProvider>
		</Router>
	);
}

export default App;
