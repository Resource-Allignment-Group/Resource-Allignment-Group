// This component is used on the My Equipment page
// Shows equipment currently checked out to the user
import "../styles/myequipment.css";
import { MdArrowForwardIos } from "react-icons/md";
import { useState } from "react";
import ReturnEquipmentModal from "./returnEquipmentWindow";
import { API_BASE } from "../config";
import { FaTractor } from "react-icons/fa";

function MyEquipmentCard({ equipment, isExpanded, onToggle }) {
	// Display return form
	const [showReturnModal, setShowReturnModal] = useState(false);

	// Open return form instead of returning equipment
	const handleReturnClick = () => {
		setShowReturnModal(true);
	};

	// Handle successful return
	const handleReturnSuccess = () => {
		// Refresh the page or update the equipment list
		window.location.reload();
	};

	return (
		<>
			<div className="my-equipment-card">
				<div className="card-header">
					<div className="equipment-image">
						{equipment.display_image &&
						equipment.images?.includes(equipment.display_image) ? (
							<img
								src={`http://${API_BASE}:5000/get_equipment_image/${equipment.id}/${equipment.display_image}`}
								alt={equipment.name}
								className="equipment-card-img"
							/>
						) : equipment.images?.length > 0 ? (
							<img
								src={`http://${API_BASE}:5000/get_equipment_image/${equipment.id}/${equipment.images[0]}`}
								alt={equipment.name}
								className="equipment-card-img"
							/>
						) : (
							<div className="image-placeholder">
								<FaTractor className="placeholder-icon" />
							</div>
						)}
					</div>

					{/* Equipment details */}
					<div className="equipment-info-less-text">
						<h3>{equipment.name}</h3>

						{/* Return Equipment button */}
						<button className="btn-primary" onClick={handleReturnClick}>
							Return Equipment
						</button>
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

						<div className="card-footer">
							<div className="attachments-section">
								<span className="attachments-label">Attachments</span>

								<div className="attachments-chips">
									{equipment.images?.map((imgId) => (
										<div key={`img-${imgId}`} className="attachment-chip">
											<span className="attachment-chip-name">Image</span>
											<a
												href={`http://${API_BASE}:5000/get_equipment_image/${equipment.id}/${imgId}`}
												target="_blank"
												rel="noopener noreferrer"
												className="chip-action-btn"
											>
												View
											</a>
										</div>
									))}

									{equipment.reports?.map((reportId) => (
										<div key={`rpt-${reportId}`} className="attachment-chip">
											<span className="attachment-chip-name">Report</span>
											<a
												href={`http://${API_BASE}:5000/get_equipment_report/${equipment.id}/${reportId}`}
												target="_blank"
												rel="noopener noreferrer"
												className="chip-action-btn"
											>
												Open
											</a>
										</div>
									))}

									{(!equipment.images || equipment.images.length === 0) &&
										(!equipment.reports || equipment.reports.length === 0) && (
											<span className="attachments-none">None</span>
										)}
								</div>
							</div>
						</div>
					</div>
				)}
			</div>
			{/* Form component for returning equipment */}
			<ReturnEquipmentModal
				isOpen={showReturnModal}
				onClose={() => setShowReturnModal(false)}
				equipment={equipment}
				onSuccess={handleReturnSuccess}
			/>
		</>
	);
}

export default MyEquipmentCard;
