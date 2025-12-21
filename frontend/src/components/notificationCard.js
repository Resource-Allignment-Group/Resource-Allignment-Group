import "../styles/notificationCard.css";
import { useState } from "react";

function NewRequestNotification({
	notification,
	onApprove,
	onReject,
	onDismiss,
}){
	const [status, setStatus] = useState(null)

	const handleApproveClick = () => {
		setStatus("approved");
		onApprove(notification);
	};

	const handleRejectClick = () => {
		setStatus("rejected");
		onReject(notification);
	};
	return (
		<div className="notification-card">
			<div className="notification-content">
				{/* Notification icon */}
				<div className="notification-icon-circle notification-icon-account">
					<span>
						🚜
						{/* This is where we should put the profile picture for the equipment */}
					</span>
				</div>

				{/* Notification details */}
				<div className="notification-info">
					<h3>New Equipment Request</h3>
					<p>
						<strong>{notification.sender_username}</strong> has requested a new
						account.
					</p>

					{/* Action buttons */}
					{status === null && (
						<div className="notification-actions">
							<button className="btn-success" onClick={handleApproveClick}>
								Approve
							</button>
							<button className="btn-danger" onClick={handleRejectClick}>
								Reject
							</button>
						</div>
					)}

					{status === "approved" && (
						<div className="notification-actions">
							<p className="notification-status approved">✓ Approved</p>
						</div>
					)}

					{status === "rejected" && (
						<div className="notification-actions">
							<p className="notification-status rejected">✕ Rejected</p>
						</div>
					)}
				</div>

				<span className="notification-date">
					{new Date(notification.date).toLocaleString()}
				</span>

			</div>
		</div>
	);
}

function NewAccountNotification({
	notification,
	onApprove,
	onReject,
	onDismiss,
}) {
	const [status, setStatus] = useState(null);

	const handleApproveClick = () => {
		setStatus("approved");
		onApprove(notification);
	};

	const handleRejectClick = () => {
		setStatus("rejected");
		onReject(notification);
	};

	return (
		<div className="notification-card">
			<div className="notification-content">
				{/* Notification icon */}
				<div className="notification-icon-circle notification-icon-account">
					<span>👤</span>
				</div>

				{/* Notification details */}
				<div className="notification-info">
					<h3>New Account Request</h3>
					<p>
						<strong>{notification.sender_username}</strong> has requested a new
						account.
					</p>

					{/* Action buttons */}
					{status === null && (
						<div className="notification-actions">
							<button className="btn-success" onClick={handleApproveClick}>
								Approve
							</button>
							<button className="btn-danger" onClick={handleRejectClick}>
								Reject
							</button>
						</div>
					)}

					{status === "approved" && (
						<div className="notification-actions">
							<p className="notification-status approved">✓ Approved</p>
						</div>
					)}

					{status === "rejected" && (
						<div className="notification-actions">
							<p className="notification-status rejected">✕ Rejected</p>
						</div>
					)}
				</div>

				<span className="notification-date">
					{new Date(notification.date).toLocaleString()}
				</span>

				{/* Dismiss button */}
				{onDismiss && (
					<button
						className="dismiss-button"
						onClick={() => onDismiss(notification)}
					>
						✕
					</button>
				)}
			</div>
		</div>
	);
}



export default function NotificationCard({
	notification,
	onApprove,
	onReject,
	onDismiss,
}) {
	switch (notification.type) {
		case "a": // New account notification
			return (
				<NewAccountNotification
					notification={notification}
					onApprove={onApprove}
					onReject={onReject}
					onDismiss={onDismiss}
				/>
			);
		
		case 'r': // request notification
			return 
			<NewRequestNotification
				notification={notification}
				onApprove={onApprove}
				onReject={onReject}
				onDismiss={onDismiss}
			/>
		default:
			return (
				<div className="notification-card">
					<div className="notification-content">
						<div className="notification-icon-circle notification-icon-info">
							<span>ℹ</span>
						</div>
						<div className="notification-info">
							<h3>Notification</h3>
							<p>{notification.body}</p>
						</div>

						<span className="notification-date">
							{new Date(notification.date).toLocaleString()}
						</span>

						{onDismiss && (
							<button
								className="dismiss-button"
								onClick={() => onDismiss(notification)}
							>
								✕
							</button>
						)}
					</div>
				</div>
			);
	}
}
