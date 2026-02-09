import "../styles/default.css";
import { useState, useEffect } from "react";
import Header from "../components/header";
import Sidebar from "../components/sidebar";
import UserManagementCard from "../components/userManagementCard";
import { API_BASE } from "../config";
import { useSidebar } from "../SidebarContext";

function UserManagement({ num_of_notifications, setNumNotifications }) {
	const { sidebarOpen, openSidebar, closeSidebar } = useSidebar();
	const [expandedCard, setExpandedCard] = useState(null);
	const [users, setUsers] = useState([]);

	useEffect(() => {
		const GetUsersInfo = async () => {
			try {
				const res = await fetch(`http://${API_BASE}:5000/get_users`, {
					credentials: "include",
				});
				const data = await res.json();
				setUsers(data.users);
			} catch (error) {
				alert("Something Went Wrong Gathering The User's Information");
			}
		};
		GetUsersInfo();
	}, []);

	const handleDeleteUser = async (userToDelete) => {
		try {
			const res = await fetch(`http://${API_BASE}:5000/delete_user_account`, {
				method: "POST",
				credentials: "include",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify({ user: userToDelete }),
			});
			const data = await res.json();
			if (data.result) {
				alert("User Was Successfully Deleted");
				setUsers((prevUsers) =>
					prevUsers.filter((u) => u.id !== userToDelete.id),
				);
			}
		} catch (error) {
			alert("There Were Problems Deleting The User");
		}
	};

	return (
		<div className="home-container">
			{/* Sidebar is a separate component */}
			<Sidebar isOpen={sidebarOpen} onClose={closeSidebar} />

			<div className="main">
				{/* Header is a separate component */}
				<Header
					sidebarOpen={sidebarOpen}
					onMenuToggle={openSidebar}
					activeTab="User Management"
					num_of_notifications={num_of_notifications}
					setNotificationsNum={setNumNotifications}
				/>

				{/* The title and brief description of the user management page  */}
				<div className="hero-section">
					<h2>User Management</h2>
					<p>Monitor user accounts and permissions</p>
				</div>

				{/* Scrollable content  */}
				<div className="content">
					{/* Scrollable users are a seperate component */}
					{users
						.filter((item) => item.role !== "p")
						.map((item) => (
							<UserManagementCard
								key={item.id}
								user={item}
								isExpanded={expandedCard === item.id}
								onToggle={() =>
									setExpandedCard(expandedCard === item.id ? null : item.id)
								}
								onDelete={handleDeleteUser}
							/>
						))}
				</div>
			</div>
		</div>
	);
}

export default UserManagement;
