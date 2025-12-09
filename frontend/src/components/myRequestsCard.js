// This component is used on the My Requests page
// Shows the user's pending, approved, or denied equipment requests
import "../styles/myrequests.css";
import { MdArrowForwardIos } from "react-icons/md";

function MyRequestsCard({ equipment, notification, isExpanded, onToggle }) {
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
				{/* Add placeholder image later  */}
				<div className="equipment-image">
					<div className="image-placeholder"></div>
				</div>

				{/* Equipment details */}
				<div className="equipment-info">
					<h3>{equipment.name}</h3>

					{/* Displays when the user requested to check out a piece of equipment */}
					<p className="checkout-info">
						<strong>Requested On:</strong> {notification.requestDate}
					</p>

					{/* Show the current state of the users equipment request. This will
					be replaced with content found in the notifications module*/}
					<div className="status-row">
						<span
							className={`status-badge ${getStatusClass(notification.notif)}`}
						>
							{notification.notif}
						</span>
					</div>
				</div>

				{/* Button state for opening and closing the equipment card  */}
				{/* Button state for opening and closing the equipment card  */}
				<button className={`expand-button ${isExpanded ? "rotated" : ""}`} onClick={onToggle}>
					<MdArrowForwardIos />
				</button>
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
								<span className="value">{equipment.category}</span>
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
								<span className="value">{equipment.assignedFarm}</span>
							</div>
							<div className="detail-row">
								<span className="label">Use Frequency</span>
								<span className="value">{equipment.useFrequency}</span>
							</div>
							<div className="detail-row">
								<span className="label">Replacement Cost</span>
								<span className="value">{equipment.replacementCost}</span>
							</div>
						</div>

						<div className="details-column">
							<h4>Description</h4>
							{/* "Read only" on display, this can change when we open the 
              				form to edit the equipment details */}
							<textarea
								className="description-textarea"
								value={equipment.description}
								readOnly
							/>
						</div>
					</div>

					{/* Bottom of the opened equipment card
          			This is where users can view and attach files, edit details,
          			checkout equipment item, or delete that item. */}
					<div className="card-footer">
						<div className="attachment-buttons">
							{/* Define how we want to do this later  */}
							<button className="link-button">
								View Attachments({equipment.attachments})
							</button>
							<button className="link-button">Upload</button>
						</div>
					</div>
				</div>
			)}
		</div>
	);
}

export default MyRequestsCard;
