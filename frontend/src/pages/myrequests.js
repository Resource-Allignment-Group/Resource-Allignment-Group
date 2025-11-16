import "../styles/default.css";
import { useState } from "react";

// Import componets that will make up the my requests page
import Header from "../components/header";
import Sidebar from "../components/sidebar";

function MyRequests() {
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
					activeTab="My Requests"
				/>

				{/* The title and brief description of the my requests page  */}
				<div className="hero-section">
					<h2>My Requests</h2>
					<p>View and manage your equipment requests</p>
				</div>
			</div>
		</div>
	);
}

export default MyRequests;
