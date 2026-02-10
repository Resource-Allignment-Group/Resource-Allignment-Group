import { useState } from "react";
import "../styles/returnequipment.css";
import { API_BASE } from "../config";

function ReturnEquipmentModal({ isOpen, onClose, equipment, onSuccess }) {
	const [formData, setFormData] = useState({
		functionedProperly: "",
		wasCleaned: "",
		hasDamage: "",
		damageDescription: "",
	});

	const [submitting, setSubmitting] = useState(false);

	if (!isOpen) return null;

	const handleChange = (e) => {
		const { name, value } = e.target;
		setFormData((prev) => ({ ...prev, [name]: value }));

		// Clear damage description if user selects "No" for damage
		if (name === "hasDamage" && value === "no") {
			setFormData((prev) => ({ ...prev, damageDescription: "" }));
		}
	};

	const handleSubmit = async (e) => {
		e.preventDefault();
		setSubmitting(true);

		try {
			const res = await fetch(`http://${API_BASE}:5000/return_equipment`, {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				credentials: "include",
				body: JSON.stringify({
					equipment_id: equipment.id,
					damaged: formData.hasDamage === "yes",
					damage_description: formData.damageDescription || null,
					functioned_properly: formData.functionedProperly,
					was_cleaned: formData.wasCleaned,
				}),
			});

			const data = await res.json();

			if (data.result) {
				if (onSuccess) onSuccess();
				onClose();
			} else {
				alert("Something Has Gone Wrong.");
			}
		} catch (error) {
			console.log(error);
			alert("Error returning equipment");
		} finally {
			setSubmitting(false);
		}
	};

	return (
		<div className="return-equipment-overlay" onClick={onClose}>
			<div
				className="return-equipment-modal"
				onClick={(e) => e.stopPropagation()}
			>
				<div className="return-equipment-header">
					<h2>Return Equipment</h2>
					<button className="return-equipment-close" onClick={onClose}>
						×
					</button>
				</div>

				<div className="return-equipment-body">
					<div className="equipment-name-display">
						<strong>Equipment:</strong> {equipment.name}
					</div>

					<form onSubmit={handleSubmit}>
						<label>
							Did the equipment function properly?{" "}
							<select
								name="functionedProperly"
								value={formData.functionedProperly}
								onChange={handleChange}
								required
							>
								<option value="">Select an option</option>
								<option value="yes">Yes</option>
								<option value="no">No</option>
								<option value="partially">Partially</option>
							</select>
						</label>

						<label>
							Was the equipment cleaned on return?{" "}
							<select
								name="wasCleaned"
								value={formData.wasCleaned}
								onChange={handleChange}
								required
							>
								<option value="">Select an option</option>
								<option value="yes">Yes</option>
								<option value="no">No</option>
							</select>
						</label>

						<label>
							Are there any damages to report?{" "}
							<select
								name="hasDamage"
								value={formData.hasDamage}
								onChange={handleChange}
								required
							>
								<option value="">Select an option</option>
								<option value="yes">Yes</option>
								<option value="no">No</option>
							</select>
						</label>

						{/* Show damage description field only if user selected "Yes" for damages */}
						{formData.hasDamage === "yes" && (
							<label>
								Damage Description
								<textarea
									name="damageDescription"
									value={formData.damageDescription}
									onChange={handleChange}
									placeholder="Please describe the damage in detail..."
									required
								/>
							</label>
						)}

						<div className="return-equipment-footer">
							<button
								className="return-equipment-submit"
								type="submit"
								disabled={submitting}
							>
								{submitting ? "Returning..." : "Return Equipment"}
							</button>
							<button
								className="return-equipment-cancel"
								type="button"
								onClick={onClose}
							>
								Cancel
							</button>
						</div>
					</form>
				</div>
			</div>
		</div>
	);
}

export default ReturnEquipmentModal;
