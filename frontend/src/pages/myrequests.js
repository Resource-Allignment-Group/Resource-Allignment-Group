import "../styles/default.css";
import { useState, useEffect } from "react";

import Header from "../components/header";
import Sidebar from "../components/sidebar";
import MyRequestsCard from "../components/myRequestsCard";

function MyRequests({ num_of_notifications, setNumNotifications }) {
	const [sidebarOpen, setSidebarOpen] = useState(true);
	const [expandedCard, setExpandedCard] = useState(null);

	const [notifications, setNotifications] = useState([]);
	const [equipment, setEquipment] = useState([]);

	// notifications get connected to their equipment
	const [notificationsByEquipment, setNotificationsByEquipment] = useState({});

	useEffect(() => {
		const fillRequests = async () => {
			try {
				const res = await fetch("http://localhost:5000/get_requests", {
					credentials: "include",
				});

				const data = await res.json();

				const notifArray = data.notifications || [];
				const equipArray = data.equipment || [];

				setNotifications(notifArray);
				setEquipment(equipArray);

				//this creates the mapping of equipment and notification
				const notifMap = {};
				for (const notif of notifArray) {
					notifMap[notif.equipment_id] = notif;
				}
				setNotificationsByEquipment(notifMap);
			
			} catch (error) {
				console.error("Failed to load requests:", error);
			}
		};

		fillRequests();
	}, []);

	return (
		<div className="home-container">
			<Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

			<div className="main">
				<Header
					sidebarOpen={sidebarOpen}
					onMenuToggle={() => setSidebarOpen(true)}
					activeTab="My Requests"
					num_of_notifications={num_of_notifications}
					setNotificationsNum={setNumNotifications}
				/>

				<div className="hero-section">
					<h2>My Requests</h2>
					<p>View and manage your equipment requests</p>
				</div>

				<div className="content">
					{equipment.map((item) => {
						const notif = notificationsByEquipment[item.id];
	
						return (
							<MyRequestsCard
								key={item.id}
								equipment={item}
								notification={notif}
								isExpanded={expandedCard === item.id}
								onToggle={() =>
									setExpandedCard(
										expandedCard === item.id ? null : item.id
									)
								}
							/>
						);
					})}
				</div>
			</div>
		</div>
	);
}

export default MyRequests;