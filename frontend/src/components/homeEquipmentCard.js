// Used on the home page
// Is the card modal to show equipment details

import "../styles/home.css";
import { MdArrowForwardIos } from "react-icons/md";
import { useAuth } from "../Authentication";
import { API_BASE } from "../config";
import { useState } from "react";
import { FaTractor } from "react-icons/fa";

function HomeEquipmentCard({
	equipment,
	isExpanded,
	onToggle,
	isSelected,
	onSelect,
	onEdit,
	onDelete,
	onRefresh,
}) {
	const { role } = useAuth();
	// Role 'a' = admin
	const isAdmin = role === "a";
	const [editedEquipment, setEquipment] = useState({
		id: equipment.id,
		name: equipment.name,
		class: equipment.class,
		make: equipment.make,
		model: equipment.model,
		farm: equipment.farm,
		use: equipment.use,
		replacement_cost: equipment.replacement_cost,
		description: equipment.description,
		damaged: equipment.damaged,
	});
	const [isEditing, setIsEditing] = useState(false);
	const [uploadingFile, setUploadingFile] = useState(false);
	const imageUrl =
		equipment.display_image &&
		equipment.images &&
		equipment.images.includes(equipment.display_image)
			? `http://${API_BASE}:5000/get_equipment_image/${equipment.id}/${equipment.display_image}`
			: equipment.images && equipment.images.length > 0
				? `http://${API_BASE}:5000/get_equipment_image/${equipment.id}/${equipment.images[0]}`
				: null;

	// Current equipment status matched to its unique styling in CSS
	function getEquipmentStatus({ checked_out, damaged, unavailable }) {
		if (unavailable)
			return { label: "Unavailable", className: "status-unavailable" };
		if (damaged) return { label: "Damaged", className: "status-damaged" };
		if (checked_out)
			return { label: "Checked Out", className: "status-checked-out" };
		return { label: "Available", className: "status-available" };
	}

	// Handles user checking out equipment + edge cases
	const handleCheckOut = async () => {
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
				alert(data.message || "Failed to Request Equipment");
			}
		} catch (error) {
			alert("Failed to Checkout Equipment");
		}
	};

	// Triggers equip deletion
	const handleDelete = () => {
		onDelete(equipment.id, equipment.name);
	};

	// Allow admins to attach files to the equipment
	const handleFileUpload = async (e, fileType) => {
		const file = e.target.files?.[0];
		if (!file) return;
		const MAX_IMAGE = 5 * 1024 * 1024;
		const MAX_REPORT = 10 * 1024 * 1024;
		if (
			fileType === "image" &&
			(file.size > MAX_IMAGE ||
				!["image/png", "image/jpeg", "image/jpg"].includes(file.type))
		) {
			alert("Image must be PNG/JPG and under 5MB");
			return;
		}
		if (
			fileType === "report" &&
			(file.size > MAX_REPORT || file.type !== "application/pdf")
		) {
			alert("Report must be PDF and under 10MB");
			return;
		}
		setUploadingFile(true);
		try {
			const formData = new FormData();
			formData.append("equipment_id", equipment.id);
			formData.append("file_type", fileType);
			formData.append("file", file);
			const res = await fetch(`http://${API_BASE}:5000/upload_equipment_file`, {
				method: "POST",
				credentials: "include",
				body: formData,
			});
			const data = await res.json();
			if (data.result) onRefresh?.();
			else alert(data.message || "Upload failed");
		} catch {
			alert("Upload failed");
		} finally {
			setUploadingFile(false);
			e.target.value = "";
		}
	};

	// Admins can also set the display image based on images attached to that equipment
	const handleSetDisplayImage = async (imageId) => {
		try {
			const res = await fetch(
				`http://${API_BASE}:5000/set_equipment_display_image`,
				{
					method: "POST",
					credentials: "include",
					headers: { "Content-Type": "application/json" },
					body: JSON.stringify({
						equipment_id: equipment.id,
						image_id: imageId,
					}),
				},
			);
			const data = await res.json();
			if (data.result) onRefresh?.();
			else alert(data.message || "Failed to set display image");
		} catch {
			alert("Failed to set display image");
		}
	};

	// Removes files from the equipment
	const handleRemoveFile = async (fileId, fileType) => {
		if (!window.confirm(`Remove this ${fileType}?`)) return;
		try {
			const res = await fetch(`http://${API_BASE}:5000/remove_equipment_file`, {
				method: "POST",
				credentials: "include",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify({
					equipment_id: equipment.id,
					file_id: fileId,
					file_type: fileType,
				}),
			});
			const data = await res.json();
			if (data.result) onRefresh?.();
			else alert(data.message || "Failed to remove file");
		} catch {
			alert("Failed to remove file");
		}
	};

	// Allows admins to edit equip form fields
	const handleEquipmentEdit = () => {
		setIsEditing(false);
		onEdit(editedEquipment);
	};

	const status = getEquipmentStatus(equipment);
	const hasAttachments =
		equipment.images?.length > 0 || equipment.reports?.length > 0;

	return (
		// Equip card info: title, who has it checked out, ability to mark unavailable
		<div className="equipment-card">
			<div className="card-header">
				<div className="equipment-image">
					{imageUrl ? (
						<img
							src={imageUrl}
							alt={equipment.name}
							className="equipment-card-img"
						/>
					) : (
						<div className="image-placeholder">
							<FaTractor className="placeholder-icon" />
						</div>
					)}
				</div>

				<div className="equipment-info">
					<h3>{equipment.name}</h3>
					<p className="checkout-info">
						{equipment.checked_out && equipment.checkedOutBy && (
							<>
								<strong>Checked Out By:</strong> {equipment.checkedOutBy}
							</>
						)}
					</p>
					<div className="status-row">
						<span className={`status-badge ${status.className}`}>
							{status.label}
						</span>
						{isAdmin && (
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
						)}
					</div>
				</div>

				<button
					className={`expand-button ${isExpanded ? "rotated" : ""}`}
					onClick={onToggle}
				>
					<MdArrowForwardIos />
				</button>
			</div>

			{/* Displayed when the card is expanded */}
			{isExpanded && (
				<div className="card-details">
					<div className="details-grid">
						<div className="details-column">
							{/* General equipment information */}
							<h4>Basic Information</h4>
							<div className="detail-row">
								<span className="label">Name</span>
								<input
									className="equipment-value"
									type="text"
									value={editedEquipment.name}
									disabled={!isEditing}
									onChange={(e) =>
										setEquipment({ ...editedEquipment, name: e.target.value })
									}
								/>
							</div>
							<div className="detail-row">
								<span className="label">Class</span>
								<input
									className="equipment-value"
									type="text"
									value={editedEquipment.class}
									disabled={!isEditing}
									onChange={(e) =>
										setEquipment({ ...editedEquipment, class: e.target.value })
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
										setEquipment({ ...editedEquipment, make: e.target.value })
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
										setEquipment({ ...editedEquipment, model: e.target.value })
									}
								/>
							</div>
						</div>
						{/* Operational data for equipment */}
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
										setEquipment({ ...editedEquipment, farm: e.target.value })
									}
								/>
							</div>
							<div className="detail-row">
								<span className="label">Use</span>
								<input
									className="equipment-value"
									type="text"
									value={editedEquipment.use}
									disabled={!isEditing}
									onChange={(e) =>
										setEquipment({ ...editedEquipment, use: e.target.value })
									}
								/>
							</div>
							<div className="detail-row">
								<span className="label">Replacement Cost</span>
								<input
									className="equipment-value"
									type="number"
									value={editedEquipment.replacement_cost}
									disabled={!isEditing}
									onChange={(e) =>
										setEquipment({
											...editedEquipment,
											replacement_cost: Number(e.target.value),
										})
									}
								/>
							</div>
							{/* Allows admins to manually flag/un-flag equip as damaged */}
							<div className="detail-row">
								{isEditing && (
									<>
										<span className="label">Damaged</span>
										<input
											type="checkbox"
											checked={editedEquipment?.damaged || false}
											onChange={(e) =>
												setEquipment({
													...editedEquipment,
													damaged: e.target.checked,
												})
											}
										/>
									</>
								)}
							</div>
						</div>
						{/* Description of the equipment item */}
						<div className="details-column">
							<h4>Description</h4>
							<textarea
								className="equipment-value description-field"
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

					<div className="card-footer">
						{/* Left side: attachments above, upload buttons below (edit only) */}
						<div className="attachments-section">
							<span className="attachments-label">Attachments</span>
							<div className="attachments-chips">
								{!hasAttachments && (
									<span className="attachments-none">None</span>
								)}
								{/* All of the icons for attached images (if any) */}
								{equipment.images?.map((imgId) => (
									<div key={`img-${imgId}`} className="attachment-chip">
										<span className="attachment-chip-name">
											Image
											{equipment.display_image === imgId && (
												<span className="display-badge">Display</span>
											)}
										</span>
										<a
											href={`http://${API_BASE}:5000/get_equipment_image/${equipment.id}/${imgId}`}
											target="_blank"
											rel="noopener noreferrer"
											className="chip-action-btn"
										>
											View
										</a>
										{/* Allows an admin to set an image as the display image */}
										{equipment.display_image !== imgId &&
											isAdmin &&
											isEditing && (
												<button
													className="chip-action-btn"
													onClick={() => handleSetDisplayImage(imgId)}
												>
													Set Display
												</button>
											)}
										{isAdmin && isEditing && (
											<button
												className="chip-action-btn chip-action-btn--danger"
												onClick={() => handleRemoveFile(imgId, "image")}
											>
												Remove
											</button>
										)}
									</div>
								))}
								{/* All of the icons for attached PDFs (if any) */}
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
										{isAdmin && isEditing && (
											<button
												className="chip-action-btn chip-action-btn--danger"
												onClick={() => handleRemoveFile(reportId, "report")}
											>
												Remove
											</button>
										)}
									</div>
								))}
							</div>
							{/* Upload file buttons (only appear when editing, below the file attachments) */}
							{isAdmin && isEditing && (
								<div className="upload-buttons">
									<label className="btn-primary btn-upload-label">
										{uploadingFile ? "Uploading..." : "Upload Image"}
										<input
											type="file"
											accept=".png,.jpg,.jpeg"
											hidden
											onChange={(e) => handleFileUpload(e, "image")}
											disabled={uploadingFile}
										/>
									</label>
									<label className="btn-primary btn-upload-label">
										{uploadingFile ? "..." : "Upload Report"}
										<input
											type="file"
											accept=".pdf"
											hidden
											onChange={(e) => handleFileUpload(e, "report")}
											disabled={uploadingFile}
										/>
									</label>
								</div>
							)}
						</div>

						{/* Right side: Contains the equip action buttons */}
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
