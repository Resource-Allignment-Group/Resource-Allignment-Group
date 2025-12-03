import "../styles/default.css";
import "../styles/notificationPage.css"
import { useState, useEffect } from "react";
import NotificationItem from "../components/notification";
import Header from "../components/header";
import Sidebar from "../components/sidebar";

function Notifications() {
	const [sidebarOpen, setSidebarOpen] = useState(true);
	const [notifications, setNotifications] = useState([])

	useEffect(() => {
		const fillNotification = async () => {
			try {
				const res = await fetch("http://localhost:5000/get_notifications", {
					credentials: "include"
				})
				const data = await res.json()
				setNotifications(data.messages || [])
			}
			catch (error) {
				console.log(error)
			}
		}
		fillNotification()
		}, [])
	
	const handleApprove = (notification) => {
		//Handle this later
	}

	const handleReject = (notification) => {
		//Handle this later
	}

	return (
		<div className="home-container">
			{/* Sidebar is a separate component */}
			<Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

			<div className="main">
				{/* Header is a separate component */}
				<Header
					sidebarOpen={sidebarOpen}
					onMenuToggle={() => setSidebarOpen(true)}
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
								onApprove={handleApprove}
								onReject={handleReject}
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
