import "../styles/default.css";
import { useState } from "react";

// Import componets that will make up the my equipment page
import Header from "../components/header";
import Sidebar from "../components/sidebar";
import MyEquipmentCard from "../components/myEquipmentCard";

function MyEquipment({num_of_notifications, setNumNotifications}) {
	const [sidebarOpen, setSidebarOpen] = useState(true);
	const [expandedCard, setExpandedCard] = useState(null);

	// Sample equipment data, will be replaced with backend info later
	const equipment = [
		{
			id: 1,
			name: "Snow Plow Truck - Ford",
			status: "Checked Out",
			checkedOutBy: "exampleUser@gmail.com",
			checkedOutDate: "Nov 12, 2025",
			category: "Truck",
			make: "Ford",
			model: "F-350",
			assignedFarm: "Blueberry Hill",
			useFrequency: "Seasonal",
			replacementCost: "$75,000",
			description: "Snow removal vehicle for winter maintenance operations.",
			attachments: 2,
		},
	];

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
					num_of_notifications={num_of_notifications}
					setNotificationsNum={setNumNotifications}
				/>

				{/* The title and brief description of the my equipment page  */}
				<div className="hero-section">
					<h2>My Equipment</h2>
					<p>Equipment currently checked out to you</p>
				</div>

				{/* Scrollable content  */}
				<div className="content">
					{/* Scrollable equipment items are a seperate component */}
					{equipment.map((item) => (
						<MyEquipmentCard
							key={item.id}
							equipment={item}
							isExpanded={expandedCard === item.id}
							onToggle={() =>
								setExpandedCard(expandedCard === item.id ? null : item.id)
							}
						/>
					))}
				</div>
			</div>
		</div>
	);
}

export default MyEquipment;
