import "../styles/default.css";
import "../styles/profile.css";
import { useState, useEffect, useRef } from "react";
import { useAuth } from "../Authentication";
import { useNavigate } from "react-router-dom";
import { API_BASE } from "../config";
import Header from "../components/header";
import Sidebar from "../components/sidebar";
import { useSidebar } from "../SidebarContext";
import UserProfileImage from "../components/UserProfileImage";

const MAX_PROFILE_IMAGE_SIZE = 2 * 1024 * 1024; //2MB
const ALLOWED_IMAGE_TYPES = [".png", ".jpg", ".jpeg"];

function Profile({ num_of_notifications, setNumNotifications }) {
	const { sidebarOpen, openSidebar, closeSidebar } = useSidebar();
	const { logout } = useAuth();
	const navigate = useNavigate();

	const [profile, setProfile] = useState({
		fname: "",
		lname: "",
		email: "",
		phone: "",
		position: "",
		department: "",
		profile_image: null,
	});
	const fileInputRef = useRef(null);

	useEffect(() => {
		const fetchProfile = async () => {
			try {
				const res = await fetch(`http://${API_BASE}:5000/get_profile_info`, {
					method: "GET",
					credentials: "include",
				});

				if (!res.ok) throw new Error("Failed to fetch profile");

				const data = await res.json();
				const user_info = data["user"];
				const fname = user_info.name.split(" ")[0];
				const lname = user_info.name.split(" ")[1];

				setProfile({
					fname: fname,
					lname: lname,
					email: user_info.email,
					phone: user_info.phone || "",
					position: user_info.position || "",
					department: user_info.department || "",
					profile_image: user_info.profile_image,
				});
			} catch (err) {
				console.error(err);
				alert("Could not load profile information");
			}
		};
		fetchProfile();
	}, []);

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
		} catch (err) {
			console.error(err);
			alert("Error saving profile changes");
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

	const handleProfileImageChange = async (e) => {
		const file = e.target.files?.[0];
		if (!file) return;
		const ext = "." + (file.name.split(".").pop() || "").toLowerCase();
		if (!ALLOWED_IMAGE_TYPES.includes(ext)) {
			alert("Invalid file type. Allowed: PNG, JPG, JPEG");
			return;
		}
		if (file.size > MAX_PROFILE_IMAGE_SIZE) {
			alert("File too large. Max size: 2MB");
			return;
		}
		const formData = new FormData();
		formData.append("image", file);
		try {
			const res = await fetch(`http://${API_BASE}:5000/upload_profile_image`, {
				method: "POST",
				credentials: "include",
				body: formData,
			});
			const data = await res.json();
			if (data.result) {
				setProfile((prev) => ({ ...prev, profile_image: data.image_id }));
			} else {
				alert(data.message || "Failed to upload image");
			}
		} catch (err) {
			alert("Failed to upload image");
		}
		e.target.value = "";
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
					<div className="settings-card">
						{/* Left side */}
						<div className="profile-section">
							<div className="profile-picture-large">
								<UserProfileImage user={profile} className="profile-picture-img" />
							</div>
							<label className="change-picture-btn">
								Change Picture
								<input
									ref={fileInputRef}
									type="file"
									accept=".png,.jpg,.jpeg"
									onChange={handleProfileImageChange}
									hidden
								/>
							</label>

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
				</div>
			</div>
		</div>
	);
}

export default Profile;
