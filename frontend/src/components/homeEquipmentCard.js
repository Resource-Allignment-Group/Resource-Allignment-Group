// This component is currently used on the home page

import "../styles/home.css";
import { MdArrowForwardIos } from "react-icons/md";
import { useAuth } from "../Authentication";
import { API_BASE } from "../config";
import { useState } from "react";

function HomeEquipmentCard({
	equipment,
	isExpanded,
	onToggle,
	isSelected,
	onSelect,
	onDelete,
}) {
	const { role } = useAuth();
	const isAdmin = role === "a";
	const [editedEquipment, setEquipment] = useState({
		id: equipment.id,
		name: equipment.name,
		category: equipment.class,
		make: equipment.make,
		model: equipment.model,
		farm: equipment.farm,
		use: equipment.use,
		replacementCost: equipment.replacementCost,
		description: equipment.description,
		damaged: equipment.damaged,
	});
	const [isEditing, setIsEditing] = useState(false);
	// Will check the status of the specific equipment item
	// It will display the stylized badge associated to that status
	function getEquipmentStatus({ checked_out, damaged, unavailable }) {
		if (unavailable) {
			return {
				label: "Unavailable",
				className: "status-unavailable",
			};
		}

		if (damaged) {
			return {
				label: "Damaged",
				className: "status-damaged",
			};
		}

		if (checked_out) {
			return {
				label: "Checked Out",
				className: "status-checked-out",
			};
		}

		return {
			label: "Available",
			className: "status-available",
		};
	}

	const handleCheckOut = async () => {
		// Don't let the user checkout equipment if it's been marked unavailable
		if (equipment.unavailable) {
			alert("This equipment is currently unavailble and can't be checked out.");
			return;
		}

		try {
			const res = await fetch(`http://${API_BASE}:5000/request_equipment`, {
				method: "POST",
				credentials: "include",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify({
					equip_id: equipment.id,
					equip_name: equipment.name,
				}),
			});
			const data = await res.json();
			if (data.result) {
				alert("Your Request Has Been Sent");
			} else {
				alert("Something Went Wrong With Your Request");
			}
		} catch (error) {
			alert("Failed to Checkout Equipment");
		}
	};

	const handleDelete = async () => {
		if (!isAdmin) {
			alert("Only administrators can delete equipment");
			return;
		}

		const confirmDelete = window.confirm(
			`Are you sure you want to delete "${equipment.name}"? `,
		);

		if (!confirmDelete) {
			return;
		}

		try {
			const res = await fetch(`http://${API_BASE}:5000/delete_equipment`, {
				method: "POST",
				credentials: "include",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify({
					equipment_id: equipment.id,
				}),
			});
			const data = await res.json();
			if (data.result) {
				alert("Equipment deleted successfully");
				if (onDelete) {
					onDelete();
				}
			} else {
				alert(data.message || "Failed to delete equipment");
			}
		} catch (error) {
			alert("There Were Problems Deleting The Equipment");
		}
	};

	const handleEquipmentEdit = async () => {
		setIsEditing(false);
		try {
			const res = await fetch(`http://${API_BASE}:5000/change_equipment_info`, {
				method: "POST",
				credentials: "include",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify({
					equipment: editedEquipment,
				}),
			});
			const data = await res.json();
			if (data.result) {
				alert("Equipment information changed successfully");
			} else {
				alert(data.message || "Failed to change equipment information");
			}
		} catch {
			alert("There Were Problems Changing The Equipment Information");
		}
	};
	const status = getEquipmentStatus(equipment); //this gets the information for the equipment cards to reference later in the div
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
						{equipment.checked_out && equipment.checkedOutBy && (
							<>
								<strong>Checked Out By:</strong> {equipment.checkedOutBy}
							</>
						)}
					</p>

					{/* Show the status badge for the current equipment item
          			It will be stylized depending on the status (checked out, damaged, etc) */}
					<div className="status-row">
						<span className={`status-badge ${status.className}`}>
							{status.label}
						</span>

						<div className="status-actions">
							<label className="checkbox-label">
								<input
									type="checkbox"
									checked={isSelected}
									onChange={() => onSelect(equipment.id)}
								/>
							</label>
							Mark Unavailable
						</div>
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
								<input
									className="equipment-value"
									type="text"
									value={editedEquipment.name}
									disabled={!isEditing}
									onChange={(e) =>
										setEquipment({
											...editedEquipment,
											name: e.target.value,
										})
									}
								/>
							</div>
							<div className="detail-row">
								<span className="label">Category</span>
								<input
									className="equipment-value"
									type="text"
									value={editedEquipment.category}
									disabled={!isEditing}
									onChange={(e) =>
										setEquipment({
											...editedEquipment,
											class: e.target.value,
										})
									}
								/>
							</div>
							<div className="detail-row">
								<span className="label">Make</span>
								<input
									className="equipment-value"
									type="text"
									value={editedEquipment.make}
									disabled={!isEditing}
									onChange={(e) =>
										setEquipment({
											...editedEquipment,
											make: e.target.value,
										})
									}
								/>
							</div>
							<div className="detail-row">
								<span className="label">Model</span>
								<input
									className="equipment-value"
									type="text"
									value={editedEquipment.model}
									disabled={!isEditing}
									onChange={(e) =>
										setEquipment({
											...editedEquipment,
											model: e.target.value,
										})
									}
								/>
							</div>
						</div>

						<div className="details-column">
							<h4>Operations</h4>
							<div className="detail-row">
								<span className="label">Assigned Farm</span>
								<input
									className="equipment-value"
									type="text"
									value={editedEquipment.farm}
									disabled={!isEditing}
									onChange={(e) =>
										setEquipment({
											...editedEquipment,
											farm: e.target.value,
										})
									}
								/>
							</div>
							<div className="detail-row">
								<span className="label">Use Frequency</span>
								<input
									className="equipment-value"
									type="text"
									value={editedEquipment.use}
									disabled={!isEditing}
									onChange={(e) =>
										setEquipment({
											...editedEquipment,
											use: e.target.value,
										})
									}
								/>
							</div>
							<div className="detail-row">
								<span className="label">Replacement Cost</span>
								<input
									className="equipment-value"
									type="text"
									value={editedEquipment.replacementCost}
									disabled={!isEditing}
									onChange={(e) =>
										setEquipment({
											...editedEquipment,
											replacementCost: e.target.value,
										})
									}
								/>
							</div>
							<div className="detail-row" hidden={!isEditing}>
								<span className="label">Damaged</span>
								<input
									className="equipment-value"
									type="checkbox"
									value={editedEquipment.damaged}
									checked={editedEquipment?.damaged || false}
									onChange={(e) =>
										setEquipment({
											...editedEquipment,
											damaged: e.target.checked,
										})
									}
								/>
							</div>
						</div>

						<div className="details-column">
							<h4>Description</h4>
							{/* "Read only" on display, this can change when we open the 
              				form to edit the equipment details */}
							<input
								className="equipment-value"
								type="text"
								value={editedEquipment.description}
								disabled={!isEditing}
								onChange={(e) =>
									setEquipment({
										...editedEquipment,
										description: e.target.value,
									})
								}
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
							<button
								className="btn-primary"
								onClick={handleCheckOut}
								hidden={equipment.checked_out}
							>
								Request Checkout
							</button>
							<button
								className="btn-primary"
								hidden={equipment.checked_out || isEditing || !isAdmin}
								onClick={() => setIsEditing(true)}
							>
								Edit Equipment
							</button>
							<button
								className="btn-primary"
								hidden={equipment.checked_out || !isEditing}
								onClick={handleEquipmentEdit}
							>
								Save
							</button>
							{isAdmin && (
								<button className="btn-danger" onClick={handleDelete}>
									Delete
								</button>
							)}
						</div>
					</div>
				</div>
			)}
		</div>
	);
}

export default HomeEquipmentCard;
