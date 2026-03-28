// Used on the notifications page
// Card component for each notification

import "../styles/notificationCard.css";
import { useState } from "react";
import { MdPerson } from "react-icons/md";
import { API_BASE } from "../config";
import { FaTractor } from "react-icons/fa";

// Notification card info for an equipment request
function NewRequestNotification({ notification, onApprove, onReject }) {
	const [status, setStatus] = useState(null);

	// When approved/denied, resolve the notif
	const handleApproveClick = () => {
		setStatus("approved");
		onApprove(notification);
	};
	const handleRejectClick = () => {
		setStatus("rejected");
		onReject(notification);
	};

	const equipmentImageUrl =
		notification.equipment_id && notification.equipment_display_image_id
			? `http://${API_BASE}:5000/get_equipment_image/${notification.equipment_id}/${notification.equipment_display_image_id}`
			: null;

	return (
		<div className="notification-card">
			<div className="notification-content">
				{/* Notification icon */}
				<div className="notification-icon-circle notification-icon-equipment">
					{equipmentImageUrl ? (
						<img
							src={equipmentImageUrl}
							alt=""
							className="notification-equipment-image"
						/>
					) : (
						<FaTractor />
					)}
				</div>

				{/* Notification details */}
				<div className="notification-info">
					<h3>New Equipment Request</h3>
					<p>
						<strong>{notification.body}</strong>
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

// Notification card info for new account creation
function NewAccountNotification({ notification, onApprove, onReject }) {
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
					<MdPerson />
				</div>

				{/* Notification details */}
				<div className="notification-info">
					<h3>New Account Request</h3>
					<p>
						<strong>{notification.sender_name}</strong> has requested a new
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

// Notification card info for generic data
function InformNotification({ notification, onDismiss }) {
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

// Establishes the unique notif cards
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
				/>
			);

		case "r": // request notification
			return (
				<NewRequestNotification
					notification={notification}
					onApprove={onApprove}
					onReject={onReject}
				/>
			);
		case "i": // general information notification
			return (
				<InformNotification notification={notification} onDismiss={onDismiss} />
			);
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
