// This component is currently used on the home page

import "../styles/home.css";
import { MdArrowForwardIos } from "react-icons/md";

function HomeEquipmentCard({ equipment, isExpanded, onToggle }) {
	// Will check the status of the specific equipment item
	// It will display the stylized badge associated to that status
	function getStatusClass(checked_out) {
		if (checked_out === "Available") return "status-available";
		if (checked_out === "Checked Out") return "status-checked-out";
		if (checked_out === "Damaged") return "status-damaged";
		return "";
	}

	return (
		<div className="equipment-card">
			<div className="card-header">
				{/* Add placeholder image later  */}
				<div className="equipment-image">
					<div className="image-placeholder"></div>
				</div>

				{/* Equipment details */}
				<div className="equipment-info">
					<h3>{equipment.name}</h3>

					{/* Show who has the equipment checked out
          			If it's not checked out, keep blank line "Empty Text" (not visible) */}
					<p className="checkout-info">
					{equipment.checked_out === "Checked Out" && equipment.checkedOutBy && (
						<>
						<strong>Checked Out By:</strong> {equipment.checkedOutBy}
						</>
					)}
					</p>

					{/* Show the status badge for the current equipment item
          			It will be stylized depending on the status (checked out, damaged, etc) */}
					<div className="status-row">
						<span
							className={`status-badge ${getStatusClass(equipment.checked_out)}`}
						>
							{equipment.checked_out}
						</span>
						<label className="checkbox-label">
							Mark as Unavailable
							<input type="checkbox" />
						</label>
					</div>
				</div>

				{/* Button state for opening and closing the equipment card  */}
				<button
					className={`expand-button ${isExpanded ? "rotated" : ""}`}
					onClick={onToggle}
				>
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
						<div className="action-buttons">
							<button className="btn-primary">Request Checkout</button>
							<button className="btn-primary">Edit Equipment</button>
							<button className="btn-danger">Delete</button>
						</div>
					</div>
				</div>
			)}
		</div>
	);
}

export default HomeEquipmentCard;
