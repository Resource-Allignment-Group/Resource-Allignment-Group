import { useNavigate } from "react-router-dom";

// This component is used across all pages

function Header({ sidebarOpen, onMenuToggle, activeTab = null }) {
	const navigate = useNavigate();

	return (
		<header className="header">
			{/* The top part of the header  */}
			<div className="header-top">
				{/* Only display menu icon if the sidebar is closed  */}
				{/* Replace with menu icon later  */}
				{!sidebarOpen && (
					<button className="menu-toggle" onClick={onMenuToggle}>
						menu
					</button>
				)}
				<h1>MAFES Equipment Management System</h1>

				{/* Notification and profile items */}
				{/* Replace with icons later  */}
				<div className="header-right">
					<div
						className="notification-icon"
						onClick={() => navigate("/notifications")}
					>
						<p>&#x1F514;</p>
					</div>
					<div className="profile-icon" onClick={() => navigate("/profile")}>
						<p>&#x1F464;</p>
					</div>
				</div>
			</div>

			{/* Navigation items  */}
			{/* Adjust styling for the active/selected nav item  */}
			<nav className="nav-tabs">
				<button
					className={`nav-tab ${activeTab === "Home" ? "active" : ""}`}
					onClick={() => navigate("/home")}
				>
					Home
				</button>
				<button
					className={`nav-tab ${activeTab === "My Requests" ? "active" : ""}`}
					onClick={() => navigate("/myrequests")}
				>
					My Requests
				</button>
				<button
					className={`nav-tab ${activeTab === "My Equipment" ? "active" : ""}`}
					onClick={() => navigate("/myequipment")}
				>
					My Equipment
				</button>
				<button
					className={`nav-tab ${activeTab === "Dashboard" ? "active" : ""}`}
					onClick={() => navigate("/dashboard")}
				>
					Dashboard
				</button>
				<button
					className={`nav-tab ${
						activeTab === "User Management" ? "active" : ""
					}`}
					onClick={() => navigate("/usermanagement")}
				>
					User Management
				</button>
			</nav>
		</header>
	);
}

export default Header;
