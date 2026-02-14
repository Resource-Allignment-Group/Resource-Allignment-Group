// This component is currently used on the home page

import { useState } from "react";
import "../styles/home.css";
import { MdArrowForwardIos, MdCategory } from "react-icons/md";
import { useAuth } from "../Authentication";
import { API_BASE } from "../config";
import EquipmentImage from "./EquipmentImage";
import ImageViewerModal from "./ImageViewerModal";

//This needs to match backend. File size in bytes.
const MAX_IMAGE_SIZE = 5 * 1024 * 1024; //5MB
const MAX_REPORT_SIZE = 10 * 1024 * 1024; //10MB
const ALLOWED_IMAGE_TYPES = [".png", ".jpg", ".jpeg"];
const ALLOWED_REPORT_TYPES = [".pdf"];
import { useState } from "react";

function HomeEquipmentCard({
	equipment,
	isExpanded,
	onToggle,
	isSelected,
	onSelect,
	onDelete,
	onRefresh,
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
		useFrequency: equipment.use,
		replacementCost: equipment.replacementCost,
		description: equipment.description
		// other fields...
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
			console.log(error);
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
			console.log(error);
			alert("There Were Problems Deleting The Equipment");
		}
	};

	const status = getEquipmentStatus(equipment);

	// File upload validation
	const validateFile = (file, isImage) => {
		const ext = "." + (file.name.split(".").pop() || "").toLowerCase();
		const allowed = isImage ? ALLOWED_IMAGE_TYPES : ALLOWED_REPORT_TYPES;
		const maxSize = isImage ? MAX_IMAGE_SIZE : MAX_REPORT_SIZE;
		if (!allowed.includes(ext)) {
			return `Invalid file type. Allowed: ${allowed.join(", ")}`;
		}
		if (file.size > maxSize) {
			return `File too large. Max: ${maxSize / (1024 * 1024)}MB`;
		}
		return null;
	};

	const handleUploadImage = async (e) => {
		const file = e.target.files?.[0];
		if (!file) return;
		const err = validateFile(file, true);
		if (err) {
			alert(err);
			return;
		}
		const formData = new FormData();
		formData.append("equipment_id", equipment.id);
		formData.append("image", file);
		try {
			const res = await fetch(`http://${API_BASE}:5000/upload_equipment_image`, {
				method: "POST",
				credentials: "include",
				body: formData,
			});
			const data = await res.json();
			if (data.result) {
				onRefresh?.();
			} else {
				alert(data.message || "Upload failed");
			}
		} catch (err) {
			alert("Upload failed");
		}
		e.target.value = "";
	};

	const handleUploadReport = async (e) => {
		const file = e.target.files?.[0];
		if (!file) return;
		const err = validateFile(file, false);
		if (err) {
			alert(err);
			return;
		}
		const formData = new FormData();
		formData.append("equipment_id", equipment.id);
		formData.append("report", file);
		try {
			const res = await fetch(`http://${API_BASE}:5000/upload_equipment_report`, {
				method: "POST",
				credentials: "include",
				body: formData,
			});
			const data = await res.json();
			if (data.result) {
				onRefresh?.();
			} else {
				alert(data.message || "Upload failed");
			}
		} catch (err) {
			alert("Upload failed");
		}
		e.target.value = "";
	};

	const handleSetDisplayImage = async (imageId) => {
		try {
			const res = await fetch(`http://${API_BASE}:5000/set_equipment_display_image`, {
				method: "POST",
				credentials: "include",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify({ equipment_id: equipment.id, image_id: imageId }),
			});
			const data = await res.json();
			if (data.result) {
				onRefresh?.();
			} else {
				alert(data.message || "Failed to set display image");
			}
		} catch (err) {
			alert("Failed to set display image");
		}
	};

	const handleRemoveFile = async (fileType, fileId) => {
		if (!window.confirm(`Remove this ${fileType}?`)) return;
		try {
			const res = await fetch(`http://${API_BASE}:5000/remove_equipment_file`, {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          equipment_id: equipment.id,
          file_type: fileType,
          file_id: fileId,
        }),
      });
      const data = await res.json();
      if (data.result) {
        onRefresh?.();
      } else {
        alert(data.message || "Failed to remove file");
      }
    } catch (err) {
      alert("Failed to remove file");
    }
  };
        
	const handleEquipmentEdit = async () => {
		setIsEditing(false)
		try {
			const res = await fetch(`http://${API_BASE}:5000/change_equipment_info`, {
				method: "POST",
				credentials: "include",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify({ equipment: editedEquipment }),
			});
			const data = await res.json();
			if (data.result) {
        alert("Equipment information changed successfully");
      } else {
				alert(data.message || "Failed to change equipment information");
			}
		} catch (err) {
			alert("Failed to remove file");
		}
	};

	const imageUrl = (id) => `http://${API_BASE}:5000/equipment_image/${encodeURIComponent(id)}`;
	const reportUrl = (id) => `http://${API_BASE}:5000/equipment_report/${encodeURIComponent(id)}`;

	const [imageViewerOpen, setImageViewerOpen] = useState(false);
	const [imageViewerIndex, setImageViewerIndex] = useState(0);
	const imageUrls = equipment.images?.map((id) => imageUrl(id)) || [];

	const openImageViewer = (index) => {
		setImageViewerIndex(index);
		setImageViewerOpen(true);
	};

				alert("Equipment information changed successfully");
			} else {
				alert(data.message || "Failed to change equipment information");
			}
		} catch (error) {
			console.log(error);
			alert("There Were Problems Changing The Equipment Information");
		}
	}
	const status = getEquipmentStatus(equipment); //this gets the information for the equipment cards to reference later in the div
	return (
		<div className="equipment-card">
			<div className="card-header">
				<EquipmentImage equipment={equipment} className="equipment-image" />

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
									value={editedEquipment.useFrequency}
									disabled={!isEditing}
									onChange={(e) =>
										setEquipment({
										...editedEquipment,
										useFrequency: e.target.value,
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

					{/* Attachments section - admin can upload, set display, remove */}
					<div className="attachments-section">
						<h4>Attachments ({equipment.attachments || 0})</h4>
						{(equipment.images?.length > 0 || equipment.reports?.length > 0) && (
							<div className="attachments-list">
								{equipment.images?.map((imgId, idx) => {
									const isDisplayImage = equipment.display_image === imgId || (idx === 0 && !equipment.display_image);
									return (
										<div key={imgId} className="attachment-item">
											<img
												src={imageUrl(imgId)}
												alt=""
												className="attachment-thumb"
												onClick={() => openImageViewer(idx)}
											/>
											<div className="attachment-actions">
												{isAdmin && (
													<>
														{!isDisplayImage && (
															<button
																className="link-button"
																onClick={() => handleSetDisplayImage(imgId)}
																title="Set as card display image"
															>
																Set Display
															</button>
														)}
														<button
															className="link-button delete-text-link"
															onClick={() => handleRemoveFile("image", imgId)}
														>
															Remove
														</button>
													</>
												)}
											</div>
										</div>
									);
								})}
								{equipment.reports?.map((rId) => (
									<div key={rId} className="attachment-item">
										<span className="report-label">Equipment Report</span>
										<div className="attachment-actions">
											<a
												href={reportUrl(rId)}
												target="_blank"
												rel="noopener noreferrer"
												className="link-button"
											>
												View
											</a>
											{isAdmin && (
												<button
													className="link-button delete-text-link"
													onClick={() => handleRemoveFile("report", rId)}
												>
													Remove
												</button>
											)}
										</div>
									</div>
								))}
							</div>
						)}
						{isAdmin && (
							<div className="attachment-upload">
								<label className="link-button file-upload-label">
									Upload Image (PNG, JPG, max 5MB)
									<input
										type="file"
										accept=".png,.jpg,.jpeg"
										onChange={handleUploadImage}
										hidden
									/>
								</label>
								<label className="link-button file-upload-label">
									Upload Report (PDF, max 10MB)
									<input
										type="file"
										accept=".pdf"
										onChange={handleUploadReport}
										hidden
									/>
								</label>
							</div>
						)}
					</div>

					{/* Bottom of the opened equipment card */}
					<div className="card-footer">
						<div className="action-buttons">
							<button
								className="btn-primary"
								onClick={handleCheckOut}
								hidden={equipment.checked_out}
							>
								Request Checkout
							</button>
							<button className="btn-primary" hidden={equipment.checked_out || isEditing} onClick={() => setIsEditing(true)}>
								Edit Equipment
							</button>
							<button className="btn-primary" hidden={equipment.checked_out || !isEditing} onClick={handleEquipmentEdit}>
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

			<ImageViewerModal
				isOpen={imageViewerOpen}
				onClose={() => setImageViewerOpen(false)}
				images={imageUrls}
				currentIndex={imageViewerIndex}
				onIndexChange={setImageViewerIndex}
			/>
		</div>
	);
}

export default HomeEquipmentCard;
