import "../styles/default.css";
import { useState, useEffect } from "react";
import Header from "../components/header";
import Sidebar from "../components/sidebar";
import MyRequestsCard from "../components/myRequestsCard";
import { API_BASE } from "../config";
import { useSidebar } from "../SidebarContext";

function MyRequests({ num_of_notifications, setNumNotifications }) {
	const { sidebarOpen, openSidebar, closeSidebar } = useSidebar();
	const [expandedCard, setExpandedCard] = useState(null);
	const [requests, setRequests] = useState([]);

	useEffect(() => {
		const fillRequests = async () => {
			try {
				const res = await fetch(`http://${API_BASE}:5000/get_requests`, {
					credentials: "include",
				});

				const data = await res.json();
				const notifArray = data.notifications || [];
				const equipArray = data.equipment || [];
				// Pair each notification with its equipment directly
				const pairedRequests = notifArray.map((notif, index) => ({
					notification: notif,
					equipment: equipArray[index],
					id: notif._id,
				}));

				setRequests(pairedRequests.reverse());
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
					{requests.map((request) => (
						<MyRequestsCard
							key={request.id}
							equipment={request.equipment}
							notification={request.notification}
							isExpanded={expandedCard === request.id}
							onToggle={() => {
								setExpandedCard(
									expandedCard === request.id ? null : request.id,
								);
							}}
						/>
					))}
				</div>
			</div>
		</div>
	);
}

export default MyRequests;
