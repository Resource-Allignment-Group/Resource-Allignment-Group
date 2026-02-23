// This component is used on the My Requests page
// Shows the user's pending, approved, or denied equipment requests
import "../styles/myrequests.css";
import { MdArrowForwardIos } from "react-icons/md";
import { API_BASE } from "../config";

function MyRequestsCard({
	equipment,
	notification,
	isExpanded,
	onToggle,
	onDismiss,
}) {
	const STATUS_MAP = {
		a: "Approved",
		p: "Pending",
		r: "Denied",
	};

	//defaults to pending if it does not have one, we should be implimenting these fail-safes  more when we get the chance
	const rawStatus = notification?.status ?? "p";
	const status = STATUS_MAP[rawStatus] ?? "Pending";

	// Will check the status of the specific equipment item
	// It will display the stylized badge associated to that status
	function getStatusClass(status) {
		if (status === "Approved") return "status-approved";
		if (status === "Pending") return "status-pending";
		if (status === "Denied") return "status-denied";
		return "";
	}

	return (
		<div className="my-requests-card">
			<div className="card-header">
				<div className="equipment-image">
					{equipment.display_image && equipment.images?.includes(equipment.display_image) ? (
						<img src={`http://${API_BASE}:5000/get_equipment_image/${equipment.id}/${equipment.display_image}`} alt={equipment.name} className="equipment-card-img" />
					) : equipment.images?.length > 0 ? (
						<img src={`http://${API_BASE}:5000/get_equipment_image/${equipment.id}/${equipment.images[0]}`} alt={equipment.name} className="equipment-card-img" />
					) : (
						<div className="image-placeholder"></div>
					)}
				</div>

				{/* Equipment details */}
				<div className="equipment-info">
					<h3>{equipment.name}</h3>

					{/* Displays when the user requested to check out a piece of equipment */}
					<p className="checkout-info">
						<strong>Requested On:</strong> {notification.date}
					</p>

					{/* Show the current state of the users equipment request. This will
					be replaced with content found in the notifications module*/}
					<div className="status-row">
						<span className={`status-badge ${getStatusClass(status)}`}>
							{status}
						</span>
					</div>
				</div>

				{/* Button state for opening and closing the equipment card  */}
				{/* Button state for opening and closing the equipment card  */}
				<button
					className={`expand-button ${isExpanded ? "rotated" : ""}`}
					onClick={onToggle}
				>
					<MdArrowForwardIos />
				</button>

				{/* The button for users to dismiss old equip requests approved/denied */}
				{(notification.status === "a" || notification.status === "r") && (
					<button
						className="dismiss-button"
						onClick={() => onDismiss(notification)}
					>
						✕
					</button>
				)}
			</div>

			{/* Expand the card that had the arrow selected  */}
			{/* Display all of its associated data  */}
			{isExpanded && (
				<div className="card-details">
					<div className="details-grid">
						<div className="details-column">
							<h4>Basic Information</h4>
							<div className="detail-row">
								<span className="label">Name</span>
								<span className="value">{equipment.name}</span>
							</div>
							<div className="detail-row">
								<span className="label">Category</span>
								<span className="value">{equipment.class}</span>
							</div>
							<div className="detail-row">
								<span className="label">Make</span>
								<span className="value">{equipment.make}</span>
							</div>
							<div className="detail-row">
								<span className="label">Model</span>
								<span className="value">{equipment.model}</span>
							</div>
						</div>

						<div className="details-column">
							<h4>Operations</h4>
							<div className="detail-row">
								<span className="label">Assigned Farm</span>
								<span className="value">{equipment.farm}</span>
							</div>
							<div className="detail-row">
								<span className="label">Use Frequency</span>
								<span className="value">{equipment.use}</span>
							</div>
							<div className="detail-row">
								<span className="label">Replacement Cost</span>
								<span className="value">{equipment.replacement_cost}</span>
							</div>
						</div>

						<div className="details-column">
							<h4>Description</h4>

							<div className="detail-row description-row">
								<span className="label">Details</span>
								<span className="value description-value">
									{equipment.description}
								</span>
							</div>
						</div>
					</div>

					{/* Bottom of the opened equipment card
          			This is where users can view and attach files, edit details,
          			checkout equipment item, or delete that item. */}
					<div className="card-footer">
						<div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
							<div style={{ display: "flex", alignItems: "flex-start", gap: 8 }}>
								<span style={{ fontWeight: 500, flexShrink: 0 }}>Attachments:</span>
								<div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
									{equipment.images?.map((imgId) => (
										<div key={imgId} style={{ display: "flex", alignItems: "center", gap: 8 }}>
											<span style={{ fontSize: 14 }}>Image</span>
											<a href={`http://${API_BASE}:5000/get_equipment_image/${equipment.id}/${imgId}`} target="_blank" rel="noopener noreferrer" className="link-button" style={{ color: "#1976d2" }}>View</a>
										</div>
									))}
									{equipment.reports?.map((reportId) => (
										<div key={reportId} style={{ display: "flex", alignItems: "center", gap: 8 }}>
											<span style={{ fontSize: 14 }}>Report (PDF)</span>
											<a href={`http://${API_BASE}:5000/get_equipment_report/${equipment.id}/${reportId}`} target="_blank" rel="noopener noreferrer" className="link-button" style={{ color: "#1976d2" }}>Open</a>
										</div>
									))}
									{((!equipment.images || equipment.images.length === 0) && (!equipment.reports || equipment.reports.length === 0)) && (
										<span style={{ color: "#666", fontSize: 14 }}>None</span>
									)}
								</div>
							</div>
						</div>
					</div>
				</div>
			)}
		</div>
	);
}

export default MyRequestsCard;
