import "../styles/default.css";
import { useState } from "react";
import Header from "../components/header";
import Sidebar from "../components/sidebar";

function UserManagement() {
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
					activeTab="User Management"
				/>

				{/* The title and brief description of the user management page  */}
				<div className="hero-section">
					<h2>User Management</h2>
					<p>Monitor user accounts and permissions</p>
				</div>
			</div>
		</div>
	);
}

export default UserManagement;
