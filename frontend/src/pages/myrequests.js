import "../styles/default.css";
import { useState, useEffect } from "react";
import Header from "../components/header";
import Sidebar from "../components/sidebar";
import MyRequestsCard from "../components/myRequestsCard";
import { API_BASE } from "../config";
import { useSidebar } from "../SidebarContext";

// Shows all equip requests the user has made
// Includes if they are pending, approved, declined

function MyRequests({ num_of_notifications, setNumNotifications }) {
	const { sidebarOpen, openSidebar, closeSidebar } = useSidebar();
	const [expandedCard, setExpandedCard] = useState(null);
	const [requests, setRequests] = useState([]);
	const [isLoading, setIsLoading] = useState(true);

	// Load all of the user's requests
	useEffect(() => {
		const fillRequests = async () => {
			try {
				setIsLoading(true);
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
			} finally {
				setIsLoading(false);
			}
		};
		fillRequests();
	}, []);

	// Allows users to dismiss equipment requests that have already
	// been flagged as approved or denied by an admin
	const handleDismissRequest = async (notificationToRemove) => {
		try {
			const prevRequests = requests;
			// Remove from UI immediately
			setRequests((prev) =>
				prev.filter((r) => r.notification._id !== notificationToRemove._id),
			);

			const res = await fetch(`http://${API_BASE}:5000/dismiss_notification`, {
				method: "POST",
				credentials: "include",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify({ notification: notificationToRemove }),
			});
			const data = await res.json();

			if (!res.ok || !data.result) {
				setRequests(prevRequests);
				alert(data.message);
			}
		} catch {
			alert("Failed to dismiss request");
		}
	};

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
					{isLoading ? (
						<div className="response-text">
							<p>Loading Requests...</p>
						</div>
					) : requests.length > 0 ? (
						requests.map((request) => (
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
								onDismiss={handleDismissRequest}
							/>
						))
					) : (
						<div className="response-text">
							<p>No pending requests found.</p>
						</div>
					)}
				</div>
			</div>
		</div>
	);
}

export default MyRequests;
