import "../styles/default.css";
import "../styles/dashboard.css";
import * as XLSX from "xlsx";
import { useState, useEffect } from "react";
import { API_BASE } from "../config";
import Header from "../components/header";
import Sidebar from "../components/sidebar";
import AddEquipmentModal from "../components/addEquipmentWindow";
import { useSidebar } from "../SidebarContext";

// Displays status of equipment in the DB and allows admins
// to generate reports and add equipment to the DB

function Dashboard({ num_of_notifications, setNumNotifications }) {
	const { sidebarOpen, openSidebar, closeSidebar } = useSidebar();
	const [num_damaged, setDamaged] = useState(0);
	const [num_in_use, setNumInUse] = useState(0);
	const [num_available, setNumAvailable] = useState(0);
	const [num_unavailable, setNumUnavailable] = useState(0);
	const [num_total, setTotal] = useState(0);
	const [showModal, setShowModal] = useState(false);
	const [receiveReports, setReceiveReports] = useState(true);
	const [isLoading, setIsLoading] = useState(true);

	// Used to allow admins to manually download monthly reports
	const downloadReport = () => {
		const downloadUrl = `http://${API_BASE}:5000/download_monthly_report`;
		const link = document.createElement("a");
		link.href = downloadUrl;
		link.setAttribute("download", "Monthly_Report.pdf");
		document.body.appendChild(link);
		link.click();
		link.remove();
	};

	// Blank form format for bulk equip uploads
	const generateTemplate = () => {
		const headers = [
			"Name",
			"Farm",
			"Category",
			"Make",
			"Model",
			"Year",
			"Use",
			"Replacement Cost",
			"Description",
		];
		const sheet = XLSX.utils.aoa_to_sheet([headers]);
		const book = XLSX.utils.book_new();
		XLSX.utils.book_append_sheet(book, sheet, "Template");
		XLSX.writeFile(book, "Bulk Equipment Upload Template.xlsx");
	};

	// Loads all of the dashboard statistics
	useEffect(() => {
		const GetDashboardInfo = async () => {
			try {
				setIsLoading(true);
				const res = await fetch(`http://${API_BASE}:5000/get_dashboard_info`, {
					credentials: "include",
				});
				const data = await res.json();

				setDamaged(data.damaged);
				setNumInUse(data.used);
				setNumAvailable(data.available);
				setNumUnavailable(data.unavailable);
				setTotal(data.total);
				// Set the admins report gen preference, default true
				setReceiveReports(data.receive_reports ?? true);
			} catch (error) {
				alert("Something Went Wrong Gathering The Dashboard Information");
			} finally {
				setIsLoading(false);
			}
		};
		GetDashboardInfo();
	}, []);

	// Updates the admins preference for receiving
	// automatic monthly reports or not
	const handleToggleReports = async (e) => {
		const newValue = e.target.checked;
		setReceiveReports(newValue);
		try {
			await fetch(`http://${API_BASE}:5000/update_report_preference`, {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				credentials: "include",
				body: JSON.stringify({ receive_reports: newValue }),
			});
		} catch (error) {
			alert("Failed to update report preference");
			setReceiveReports(!newValue);
		}
	};

	// Handles the form input for bulk equip upload
	const handleBulkFileChange = async (e) => {
		const file = e.target.files[0];
		if (!file) return;

		const formData = new FormData();
		formData.append("file", file);

		try {
			const res = await fetch(`http://${API_BASE}:5000/add_bulk_equipment`, {
				method: "POST",
				credentials: "include",
				body: formData,
			});
			const data = await res.json();
			alert(data.message);
		} catch (error) {
			console.error("Error uploading file:", error);
			alert("Error uploading file");
		} finally {
			e.target.value = "";
		}
	};

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
					{isLoading ? (
						<div className="response-text">
							<p>Loading Dashboard Metrics...</p>
						</div>
					) : (
						<>
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
								<div className="action-buttons-container">
									<div className="action-buttons-row">
										<button className="action-button" onClick={downloadReport}>
											Generate Monthly Report
										</button>

										<button
											className="action-button"
											onClick={() => setShowModal(true)}
										>
											Add Equipment
										</button>
										<input
											type="file"
											id="bulk-file-input"
											style={{ display: "none" }}
											accept=".xlsx,.xls"
											onChange={handleBulkFileChange}
										/>
										<label htmlFor="bulk-file-input" className="action-button">
											Add Multiple Equipment
										</label>
										<button
											className="action-button"
											onClick={() => generateTemplate()}
										>
											Generate Bulk Equipment Template
										</button>
									</div>
									<div className="checkbox-row">
										<label className="report-checkbox-label">
											<input
												type="checkbox"
												checked={receiveReports}
												onChange={handleToggleReports}
												className="report-checkbox"
											/>
										</label>
										Receive Automated Monthly Reports Via Email
									</div>
								</div>
							</div>
						</>
					)}
				</div>
			</div>
			<AddEquipmentModal
				isOpen={showModal}
				onClose={() => setShowModal(false)}
			/>
		</div>
	);
}

export default Dashboard;
