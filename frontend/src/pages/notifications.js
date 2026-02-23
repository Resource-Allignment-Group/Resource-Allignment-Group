import "../styles/default.css";
import { useState, useEffect } from "react";
import Header from "../components/header";
import Sidebar from "../components/sidebar";
import NotificationCard from "../components/notificationCard";
import { API_BASE } from "../config";
import { useSidebar } from "../SidebarContext";

function Notifications({ num_of_notifications, setNumNotifications }) {
	const { sidebarOpen, openSidebar, closeSidebar } = useSidebar();
	const [notifications, setNotifications] = useState([]);
	const [isLoading, setIsLoading] = useState(true);

	useEffect(() => {
		const fillNotification = async () => {
			try {
				setIsLoading(true);

				const res = await fetch(`http://${API_BASE}:5000/get_notifications`, {
					credentials: "include",
				});

				if (!res.ok) {
					throw new Error(`Failed to fetch notifications: ${res.status}`);
				}

				const data = await res.json();
				setNotifications((data.messages || []).reverse());
			} catch {
				alert("Error Loading Notifications");
			} finally {
				setIsLoading(false);
			}
		};
		fillNotification();
	}, []);

	const handleNotification = async (notification, result) => {
		try {
			// Remove notif from UI first, revert if needed
			const prevNotifications = notifications;
			setNotifications((prev) =>
				prev.filter((n) => n._id !== notification._id),
			);
			setNumNotifications((num) => Math.max(0, num - 1));

			const res = await fetch(
				`http://${API_BASE}:5000/admin_account_decision`,
				{
					method: "POST",
					credentials: "include",
					headers: { "Content-Type": "application/json" },
					body: JSON.stringify({ result: result, notification: notification }),
				},
			);
			const data = await res.json();
			if (!data.result) {
				setNotifications(prevNotifications);
				setNumNotifications((num) => num + 1);
				alert(data.message || "Something went wrong");
			}
		} catch {
			// Revert on error
			setNotifications((prev) => [...prev, notification]);
			setNumNotifications((num) => num + 1);
			alert("Failed to process request. Please try again.");
		}
	};

	// Allows users to dismiss notifications
	const handleDismiss = async (notificationToRemove) => {
		try {
			// Update UI first for instant feedback
			const prevNotifications = notifications;
			setNotifications((prev) =>
				prev.filter((n) => n._id !== notificationToRemove._id),
			);
			setNumNotifications((num) => Math.max(0, num - 1));

			const res = await fetch(`http://${API_BASE}:5000/dismiss_notification`, {
				method: "POST",
				credentials: "include",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify({ notification: notificationToRemove }),
			});

			const data = await res.json();

			// If the API call fails, revert the prev quick update
			if (!res.ok || !data.result) {
				setNotifications(prevNotifications);
				setNumNotifications((num) => num + 1);
				alert(data.message || "Failed to dismiss notification");
			}
		} catch {
			// Revert on error
			setNotifications((prev) => [...prev, notificationToRemove]);
			setNumNotifications((num) => num + 1);
			alert("Failed to dismiss notification. Please try again.");
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
					activeTab="Notifications"
					num_of_notifications={num_of_notifications}
					setNotificationsNum={setNumNotifications}
				/>

				{/* The title and brief description of the notifications page  */}
				<div className="hero-section">
					<h2>Notifications</h2>
					<p>View all incoming notifications</p>
				</div>

				<div className="content">
					{isLoading ? (
						<div className="response-text">
							<p>Loading Notifications...</p>
						</div>
					) : notifications.length > 0 ? (
						notifications.map((n) => (
							<NotificationCard
								key={n._id}
								notification={n}
								onApprove={() => handleNotification(n, true)}
								onReject={() => handleNotification(n, false)}
								onDismiss={handleDismiss}
							/>
						))
					) : (
						<div className="response-text">
							<p>No notifications to display</p>
						</div>
					)}
				</div>
			</div>
		</div>
	);
}

export default Notifications;
