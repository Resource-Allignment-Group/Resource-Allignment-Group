// This component is used on the User Management page
// Shows user accounts with their role and checked out equipment

import '../styles/userManagementCard.css';
import { MdArrowForwardIos } from "react-icons/md";
import { useState } from "react"; // Temp needed for visibility, removed when backend connected

function UserManagementCard({ user, isExpanded, onToggle }) {
	// Placeholder for changing the user's role in the dropdown
	// Connect to the backend later
	const [role, setRole] = useState(user.role);

	return (
		<div className="user-management-card">
			<div className="card-header">
				{/* User profile circle with temporary color */}
				<div className="user-profile-circle"></div>

				{/* User details */}
				<div className="equipment-info">
					<h3>{user.name}</h3>
					<p className="user-contact-info">
						{user.email} | {user.phone}
					</p>
				</div>

				{/* User role dropdown - displays user's assigned role */}
				{/* Placeholder until conencted to the backend */}
				<div className="user-role-section">
					<select className="role-dropdown" value={role} onChange={(e) => setRole(e.target.value)}>
						<option value="Admin">Admin</option>
						<option value="Superintendent">Superintendent</option>
						<option value="User">User</option>
					</select>
				</div>

				{/* Button state for opening and closing the user card  */}
				<button className={`expand-button ${isExpanded ? "rotated" : ""}`} onClick={onToggle}>
					<MdArrowForwardIos />
				</button>
			</div>

			{/* Expand the card to show more user details  */}
			{isExpanded && (
				<div className="card-details">
					<div className="details-grid">
						<div className="details-column">
							<h4>Basic Information</h4>
							<div className="detail-row">
								<span className="label">Position within MAFES</span>
								<span className="value">{user.position}</span>
							</div>
							<div className="detail-row">
								<span className="label">MAFES Department</span>
								<span className="value">{user.department}</span>
							</div>
						</div>

						<div className="details-column">
							<h4>Checked Out Equipment</h4>
							{user.checkedOutEquipment && user.checkedOutEquipment.length > 0 ? (
								user.checkedOutEquipment.map((equipment, index) => (
									<div key={index} className="detail-row">
										<span className="label">{equipment.name}</span>
										<span className="value">
											Checked Out: {equipment.checkedOutDate}
										</span>
									</div>
								))
							) : (
								<div className="detail-row">
									<span className="value">No equipment checked out</span>
								</div>
							)}
						</div>

						<div className="details-column">
							{/* Empty column for grid alignment */}
						</div>
					</div>

					<div className="card-footer">
						<div className="action-buttons">
							<button className="btn-danger">Delete</button>
						</div>
					</div>
				</div>
			)}
		</div>
	);
}

export default UserManagementCard;