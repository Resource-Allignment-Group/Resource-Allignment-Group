import { useState } from "react";
import "../styles/addequipment.css";
import "../styles/default.css";

function AddEquipmentModal({ isOpen, onClose, onSuccess }) {
  const [formData, setFormData] = useState({
    name: "",
    class: "",
    year: "",
    model: "",
    make: "",
    use: "",
    description: "",
    farm: ""
  });

  const [images, setImages] = useState([]);
  const [reports, setReports] = useState([]);
  const [submitting, setSubmitting] = useState(false);

  if (!isOpen) return null;

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);

    const payload = new FormData();

    Object.entries(formData).forEach(([key, value]) => {
      payload.append(key, value);
    });

    images.forEach((file) => payload.append("images", file));
    reports.forEach((file) => payload.append("reports", file));

    try {
      const res = await fetch("http://localhost:5000/add_equipment", {
				method: "POST",
				credentials: "include",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify({data: formData, images: images, reports: reports}),
      });
      const data = await res.json();
      if (!data.result) {
        alert("Failed to submit equipment");
      }

      if (onSuccess) onSuccess();
      onClose();
    } catch (err) {
      console.error(err);
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
          <button className="add-equipment-close">×</button>
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
              <select
                name="class"
                value={formData.class}
                onChange={handleChange}
                required
              >
                <option value="">Select class</option>
                <option value="tractor">Tractor</option>
                <option value="handheld">Handheld</option>
                <option value="harvest">Harvest</option>
                <option value="None">Add More</option>
              </select>
            </label>

            <label>
              Farm
              <select
                name="farm"
                value={formData.farm}
                onChange={handleChange}
                required
              >
                <option value="">Select class</option>
                <option value="arrostook">Arrostook</option>
                <option value="blueberry_hill">Blueberry Hill B</option>
                <option value="greenhouse/garden">Greenhouse / Garden</option>
                <option value="witter">Witter</option>
                <option value="rogers">Rogers</option>
                <option value="highmoor">Highmoor</option>
              </select>
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
                name="make"
                value={formData.make}
                onChange={handleChange}
                required
              />
            </label>

            <label>
              Use
              <select
                name="use"
                value={formData.use}
                onChange={handleChange}
                required
              >
                <option value="">Select use</option>
                <option value="field">Field</option>
                <option value="lab">Lab</option>
                <option value="training">Training</option>
                <option value="None">idk what to put here, ask tyler</option>
              </select>
            </label>

            <label>
              Images (optional)
              <input
                type="file"
                multiple
                accept="image/*"
                onChange={(e) => setImages([...e.target.files])}
              />
            </label>

            <label>
              Reports (optional)
              <input
                type="file"
                multiple
                onChange={(e) => setReports([...e.target.files])}
              />
            </label>

            <label>
              Description (optional)
              <textarea
                name="description"
                value={formData.description}
                onChange={handleChange}
              />
            </label>

          
          <div className="add-equipment-footer">
            <button className="add-equipment-submit" type="submit" disabled={submitting}>
              {submitting ? "Submitting..." : "Submit"}
            </button>
            <button className="add-equipment-cancel" type="button" onClick={onClose}>
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
