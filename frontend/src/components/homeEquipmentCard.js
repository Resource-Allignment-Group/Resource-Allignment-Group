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
		use: equipment.use,
		replacement_cost: equipment.replacement_cost,
		description: equipment.description,
		damaged: equipment.damaged,
	});
	const [isEditing, setIsEditing] = useState(false);
	const [uploadingFile, setUploadingFile] = useState(false);
	const imageUrl = equipment.display_image && equipment.images && equipment.images.includes(equipment.display_image)
		? `http://${API_BASE}:5000/get_equipment_image/${equipment.id}/${equipment.display_image}`
		: equipment.images && equipment.images.length > 0
		? `http://${API_BASE}:5000/get_equipment_image/${equipment.id}/${equipment.images[0]}`
		: null;
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
				if (onDelete) onDelete();
				if (onRefresh) onRefresh();
			} else {
				alert(data.message || "Failed to delete equipment");
			}
		} catch (error) {
			alert("There Were Problems Deleting The Equipment");
		}
	};

	const handleFileUpload = async (e, fileType) => {
		const file = e.target.files?.[0];
		if (!file) return;
		const MAX_IMAGE = 5 * 1024 * 1024;
		const MAX_REPORT = 10 * 1024 * 1024;
		if (fileType === "image" && (file.size > MAX_IMAGE || !["image/png", "image/jpeg", "image/jpg"].includes(file.type))) {
			alert("Image must be PNG/JPG and under 5MB");
			return;
		}
		if (fileType === "report" && (file.size > MAX_REPORT || file.type !== "application/pdf")) {
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
			if (data.result) {
				onRefresh?.();
			} else {
				alert(data.message || "Upload failed");
			}
		} catch {
			alert("Upload failed");
		} finally {
			setUploadingFile(false);
			e.target.value = "";
		}
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
			if (data.result) onRefresh?.();
			else alert(data.message || "Failed to set display image");
		} catch {
			alert("Failed to set display image");
		}
	};

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
				<div className="equipment-image">
					{imageUrl ? (
						<img src={imageUrl} alt={equipment.name} className="equipment-card-img" />
					) : (
						<div className="image-placeholder"></div>
					)}
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

						<div className="details-column">
							<h4>Description</h4>
							{/* "Read only" on display, this can change when we open the 
              				form to edit the equipment details */}
							<textarea
								className="equipment-value description-field"
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
						<div style={{ display: "flex", flexDirection: "column", gap: 4, marginBottom: 12 }}>
							<div style={{ display: "flex", alignItems: "flex-start", gap: 8 }}>
								<span style={{ fontWeight: 500, flexShrink: 0 }}>Attachments:</span>
								<div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
									{(() => {
										const items = [];
										equipment.images?.forEach((imgId) => {
											items.push(
												<div key={`img-${imgId}`} style={{ display: "flex", alignItems: "center", gap: 8 }}>
													<span style={{ fontSize: 14 }}>Image</span>
													<a href={`http://${API_BASE}:5000/get_equipment_image/${equipment.id}/${imgId}`} target="_blank" rel="noopener noreferrer" className="link-button" style={{ color: "#1976d2" }}>View</a>
													{equipment.display_image !== imgId && isAdmin && isEditing && (
														<button className="link-button" style={{ padding: "2px 6px", color: "#1976d2" }} onClick={() => handleSetDisplayImage(imgId)}>Set as display</button>
													)}
													{isAdmin && isEditing && (
														<button className="link-button" style={{ padding: "2px 6px", color: "#c00" }} onClick={() => handleRemoveFile(imgId, "image")}>Remove</button>
													)}
												</div>
											);
										});
										equipment.reports?.forEach((reportId) => {
											items.push(
												<div key={`rpt-${reportId}`} style={{ display: "flex", alignItems: "center", gap: 8 }}>
													<span style={{ fontSize: 14 }}>Report (PDF)</span>
													<a href={`http://${API_BASE}:5000/get_equipment_report/${equipment.id}/${reportId}`} target="_blank" rel="noopener noreferrer" className="link-button" style={{ color: "#1976d2" }}>Open</a>
													{isAdmin && isEditing && (
														<button className="link-button" style={{ padding: "2px 6px", color: "#c00" }} onClick={() => handleRemoveFile(reportId, "report")}>Remove</button>
													)}
												</div>
											);
										});
										if (items.length === 0) {
											items.push(<span key="none" style={{ color: "#666", fontSize: 14 }}>None</span>);
										}
										return items;
									})()}
								</div>
							</div>
							{isAdmin && isEditing && (
								<div style={{ display: "flex", gap: 8, marginLeft: 0 }}>
									<label className="link-button" style={{ cursor: "pointer", margin: 0 }}>
										{uploadingFile ? "Uploading..." : "Upload Image"}
										<input type="file" accept=".png,.jpg,.jpeg" hidden onChange={(e) => handleFileUpload(e, "image")} disabled={uploadingFile} />
									</label>
									<label className="link-button" style={{ cursor: "pointer", margin: 0 }}>
										{uploadingFile ? "..." : "Upload Report"}
										<input type="file" accept=".pdf" hidden onChange={(e) => handleFileUpload(e, "report")} disabled={uploadingFile} />
									</label>
								</div>
							)}
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
