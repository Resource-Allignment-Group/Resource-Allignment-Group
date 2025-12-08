import "../styles/default.css";
import { useState } from "react";

// Import componets that will make up the home page
import Header from "../components/header";
import Sidebar from "../components/sidebar";
import HomeEquipmentCard from "../components/homeEquipmentCard";

function Home({num_of_notifications, setNumNotifications}) {
	const [sidebarOpen, setSidebarOpen] = useState(true);
	const [expandedCard, setExpandedCard] = useState(null);

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

	return (
		<div className="home-container">
			{/* Sidebar is a separate component */}
			<Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

			<div className="main">
				{/* Header is a separate component */}
				<Header
					sidebarOpen={sidebarOpen}
					onMenuToggle={() => setSidebarOpen(true)}
					activeTab="Home"
					num_of_notifications={num_of_notifications}
					setNotificationsNum={setNumNotifications}
				/>

				{/* The title and brief description of the home page  */}
				<div className="hero-section">
					<h2>Equipment Overview</h2>
					<p>Manage and track farm equipment</p>
				</div>

				{/* Scrollable content  */}
				<div className="content">
					{/* Scrollable equipment items are a seperate component */}
					{equipment.map((item) => (
						<HomeEquipmentCard
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

export default Home;
