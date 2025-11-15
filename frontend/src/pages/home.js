import "../styles/home.css";
import { useNavigate } from "react-router-dom";
import { useState } from "react";

// From the original homepage, will likely be moved to the admin dashboard
// import EquipmentPopup from "../Popup";

function Home() {
	const navigate = useNavigate();
	const [sidebarOpen, setSidebarOpen] = useState(true);
	const [selectedFarm, setSelectedFarm] = useState("All Farms");
	const [expandedCard, setExpandedCard] = useState(null);

	// From the original homepage, will likely be moved to the admin dashboard
	// const [activatePopup, setActivatePopup] = useState(false);

	// Sample equipment data, will be replaced with backend data later
	const equipment = [
		{
			id: 1,
			name: "Tractor - John Deere 4040",
			status: "Available",
			category: "Tractor",
			make: "John Deere",
			model: "4040",
			assignedFarm: "Aroostook",
			useFrequency: "Seasonally",
			replacementCost: "$120,000",
			description:
				'Back up for heavy tillage, used for 2" tillage. Used as spare if researchers need it, used for spreading waste potatoes.',
			attachments: 0,
		},
		{
			id: 2,
			name: "Snow Plow Truck - Ford",
			status: "Checked Out",
			checkedOutBy: "exampleUser@gmail.com",
			category: "Truck",
			make: "Ford",
			model: "F-350",
			assignedFarm: "Blueberry Hill",
			useFrequency: "Seasonal",
			replacementCost: "$75,000",
			description: "Snow removal vehicle for winter maintenance operations.",
			attachments: 2,
		},
		{
			id: 3,
			name: "Pneumatic Forklift - Yale",
			status: "Damaged",
			category: "Forklift",
			make: "Yale",
			model: "GP050VX",
			assignedFarm: "Highmoor",
			useFrequency: "Daily",
			replacementCost: "$35,000",
			description: "Indoor/outdoor forklift for material handling.",
			attachments: 1,
		},
		{
			id: 4,
			name: "COPY FOR SCROLLABILITY TESTING",
			status: "Damaged",
		},
	];

	const farms = [
		"All Farms",
		"Aroostook",
		"Blueberry Hill",
		"Highmoor",
		"Rogers",
		"Witter",
		"Greenhouse/Gardens",
	];

	// From the original homepage, will likely be moved to the admin dashboard
	// function AddEquipment(equipmentInformation) {
	// console.log("Added equipment", equipmentInformation);
	// }

	// Will check the status of the specific equipment item
	// It will display the stylized badge associated to that status
	function getStatusClass(status) {
		if (status === "Available") return "status-available";
		if (status === "Checked Out") return "status-checked-out";
		if (status === "Damaged") return "status-damaged";
		return "";
	}

	return (
		<div className="home-container">
			{/* Only display sidebar content if it is open */}
			{sidebarOpen && (
				<div className="sidebar">
					{/* Replace with arrow icon later  */}
					<button className="back-button" onClick={() => setSidebarOpen(false)}>
						arrow
					</button>

					{/* Search bar for equipment lookup */}
					<div className="search-box">
						<input type="text" placeholder="Search" />
					</div>

					{/* All of the farm buttons, as a list  */}
					<h3>Sort by Farm</h3>
					<div className="farm-list">
						{farms.map((farm) => (
							<button
								key={farm}
								className={`farm-item ${selectedFarm === farm ? "active" : ""}`}
								onClick={() => setSelectedFarm(farm)}
							>
								{farm}
							</button>
						))}
					</div>

					{/* The filtering options at the bottom of the sidebar  */}
					<h3>Filter Options</h3>
					<div className="filter-group">
						<label>Equipment Type</label>
						<select>
							<option>All Types</option>
							<option>Tractor</option>
							<option>Truck</option>
							<option>Forklift</option>
						</select>
					</div>

					<div className="filter-group">
						<label>Equipment Make</label>
						<select>
							<option>All Makes</option>
							<option>John Deere</option>
							<option>Ford</option>
							<option>Yale</option>
						</select>
					</div>

					<div className="filter-group">
						<label>Equipment Year</label>
						<select>
							<option>All Years</option>
							<option>2020</option>
							<option>2019</option>
							<option>2018</option>
						</select>
					</div>

					<div className="filter-group">
						<label>Accessibility</label>
						<select>
							<option>All Users</option>
							<option>Researchers</option>
							<option>Farm Staff</option>
							<option>Superintendent</option>
						</select>
					</div>
				</div>
			)}
			{/* End of sidebar content  */}

			<div className="main">
				<header className="header">
					{/* The top part of the header  */}
					<div className="header-top">
						{/* Only display menu icon if the sidebar is closed  */}
						{/* Replace with menu icon later  */}
						{!sidebarOpen && (
							<button
								className="menu-toggle"
								onClick={() => setSidebarOpen(true)}
							>
								menu
							</button>
						)}
						<h1>MAFES Equipment Management System</h1>

						{/* Notification and profile icons (in the top right) */}
						<div className="header-right">
							<div className="notification-icon">
								<p>&#x1F514;</p>
							</div>
							<div
								className="profile-icon"
								onClick={() => navigate("/profile")}
							>
								<p>&#x1F464;</p>
							</div>
						</div>
					</div>

					{/* Navigation items  */}
					<nav className="nav-tabs">
						<button className="nav-tab active">Home</button>
						<button className="nav-tab">My Requests</button>
						<button className="nav-tab">My Equipment</button>
						<button className="nav-tab">Dashboard</button>
						<button className="nav-tab">User Management</button>
					</nav>
				</header>
				{/* End of header component  */}

				{/* The title and brief description of the home page  */}
				<div className="hero-section">
					<h2>Equipment Overview</h2>
					<p>Manage and track farm equipment</p>
				</div>

				{/* Scrollable content  */}
				<div className="content">
					{equipment.map((item) => (
						<div key={item.id} className="equipment-card">
							<div className="card-header">
								{/* Add placeholder image later  */}
								<div className="equipment-image">
									<div className="image-placeholder"></div>
								</div>

								{/* Equipment details */}
								<div className="equipment-info">
									<h3>{item.name}</h3>

									{/* Show who has the equipment checked out
									If it's not checked out, keep blank line "Empty Text" (not visible) */}
									<p className="checkout-info">
										{item.checkedOutBy ? (
											<>
												<strong>Checked Out By:</strong> {item.checkedOutBy}
											</>
										) : (
											<span style={{ visibility: "hidden" }}>Empty Text</span>
										)}
									</p>

									{/* Show the status badge for the current equipment item
									It will be stylized depending on the status (checked out, damaged, etc) */}
									<div className="status-row">
										<span
											className={`status-badge ${getStatusClass(item.status)}`}
										>
											{item.status}
										</span>
										<label className="checkbox-label">
											<input type="checkbox" />
											Mark as Unavailable
										</label>
									</div>
								</div>
								{/* End of closed equipment card info  */}

								{/* Button state for opening and closing the equipment card  */}
								{/* Opens the selected card and closes any other card that was open */}
								{/* Replace with toggle icon later  */}
								<button
									className="expand-button"
									onClick={() =>
										setExpandedCard(expandedCard === item.id ? null : item.id)
									}
								>
									+
								</button>
							</div>

							{/* Expand the card that had the arrow selected  */}
							{/* Display all of its associated data  */}
							{expandedCard === item.id && (
								<div className="card-details">
									<div className="details-grid">
										<div className="details-column">
											<h4>Basic Information</h4>
											<div className="detail-row">
												<span className="label">Name</span>
												<span className="value">{item.model}</span>
											</div>
											<div className="detail-row">
												<span className="label">Category</span>
												<span className="value">{item.category}</span>
											</div>
											<div className="detail-row">
												<span className="label">Make</span>
												<span className="value">{item.make}</span>
											</div>
											<div className="detail-row">
												<span className="label">Model</span>
												<span className="value">{item.model}</span>
											</div>
										</div>

										<div className="details-column">
											<h4>Operations</h4>
											<div className="detail-row">
												<span className="label">Assigned Farm</span>
												<span className="value">{item.assignedFarm}</span>
											</div>
											<div className="detail-row">
												<span className="label">Use Frequency</span>
												<span className="value">{item.useFrequency}</span>
											</div>
											<div className="detail-row">
												<span className="label">Replacement Cost</span>
												<span className="value">{item.replacementCost}</span>
											</div>
										</div>

										<div className="details-column">
											<h4>Description</h4>
											{/* Read only on display, this can change when we open the 
											form to edit the equipment details */}
											<textarea
												className="description-textarea"
												value={item.description}
												readOnly
											/>
										</div>
									</div>

									{/* Bottom of the opened equipment card
									This is where users can view and attach files, edit details,
									checkout equipment item, or delete that item. */}
									<div className="card-footer">
										<div className="attachment-buttons">
											{/* Define how we want to do this later  */}
											<button className="link-button">
												View Attachments({item.attachments})
											</button>
											<button className="link-button">Upload</button>
										</div>
										<div className="action-buttons">
											<button className="btn-primary">Request Checkout</button>
											<button className="btn-primary">Edit Equipment</button>
											<button className="btn-danger">Delete</button>
										</div>
									</div>
								</div>
							)}
						</div>
					))}
				</div>
			</div>

			{/* 
			// From the original homepage, will likely be moved to the admin dashboard
			{activatePopup && (
				<EquipmentPopup
					onClose={() => setActivatePopup(false)}
					onSubmit={AddEquipment}
				/>
			)} */}
		</div>
	);
}

export default Home;
