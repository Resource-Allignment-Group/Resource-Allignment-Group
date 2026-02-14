//Displays equipment display image or placeholder.
import { useState, useEffect } from "react";
import { API_BASE } from "../config";

function EquipmentImage({ equipment, className = "equipment-image" }) {
	const [imageUrl, setImageUrl] = useState(null);
	const [error, setError] = useState(false);

	useEffect(() => {
		if (!equipment || error) return;
		const displayId = equipment.display_image || (equipment.images && equipment.images[0]);
		if (!displayId) return;

		const url = `http://${API_BASE}:5000/equipment_image/${encodeURIComponent(displayId)}`;
		const img = new Image();
		img.onload = () => setImageUrl(url);
		img.onerror = () => setError(true);
		img.src = url;
	}, [equipment?.display_image, equipment?.images, error]);

	if (error || !imageUrl) {
		return (
			<div className={className}>
				<div className="image-placeholder"></div>
			</div>
		);
	}

	return (
		<div className={className}>
			<img src={imageUrl} alt={equipment?.name || "Equipment"} />
		</div>
	);
}

export default EquipmentImage;
