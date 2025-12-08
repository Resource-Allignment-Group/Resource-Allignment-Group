import "../styles/default.css";
import "../styles/notificationPage.css";
import { useState, useEffect } from "react";
import NotificationItem from "../components/notification";
import Header from "../components/header";
import Sidebar from "../components/sidebar";
import NotificationCard from "../components/notificationCard";

function Notifications({ num_of_notifications, setNumNotifications }) {
	const [sidebarOpen, setSidebarOpen] = useState(true);
	const [notifications, setNotifications] = useState([]);

	useEffect(() => {
		const fillNotification = async () => {
			try {
				const res = await fetch("http://localhost:5000/get_notifications", {
					credentials: "include",
				});
				const data = await res.json();
				setNotifications(data.messages || []);
			} catch (error) {
				console.log(error);
			}
		};
		fillNotification();
	}, []);

	const handleNotification = async (notification, result) => {
		try {
			const res = await fetch("http://localhost:5000/admin_account_decision", {
				method: "POST",
				credentials: "include",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify({ result: result, notification: notification }),
			});
			const data = await res.json();
			if (result) {
				setNumNotifications((num) => num - 1); //this doesnt work but I am working on it
			}
			//change notification to an inform class
		} catch (error) {
			console.log(error);
			alert("Something went wrong");
		}
	};

	return (
		<div className="home-container">
			{/* Sidebar is a separate component */}
			<Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

			<div className="main">
				{/* Header is a separate component */}
				<Header
					sidebarOpen={sidebarOpen}
					onMenuToggle={() => setSidebarOpen(true)}
					num_of_notifications={num_of_notifications}
					setNotificationsNum={setNumNotifications}
				/>

				{/* The title and brief description of the notifications page  */}
				<div className="hero-section">
					<h2>Notifications</h2>
					<p>View all incoming notifications</p>
				</div>

				<div className="notifications-list">
					{notifications.length > 0 ? (
						notifications.map((n, i) => (
							<NotificationItem
								key={i}
								notification={n}
								onApprove={() => handleNotification(n, true)}
								onReject={() => handleNotification(n, false)}
							/>
						))
					) : (
						<p>No notifications</p>
					)}
				</div>
			</div>
		</div>
	);
}

export default Notifications;
