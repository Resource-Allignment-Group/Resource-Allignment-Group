// This component is used on the My Equipment page
// Shows equipment currently checked out to the user
import "../styles/myequipment.css";
import { MdArrowForwardIos } from "react-icons/md";
import { useState } from "react";
import ReturnEquipmentModal from "./returnEquipmentWindow";
import { API_BASE } from "../config";

function MyEquipmentCard({ equipment, isExpanded, onToggle }) {
	// Display return form
	const [showReturnModal, setShowReturnModal] = useState(false);

	// Open return form instead of returning equipment
	const handleReturnClick = () => {
		setShowReturnModal(true);

		const ReturnEquipment = async () => {
			try {
				const res = await fetch(`http://${API_BASE}:5000/return_equipment`, {
					method: "POST",
					headers: { "Content-Type": "application/json" },
					credentials: "include",
					body: JSON.stringify({
						equipment_id: equipment.id,
					}),
				});
				const data = await res.json();
				if (data.result) {
					alert("Your Equipment has been returned");
				} else {
					alert(
						"Something Has Gone Wrong, Please Refresh Your Page to See if Your Equipment was Returned",
					);
				}
			} catch (error) {
				console.log(error);
			}
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
						{/* Add placeholder image later  */}
						<div className="equipment-image">
							<div className="image-placeholder"></div>
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
										<span className="value">{equipment.useFrequency}</span>
									</div>
									<div className="detail-row">
										<span className="label">Replacement Cost</span>
										<span className="value">{equipment.replacementCost}</span>
									</div>
								</div>

								<div className="details-column">
									<h4>Description</h4>
									<textarea
										className="description-textarea"
										value={equipment.description}
										readOnly
									/>
								</div>
							</div>

							<div className="card-footer">
								<div className="attachment-buttons">
									<button className="link-button">
										View Attachments({equipment.attachments})
									</button>
									<button className="link-button">Upload</button>
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
	};
}

export default MyEquipmentCard;
