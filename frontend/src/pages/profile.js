import "../styles/default.css";
import "../styles/profile.css";
import { useState } from "react";
import { useAuth } from "../Authentication"
import { useNavigate } from 'react-router-dom';

// Import componets that will make up the profile page
import Header from "../components/header";
import Sidebar from "../components/sidebar";

function Profile({num_of_notifications, setNumNotifications}) {
	const [sidebarOpen, setSidebarOpen] = useState(true);
	const { logout } = useAuth()
	const navigate = useNavigate()
	
	const handleLogout = async () => {
		const success = await logout();
    	if(success){
      		navigate('/login'); 
    	} 
    
    	else {
      		alert('Can Not Sign Out'); 
    	}
	}

	return (
		<div className="home-container">
			{/* Sidebar is a separate component */}
			<Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

			<div className="main">
				{/* Header is a separate component */}
				<Header
					sidebarOpen={sidebarOpen}
					onMenuToggle={() => setSidebarOpen(true)}
					num_of_notifications={num_of_notifications}
					setNotificationsNum={setNumNotifications}
				/>

				{/* The title and brief description of the profile page  */}
				<div className="hero-section">
					<h2>Account Settings</h2>
					<p>Manage your personal information</p>
				</div>

				{/* Account settings content */}
				<div className="content">
					<div className="settings-card">
						{/* Left side - Profile section */}
						<div className="profile-section">
							<div className="profile-picture-large"></div>
							<button className="change-picture-btn">Change Picture</button>

							<div className="profile-info">
								<h3>John Smith</h3>
								<p>john.smith@gmail.com</p>
							</div>

							<button className="sign-out-btn" onClick={handleLogout}>Sign Out</button>
						</div>

						{/* Right side - Form section */}
						<div className="form-section">
							<h3>Personal Details</h3>

							<div className="form-row">
								<div className="form-field">
									<label>
										First Name <span className="required">*</span>
									</label>
									<input type="text" placeholder="" />
								</div>

								<div className="form-field">
									<label>
										Last Name <span className="required">*</span>
									</label>
									<input type="text" placeholder="" />
								</div>
							</div>

							<div className="form-row">
								<div className="form-field">
									<label>
										Email Address <span className="required">*</span>
									</label>
									<input type="email" placeholder="" />
								</div>

								<div className="form-field">
									<label>Phone Number</label>
									<input type="tel" placeholder="" />
								</div>
							</div>

							<div className="form-row">
								<div className="form-field">
									<label>
										Position within MAFES <span className="required">*</span>
									</label>
									<input type="text" placeholder="" />
								</div>

								<div className="form-field">
									<label>
										MAFES Department <span className="required">*</span>
									</label>
									<input type="text" placeholder="" />
								</div>
							</div>

							{/* Form buttons */}
							<div className="form-buttons">
								<button className="btn-save">Save Changes</button>
								<button className="btn-cancel">Cancel</button>
							</div>
						</div>
					</div>
				</div>
			</div>
		</div>
	);
}

export default Profile;
