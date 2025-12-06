import "../styles/default.css";
import { useState } from "react";

// Import componets that will make up the dashboard page
import Header from "../components/header";
import Sidebar from "../components/sidebar";

function Dashboard({num_of_notifications, setNumNotifications}) {
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
					activeTab="Dashboard"
					num_of_notifications={num_of_notifications}
					setNotificationsNum={setNumNotifications}
				/>

				{/* The title and brief description of the dashboard page  */}
				<div className="hero-section">
					<h2>Dashboard</h2>
					<p>
						View equipment usage, generate monthly reports, and add equipment to
						the database
					</p>
				</div>
			</div>
		</div>
	);
}

export default Dashboard;
