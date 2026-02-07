import "../styles/default.css";
import { useState, useEffect } from "react";

import Header from "../components/header";
import Sidebar from "../components/sidebar";
import MyRequestsCard from "../components/myRequestsCard";
import { API_BASE } from "../config";
function MyRequests({ num_of_notifications, setNumNotifications }) {
	const { sidebarOpen, openSidebar, closeSidebar } = useSidebar();
	const [expandedCard, setExpandedCard] = useState(null);
	const [notifications, setNotifications] = useState([]);
	const [equipment, setEquipment] = useState([]);

	// notifications get connected to their equipment
	const [notificationsByEquipment, setNotificationsByEquipment] = useState({});

	useEffect(() => {
		const fillRequests = async () => {
			try {
				const res = await fetch(`http://${API_BASE}:5000/get_requests`, {
					credentials: "include",
				});

				const data = await res.json();

				const notifArray = data.notifications || [];
				const equipArray = data.equipment || [];

				setNotifications(notifArray);
				setEquipment(equipArray.reverse());

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
			<Sidebar isOpen={sidebarOpen} onClose={closeSidebar} />

			<div className="main">
				<Header
					sidebarOpen={sidebarOpen}
					onMenuToggle={openSidebar}
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
						// Use notification ID if available, otherwise use equipment ID
						const cardId = notif?._id || notif?.id || item.id;
						return (
							<MyRequestsCard
								key={cardId}
								equipment={item}
								notification={notif}
								isExpanded={expandedCard === cardId}
								onToggle={() => {
									setExpandedCard(expandedCard === cardId ? null : cardId);
								}}
							/>
						);
					})}
				</div>
			</div>
		</div>
	);
}

export default MyRequests;
