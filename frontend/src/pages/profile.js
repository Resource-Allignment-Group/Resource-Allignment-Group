import "../styles/default.css";
import "../styles/profile.css";
import { useState, useEffect } from "react";
import { useAuth } from "../Authentication";
import { useNavigate } from "react-router-dom";
import { API_BASE } from "../config";
import Header from "../components/header";
import Sidebar from "../components/sidebar";
import { useSidebar } from "../SidebarContext";

function Profile({ num_of_notifications, setNumNotifications }) {
	const { sidebarOpen, openSidebar, closeSidebar } = useSidebar();
	const [isLoading, setIsLoading] = useState(true);
	const { logout } = useAuth();
	const navigate = useNavigate();

	const [profile, setProfile] = useState({
		fname: "",
		lname: "",
		email: "",
		phone: "",
		position: "",
		department: "",
	});
	const [userId, setUserId] = useState(null);
	const [profileImageUrl, setProfileImageUrl] = useState(null);
	const [uploadingImage, setUploadingImage] = useState(false);

	// Load user profile info
	useEffect(() => {
		const fetchProfile = async () => {
			try {
				setIsLoading(true);
				const res = await fetch(`http://${API_BASE}:5000/get_profile_info`, {
					method: "GET",
					credentials: "include",
				});

				if (!res.ok) throw new Error("Failed to fetch profile");

				// Clean the data
				const data = await res.json();
				const user_info = data["user"];
				const fname = user_info.name.split(" ")[0];
				const lname = user_info.name.split(" ")[1];

				// Display the user's info
				setProfile({
					fname: fname,
					lname: lname,
					email: user_info.email,
					phone: user_info.phone || "",
					position: user_info.position || "",
					department: user_info.department || "",
				});
				setUserId(user_info.id);
				if (user_info.profile_image) {
					setProfileImageUrl(
						`http://${API_BASE}:5000/get_profile_image/${user_info.id}?t=${Date.now()}`,
					);
				} else {
					setProfileImageUrl(null);
				}
			} catch {
				alert("Could not load profile information");
			} finally {
				setIsLoading(false);
			}
		};
		fetchProfile();
	}, []);

	// If the user updates and saves their info
	const handleSave = async () => {
		try {
			const res = await fetch(`http://${API_BASE}:5000/save_new_profile_info`, {
				method: "POST",
				headers: {
					"Content-Type": "application/json",
				},
				credentials: "include",
				body: JSON.stringify(profile),
			});

			if (!res.ok) throw new Error("Failed to save profile");

			alert("Profile updated successfully");
		} catch {
			alert("Error saving profile changes");
		}
	};

	// User removes their existing profile image
	const handleDeleteProfileImage = async () => {
		if (!window.confirm("Remove your profile picture?")) return;
		try {
			const res = await fetch(`http://${API_BASE}:5000/delete_profile_image`, {
				method: "POST",
				credentials: "include",
			});
			const data = await res.json();
			if (data.result) {
				setProfileImageUrl(null);
			} else {
				alert(data.message || "Failed to remove picture");
			}
		} catch {
			alert("Failed to remove picture");
		}
	};

	// User uploads a profile image
	const handleProfileImageUpload = async (e) => {
		const file = e.target.files?.[0];
		if (!file) return;
		if (file.size > 2 * 1024 * 1024) {
			alert("Image must be under 2MB");
			return;
		}
		if (!["image/png", "image/jpeg", "image/jpg"].includes(file.type)) {
			alert("Image must be PNG or JPG");
			return;
		}
		setUploadingImage(true);
		try {
			const formData = new FormData();
			formData.append("file", file);
			const res = await fetch(`http://${API_BASE}:5000/upload_profile_image`, {
				method: "POST",
				credentials: "include",
				body: formData,
			});
			const data = await res.json();
			if (data.result) {
				setProfileImageUrl(
					`http://${API_BASE}:5000/get_profile_image/${userId}?t=${Date.now()}`,
				);
			} else {
				alert(data.message || "Upload failed");
			}
		} catch {
			alert("Upload failed");
		} finally {
			setUploadingImage(false);
			e.target.value = "";
		}
	};

	const handleChange = (e) => {
		const { name, value } = e.target;
		setProfile((prev) => ({
			...prev,
			[name]: value,
		}));
	};

	const handleLogout = async () => {
		const success = await logout();
		if (success) {
			navigate("/login");
		} else {
			alert("Can Not Sign Out");
		}
	};

	return (
		<div className="home-container">
			<Sidebar isOpen={sidebarOpen} onClose={closeSidebar} />

			<div className="main">
				<Header
					sidebarOpen={sidebarOpen}
					onMenuToggle={openSidebar}
					activeTab="Profile"
					num_of_notifications={num_of_notifications}
					setNotificationsNum={setNumNotifications}
				/>

				<div className="hero-section">
					<h2>Account Settings</h2>
					<p>Manage your personal information</p>
				</div>

				<div className="content">
					{isLoading ? (
						<div className="response-text">
							<p>Loading your profile...</p>
						</div>
					) : (
						<>
							<div className="settings-card">
								{/* Left side */}
								<div className="profile-section">
									<div className="profile-picture-large">
										{profileImageUrl ? (
											<img
												src={profileImageUrl}
												alt="Profile"
												className="profile-picture-img"
											/>
										) : null}
									</div>

									<div className="picture-buttons">
										<label className="change-picture-btn">
											{uploadingImage ? "Uploading..." : "Change Picture"}
											<input
												type="file"
												accept=".png,.jpg,.jpeg"
												hidden
												onChange={handleProfileImageUpload}
												disabled={uploadingImage}
											/>
										</label>
										{profileImageUrl && (
											<button
												type="button"
												className="change-picture-btn remove-picture-btn"
												onClick={handleDeleteProfileImage}
											>
												Remove Picture
											</button>
										)}
									</div>

									<div className="profile-info">
										<h3>
											{profile.fname} {profile.lname}
										</h3>
										<p>{profile.email}</p>
									</div>

									<button className="sign-out-btn" onClick={handleLogout}>
										Sign Out
									</button>
								</div>

								{/* Right side form */}
								<div className="form-section">
									<h3>Personal Details</h3>

									<div className="form-row">
										<div className="form-field">
											<label>First Name</label>
											<input
												type="text"
												name="fname"
												value={profile.fname}
												onChange={handleChange}
											/>
										</div>

										<div className="form-field">
											<label>Last Name</label>
											<input
												type="text"
												name="lname"
												value={profile.lname}
												onChange={handleChange}
											/>
										</div>
									</div>

									<div className="form-row">
										<div className="form-field">
											<label>Email Address</label>
											<input
												type="email"
												name="email"
												value={profile.email}
												onChange={handleChange}
											/>
										</div>

										<div className="form-field">
											<label>Phone Number</label>
											<input
												type="tel"
												name="phone"
												value={profile.phone}
												onChange={handleChange}
											/>
										</div>
									</div>

									<div className="form-row">
										<div className="form-field">
											<label>Position within MAFES</label>
											<input
												type="text"
												name="position"
												value={profile.position}
												onChange={handleChange}
											/>
										</div>

										<div className="form-field">
											<label>MAFES Department</label>
											<input
												type="text"
												name="department"
												value={profile.department}
												onChange={handleChange}
											/>
										</div>
									</div>

									<div className="form-buttons">
										<button className="btn-save" onClick={handleSave}>
											Save Changes
										</button>
									</div>
								</div>
							</div>
						</>
					)}
				</div>
			</div>
		</div>
	);
}

export default Profile;
