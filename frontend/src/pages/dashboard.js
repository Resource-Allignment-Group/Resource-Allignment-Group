import "../styles/default.css";
import "../styles/dashboard.css";
import { useState, useEffect } from "react";
import { API_BASE } from "../config";
// Import componets that will make up the dashboard page
import Header from "../components/header";
import Sidebar from "../components/sidebar";
import AddEquipmentModal from "../components/addEquipmentWindow";
import { useSidebar } from "../SidebarContext";

function Dashboard({ num_of_notifications, setNumNotifications }) {
	const { sidebarOpen, openSidebar, closeSidebar } = useSidebar();
	const [num_damaged, setDamaged] = useState(0);
	const [num_in_use, setNumInUse] = useState(0);
	const [num_available, setNumAvailable] = useState(0);
	const [num_unavailable, setNumUnavailable] = useState(0);
	const [num_total, setTotal] = useState(0);
	const [showModal, setShowModal] = useState(false);

	// USed to allow admins to manually download monthly reports
	const downloadReport = () => {
		const downloadUrl = `http://${API_BASE}:5000/download_monthly_report`;
		const link = document.createElement("a");
		link.href = downloadUrl;
		link.setAttribute("download", "Monthly_Report.pdf");
		document.body.appendChild(link);
		link.click();
		link.remove();
	};

	useEffect(() => {
		const GetDashboardInfo = async () => {
			try {
				const res = await fetch(`http://${API_BASE}:5000/get_dashboard_info`, {
					credentials: "include",
				});
				const data = await res.json();

				setDamaged(data.damaged);
				setNumInUse(data.used);
				setNumAvailable(data.available);
				setNumUnavailable(data.unavailable);
				setTotal(data.total);
			} catch (error) {
				alert("Something Went Wrong Gathering The Dashboard Information");
			}
		};
		GetDashboardInfo();
	}, []);
	return (
		<div className="home-container">
			{/* Sidebar is a separate component */}
			<Sidebar isOpen={sidebarOpen} onClose={closeSidebar} />

			<div className="main">
				{/* Header is a separate component */}
				<Header
					sidebarOpen={sidebarOpen}
					onMenuToggle={openSidebar}
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

				{/* Dashboard content */}
				<div className="dashboard-content">
					<div className="dashboard-card">
						<h3 className="section-title">Equipment Metrics</h3>
						{/* Placeholder statistic cards */}
						{/* Connect this to backend with actual data, refresh daily? */}
						<div className="stats-grid">
							<div className="stat-card blue">
								<h4>Total</h4>
								<p className="stat-number">{num_total}</p>
							</div>

							<div className="stat-card green">
								<h4>Available</h4>
								<p className="stat-number">{num_available}</p>
							</div>

							<div className="stat-card yellow">
								<h4>In Use</h4>
								<p className="stat-number">{num_in_use}</p>
							</div>

							<div className="stat-card red">
								<h4>Damaged</h4>
								<p className="stat-number">{num_damaged}</p>
							</div>

							<div className="stat-card gray">
								<h4>Unavailable</h4>
								<p className="stat-number">{num_unavailable}</p>
							</div>
						</div>

						{/* Action buttons */}
						<div className="action-buttons-row">
							<button
								className="action-button"
								onClick={downloadReport}
								style={{ cursor: "pointer" }}
							>
								<span>
									<strong>Generate Monthly Report</strong>
								</span>
								<span className="plus-icon">+</span>
							</button>
							<button
								className="action-button"
								onClick={() => setShowModal(true)}
								style={{ cursor: "pointer" }}
							>
								<span>
									<strong>Add Equipment</strong>
								</span>
								<span className="plus-icon">+</span>
							</button>
							<AddEquipmentModal
								isOpen={showModal}
								onClose={() => setShowModal(false)}
							/>
						</div>
					</div>
				</div>
			</div>
		</div>
	);
}

export default Dashboard;
