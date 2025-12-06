import "../styles/default.css";
import { useState } from "react";

// Import componets that will make up the profile page
import Header from "../components/header";
import Sidebar from "../components/sidebar";

function Profile({num_of_notifications, setNumNotifications}) {
	const [sidebarOpen, setSidebarOpen] = useState(true);

	return (
		<div className="home-container">
			{/* Sidebar is a separate component */}
			<Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

			<div className="main">
				{/* Header is a separate component */}
				<Header
					sidebarOpen={sidebarOpen}
					onMenuToggle={() => setSidebarOpen(true)}
					num_of_notifications={num_of_notifications}
					setNotificationsNum={setNumNotifications}
				/>

				{/* The title and brief description of the profile page  */}
				<div className="hero-section">
					<h2>Account Settings</h2>
					<p>Manage your personal information</p>
				</div>
			</div>
		</div>
	);
}

export default Profile;
