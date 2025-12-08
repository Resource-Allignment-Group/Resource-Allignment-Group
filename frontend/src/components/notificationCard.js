// This component is used on the Notifications page
// Shows different types of notifications with actions

import "../styles/notificationCard.css";

function NotificationCard({ notification }) {
	// Determine icon based on notification type
	function getNotificationIcon(type) {
		if (type === "Request Approved") return "✓";
		if (type === "Equipment Damage Reported") return "⚠";
		if (type === "New Equipment Request") return "ℹ";
		if (type === "New Account Request") return "👤";
		return "";
	}

	// Determine icon color based on notification type
	function getIconClass(type) {
		if (type === "Request Approved") return "notification-icon-success";
		if (type === "Equipment Damage Reported") return "notification-icon-danger";
		if (type === "New Equipment Request") return "notification-icon-info";
		if (type === "New Account Request") return "notification-icon-account";
		return "";
	}

	return (
		<div className="notification-card">
			<div className="notification-content">
				{/* Notification icon */}
				<div
					className={`notification-icon-circle ${getIconClass(
						notification.type
					)}`}
				>
					<span>{getNotificationIcon(notification.type)}</span>
				</div>

				{/* Notification details */}
				<div className="notification-info">
					<h3>{notification.type}</h3>
					<p>{notification.message}</p>

					{/* Action buttons if applicable */}
					{notification.actions && (
						<div className="notification-actions">
							{notification.actions.includes("Approve") && (
								<button className="btn-success">Approve</button>
							)}
							{notification.actions.includes("Deny") && (
								<button className="btn-danger">Deny</button>
							)}
							{notification.actions.includes("View Details") && (
								<button className="btn-outline">View Details</button>
							)}
						</div>
					)}
				</div>

				{/* Dismiss button */}
				<button className="dismiss-button">✕</button>
			</div>
		</div>
	);
}

export default NotificationCard;
