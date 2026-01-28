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
import ResetPassword from "./pages/resetPassword";
import AdminRoute from "./AdminRoute";
import {useState} from "react"

function App() {
	const [num_of_notifications, setNumNotifications] = useState(0);

	return (
		<Router>
			<AuthProvider>
				<Routes>
					<Route path="/" element={<Navigate to="/login" />} />
					<Route path="/register" element={<Register />} />
					<Route path="/reset-password" element={<ResetPassword />} />
					<Route path="/login" element={<Login />} />
					
					<Route
						path="/profile"
						element={
							<ProtectedRoute>
								<Profile num_of_notifications={num_of_notifications} setNumNotifications = {setNumNotifications} />
							</ProtectedRoute>
						}
					/>
					<Route
						path="/home"
						element={
							<ProtectedRoute>
								<Home num_of_notifications={num_of_notifications} setNumNotifications = {setNumNotifications} />
							</ProtectedRoute>
						}
					/>
					<Route
						path="/myrequests"
						element={
							<ProtectedRoute>
								<MyRequests num_of_notifications={num_of_notifications} setNumNotifications = {setNumNotifications} />
							</ProtectedRoute>
						}
					/>
					<Route
						path="/myequipment"
						element={
							<ProtectedRoute>
								<MyEquipment num_of_notifications={num_of_notifications} setNumNotifications = {setNumNotifications} />
							</ProtectedRoute>
						}
					/>
					<Route
						path="/dashboard"
						element={
							<AdminRoute>
								<Dashboard num_of_notifications={num_of_notifications} setNumNotifications = {setNumNotifications} />
							</AdminRoute>
						}
					/>
					<Route
						path="/usermanagement"
						element={
							<AdminRoute>
								<UserManagement num_of_notifications={num_of_notifications} setNumNotifications = {setNumNotifications} />
							</AdminRoute>
						}
					/>
					<Route
						path="/notifications"
						element={
							<ProtectedRoute>
								<Notifications num_of_notifications={num_of_notifications} setNumNotifications = {setNumNotifications} />
							</ProtectedRoute>
						}
					/>
				</Routes>
			</AuthProvider>
		</Router>
	);
}

export default App;
