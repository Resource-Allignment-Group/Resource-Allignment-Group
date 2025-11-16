import "../styles/default.css";
import { useState } from "react";

// Import componets that will make up the notifications page
import Header from "../components/header";
import Sidebar from "../components/sidebar";

function Notifications() {
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
				/>

				{/* The title and brief description of the notifications page  */}
				<div className="hero-section">
					<h2>Notifications</h2>
					<p>View all incoming notifications</p>
				</div>
			</div>
		</div>
	);
}

export default Notifications;
