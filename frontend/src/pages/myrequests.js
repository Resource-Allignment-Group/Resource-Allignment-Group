import "../styles/default.css";
import { useState } from "react";

// Import componets that will make up the my requests page
import Header from "../components/header";
import Sidebar from "../components/sidebar";
import MyRequestsCard from "../components/myRequestsCard";

function MyRequests({num_of_notifications, setNumNotifications}) {
	const [sidebarOpen, setSidebarOpen] = useState(true);
	const [expandedCard, setExpandedCard] = useState(null);
	const [notifications, setNotifications] = useState([]);
	const [equipment, setEquipment] = useState([]);

	useEffect(() => {
		const fillNotification = async () => {
			try {
				const res = await fetch("http://localhost:5000/get_requests", {
					credentials: "include",
				});
				const data = await res.json();
				setNotifications(data.notifications || []);
				setEquipment(data.equipment || [])
			} catch (error) {
				console.log(error);
			}
		};
		fillNotification();
	}, []);

	// // Sample equipment data, will be replaced with backend data later
	// const equipment = [
	// 	{
	// 		id: 1,
	// 		name: "Tractor - John Deere 4040",
	// 		status: "Available",
	// 		category: "Tractor",
	// 		make: "John Deere",
	// 		model: "4040",
	// 		assignedFarm: "Aroostook",
	// 		useFrequency: "Seasonally",
	// 		replacementCost: "$120,000",
	// 		description:
	// 			'Back up for heavy tillage, used for 2" tillage. Used as spare if researchers need it, used for spreading waste potatoes.',
	// 		attachments: 0,
	// 	},
	// 	{
	// 		id: 2,
	// 		name: "Pneumatic Forklift - Yale",
	// 		status: "Damaged",
	// 		category: "Forklift",
	// 		make: "Yale",
	// 		model: "GP050VX",
	// 		assignedFarm: "Highmoor",
	// 		useFrequency: "Daily",
	// 		replacementCost: "$35,000",
	// 		description: "Indoor/outdoor forklift for material handling.",
	// 		attachments: 1,
	// 	},
	// 	{
	// 		id: 3,
	// 		name: "Snow Plow Truck - Ford",
	// 		status: "Checked Out",
	// 		checkedOutBy: "exampleUser@gmail.com",
	// 		category: "Truck",
	// 		make: "Ford",
	// 		model: "F-350",
	// 		assignedFarm: "Blueberry Hill",
	// 		useFrequency: "Seasonal",
	// 		replacementCost: "$75,000",
	// 		description: "Snow removal vehicle for winter maintenance operations.",
	// 		attachments: 2,
	// 	},
	// ];

	// // Sample notification data, will be replaced with backend data later
	// // Uses the equipment's ID's to access relevant notification for that piece
	// const notifications = {
    //     1: {
    //         requestDate: "Nov 12, 2025",
    //         notif: "Approved"
    //     },
    //     2: {
    //         requestDate: "Dec 1, 2025",
    //         notif: "Denied"
    //     },
	// 	3: {
    //         requestDate: "Dec 2, 2025",
    //         notif: "Pending"
    //     },
    // };

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
					num_of_notifications={num_of_notifications}
					setNotificationsNum={setNumNotifications}
				/>

				{/* The title and brief description of the my requests page  */}
				<div className="hero-section">
					<h2>My Requests</h2>
					<p>View and manage your equipment requests</p>
				</div>

				{/* Scrollable content  */}
				<div className="content">
					{/* Scrollable equipment items are a seperate component */}
					{equipment.map((item) => (
						<MyRequestsCard
							key={item.id}
							equipment={item}
							notification={notifications[item.id]}
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

export default MyRequests;
