// This component is used on the dashboard page
// and serves as the form to add new equipment to the database

import { useState, useEffect } from "react";
import "../styles/addequipment.css";
import "../styles/default.css";
import { API_BASE } from "../config";

function AddEquipmentModal({ isOpen, onClose, onSuccess }) {
	const [formData, setFormData] = useState({
		name: "",
		class: "",
		year: "",
		model: "",
		make: "",
		use: "",
		description: "",
		farm: "",
	});

	const [options, setOptions] = useState({
		farms: [],
		classes: [],
		makes: [],
		uses: [],
	});

	const [images, setImages] = useState([]);
	const [reports, setReports] = useState([]);
	const [submitting, setSubmitting] = useState(false);
	const MAX_IMAGE_SIZE = 5 * 1024 * 1024;
	const MAX_REPORT_SIZE = 10 * 1024 * 1024;
	const ALLOWED_IMAGE_TYPES = ["image/png", "image/jpeg", "image/jpg"];
	const ALLOWED_REPORT_TYPES = ["application/pdf"];

	// Fetches the in-use options for the form fields for easy lookup
	useEffect(() => {
		if (!isOpen) return;

		fetch(`http://${API_BASE}:5000/get_filter_options`, {
			credentials: "include",
		})
			.then((res) => res.json())
			.then((data) => {
				if (data.result) {
					setOptions({
						farms: data.farms,
						classes: data.classes,
						makes: data.makes,
						uses: data.uses,
					});
				}
			})
			.catch(console.error);
	}, [isOpen]);

	if (!isOpen) return null;

	// Fill out the form fields
	const handleChange = (e) => {
		const { name, value } = e.target;
		setFormData((prev) => ({ ...prev, [name]: value }));
	};

	// Ensure all uploaded files (images/reports) aren't huge and are of the correct type
	const validateFiles = () => {
		for (const file of images) {
			if (file.size > MAX_IMAGE_SIZE) {
				alert(`Image "${file.name}" exceeds 5MB limit`);
				return false;
			}
			if (!ALLOWED_IMAGE_TYPES.includes(file.type)) {
				alert(`Image "${file.name}" must be PNG or JPG`);
				return false;
			}
		}
		for (const file of reports) {
			if (file.size > MAX_REPORT_SIZE) {
				alert(`Report "${file.name}" exceeds 10MB limit`);
				return false;
			}
			if (!ALLOWED_REPORT_TYPES.includes(file.type)) {
				alert(`Report "${file.name}" must be PDF`);
				return false;
			}
		}
		return true;
	};

	// Submitting the form for adding equipment
	const handleSubmit = async (e) => {
		e.preventDefault();
		if (!validateFiles()) return;
		setSubmitting(true);

		try {
			let res;
			// 2 cases for adding equipment with/without images/reports
			if (images.length > 0 || reports.length > 0) {
				const payload = new FormData();
				Object.entries(formData).forEach(([key, value]) => {
					payload.append(key, value || "");
				});
				images.forEach((file) => payload.append("images", file));
				reports.forEach((file) => payload.append("reports", file));
				res = await fetch(`http://${API_BASE}:5000/add_equipment`, {
					method: "POST",
					credentials: "include",
					body: payload,
				});
			} else {
				res = await fetch(`http://${API_BASE}:5000/add_equipment`, {
					method: "POST",
					credentials: "include",
					headers: { "Content-Type": "application/json" },
					body: JSON.stringify({
						data: formData,
						images: [],
						reports: [],
					}),
				});
			}
			// Output error and success info
			const data = await res.json();
			if (!data.result) {
				alert(data.message || "Failed to submit equipment");
				setSubmitting(false);
				return;
			}
			if (onSuccess) onSuccess();
			setFormData({
				name: "",
				class: "",
				year: "",
				model: "",
				make: "",
				use: "",
				description: "",
				farm: "",
			});
			setImages([]);
			setReports([]);
			onClose();
		} catch (err) {
			alert("Error submitting equipment");
		} finally {
			setSubmitting(false);
		}
	};

	return (
		<div className="add-equipment-overlay" onClick={onClose}>
			<div className="add-equipment-modal" onClick={(e) => e.stopPropagation()}>
				<div className="add-equipment-header">
					<h2>Add Equipment</h2>
					<button className="add-equipment-close" onClick={onClose}>
						×
					</button>
				</div>

				<div className="add-equipment-body">
					<form onSubmit={handleSubmit}>
						<label>
							Name
							<input
								type="text"
								name="name"
								value={formData.name}
								onChange={handleChange}
								required
							/>
						</label>

						<label>
							Class
							<input
								type="text"
								list="class-options"
								name="class"
								value={formData.class}
								onChange={handleChange}
								required
							/>
							<datalist id="class-options">
								{options.classes.map((c) => (
									<option key={c} value={c} />
								))}
							</datalist>
						</label>

						<label>
							Farm
							<input
								type="text"
								list="farm-options"
								name="farm"
								value={formData.farm}
								onChange={handleChange}
								required
							/>
							<datalist id="farm-options">
								{options.farms.map((farm) => (
									<option key={farm} value={farm} />
								))}
							</datalist>
						</label>

						<label>
							Year
							<input
								type="text"
								name="year"
								value={formData.year}
								onChange={handleChange}
								required
							/>
						</label>

						<label>
							Model
							<input
								type="text"
								name="model"
								value={formData.model}
								onChange={handleChange}
								required
							/>
						</label>

						<label>
							Make
							<input
								type="text"
								list="make-options"
								name="make"
								value={formData.make}
								onChange={handleChange}
								required
							/>
							<datalist id="make-options">
								{options.makes.map((m) => (
									<option key={m} value={m} />
								))}
							</datalist>
						</label>

						<label>
							Use
							<input
								type="text"
								list="use-options"
								name="use"
								value={formData.use}
								onChange={handleChange}
								required
							/>
							<datalist id="use-options">
								{options.uses.map((u) => (
									<option key={u} value={u} />
								))}
							</datalist>
						</label>

						<label>
							Images (Optional - PNG, JPG, max 5MB each)
							<input
								type="file"
								multiple
								accept=".png,.jpg,.jpeg"
								onChange={(e) =>
									setImages(e.target.files ? [...e.target.files] : [])
								}
							/>
						</label>

						<label>
							Reports (Optional - PDF only, max 10MB each)
							<input
								type="file"
								multiple
								accept=".pdf"
								onChange={(e) =>
									setReports(e.target.files ? [...e.target.files] : [])
								}
							/>
						</label>

						<label>
							Description (Optional)
							<textarea
								type="text"
								name="description"
								value={formData.description}
								onChange={handleChange}
							/>
						</label>
						<div className="add-equipment-footer">
							<button
								className="add-equipment-submit"
								type="submit"
								disabled={submitting}
							>
								{submitting ? "Submitting..." : "Submit"}
							</button>
							<button
								className="add-equipment-cancel"
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

export default AddEquipmentModal;
