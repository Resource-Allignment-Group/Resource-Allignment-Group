import "../styles/default.css";
import "../styles/dashboard.css";
import { useState } from "react";

// Import componets that will make up the dashboard page
import Header from "../components/header";
import Sidebar from "../components/sidebar";

function Dashboard() {
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
				/>

				{/* The title and brief description of the dashboard page  */}
				<div className="hero-section">
					<h2>Dashboard</h2>
					<p>
						View equipment usage, generate monthly reports, and add equipment to
						the database
					</p>
				</div>

				{/* Dashboard content */}
				<div className="dashboard-content">
					<div className="dashboard-card">
						<h3 className="section-title">Equipment Metrics</h3>
						{/* Placeholder statistic cards */}
						{/* Connect this to backend with actual data, refresh daily? */}
						<div className="stats-grid">
							<div className="stat-card blue">
								<h4>Total</h4>
								<p className="stat-number">170</p>
							</div>

							<div className="stat-card green">
								<h4>Available</h4>
								<p className="stat-number">50</p>
							</div>

							<div className="stat-card yellow">
								<h4>In Use</h4>
								<p className="stat-number">100</p>
							</div>

							<div className="stat-card red">
								<h4>Damaged</h4>
								<p className="stat-number">5</p>
							</div>

							<div className="stat-card gray">
								<h4>Unavailable</h4>
								<p className="stat-number">15</p>
							</div>
						</div>

						{/* Action buttons */}
						<div className="action-buttons-row">
							<button className="action-button">
								<span>
									<strong>Generate Monthly Report</strong>
								</span>
								<span className="plus-icon">+</span>
							</button>

							<button className="action-button">
								<span>
									<strong>Add Equipment</strong>
								</span>
								<span className="plus-icon">+</span>
							</button>
						</div>
					</div>
				</div>
			</div>
		</div>
	);
}

export default Dashboard;
