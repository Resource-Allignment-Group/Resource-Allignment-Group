// This component is used on the User Management page
// Shows user accounts with their role and checked out equipment

import "../styles/userManagementCard.css";
import { MdArrowForwardIos, MdPerson } from "react-icons/md";
import { useState } from "react";
import { API_BASE } from "../config";
import { useAuth } from "../Authentication";

function UserManagementCard({ user, isExpanded, onToggle, onDelete }) {
	const { role: currentUserRole } = useAuth();
	const isAdmin = currentUserRole === "a";
	const [role, setRole] = useState(user.role);

	// Allow admins to change the user's role
	const ChangeRole = async (new_role) => {
		try {
			setRole(new_role);
			const res = await fetch(`http://${API_BASE}:5000/change_user_role`, {
				method: "POST",
				credentials: "include",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify({ new_role: new_role, user: user }),
			});
			const data = await res.json();
			if (data.result) {
				alert("User's Role Was Successfully Updated");
			} else {
				alert(data.message || "Something Went Wrong");
			}
		} catch (error) {
			alert("There Were Problems Changing The User's Role");
		}
	};

	// Admins can delete user accounts from the DB
	const DeleteUser = async () => {
		const confirmDelete = window.confirm(
			`Are you sure you want to delete "${user.name}"? `,
		);
		if (!confirmDelete) {
			return;
		}
		onDelete(user);
	};

	return (
		<div className="user-management-card">
			<div className="card-header">
				<div className="user-profile-circle">
					{user.profile_image ? (
						<img
							src={`http://${API_BASE}:5000/get_profile_image/${user.id}`}
							alt={user.name}
							className="user-profile-img"
							style={{
								width: "100%",
								height: "100%",
								objectFit: "cover",
								borderRadius: "50%",
							}}
						/>
					) : (
						<MdPerson className="user-placeholder-icon" />
					)}
				</div>

				{/* User details */}
				<div className="equipment-info">
					<h3>{user.name}</h3>
					<p className="user-contact-info">
						{/* change back to email */}
						{user.email} | {user.phone}
					</p>
				</div>

				{/* Role dropdown - Admin only */}
				{isAdmin && (
					<div className="user-role-section">
						<select
							className="role-dropdown"
							value={role}
							onChange={(e) => ChangeRole(e.target.value)}
						>
							<option value="a">Admin</option>
							<option value="s">Superintendent</option>
							<option value="u">User</option>
						</select>
					</div>
				)}
				{!isAdmin && (
					<div className="user-role-section">
						<span className="role-display">
							{role === "a"
								? "Admin"
								: role === "s"
									? "Superintendent"
									: "User"}
						</span>
					</div>
				)}

				{/* Button state for opening and closing the user card  */}
				<button
					className={`expand-button ${isExpanded ? "rotated" : ""}`}
					onClick={onToggle}
				>
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
							{user.checked_out_equipment &&
							user.checked_out_equipment.length > 0 ? (
								user.checked_out_equipment.map((equipment, index) => (
									<div key={index} className="detail-row">
										<span className="label">{equipment.name}</span>
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

					{isAdmin && (
						<div className="card-footer">
							<div className="action-buttons">
								<button className="btn-danger" onClick={DeleteUser}>
									Delete
								</button>
							</div>
						</div>
					)}
				</div>
			)}
		</div>
	);
}

export default UserManagementCard;
