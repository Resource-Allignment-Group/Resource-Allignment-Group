import "../styles/default.css";
import { useState } from "react";

// Import componets that will make up the my equipment page
import Header from "../components/header";
import Sidebar from "../components/sidebar";

function MyEquipment() {
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
					activeTab="My Equipment"
				/>

				{/* The title and brief description of the my equipment page  */}
				<div className="hero-section">
					<h2>My Equipment</h2>
					<p>Equipment currently checked out to you</p>
				</div>
			</div>
		</div>
	);
}

export default MyEquipment;
