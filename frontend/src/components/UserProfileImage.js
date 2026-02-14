//Displays user profile image
import { useState, useEffect } from "react";
import { API_BASE } from "../config";

function UserProfileImage({ user, className = "user-profile-img" }) {
	const [imageUrl, setImageUrl] = useState(null);

	useEffect(() => {
		if (!user?.profile_image) return;
		const url = `http://${API_BASE}:5000/profile_image/${encodeURIComponent(user.profile_image)}`;
		const img = new Image();
		img.onload = () => setImageUrl(url);
		img.src = url;
	}, [user?.profile_image]);

	if (!imageUrl) {
		return <div className={`${className} profile-placeholder`} />;
	}

	return (
		<div className={className}>
			<img src={imageUrl} alt={user?.name || "Profile"} />
		</div>
	);
}

export default UserProfileImage;
