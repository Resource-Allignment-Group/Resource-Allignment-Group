import "../styles/default.css";
import { useState, useEffect } from "react";
import Header from "../components/header";
import Sidebar from "../components/sidebar";
import UserManagementCard from "../components/userManagementCard";
import { API_BASE } from "../config";
function UserManagement({num_of_notifications, setNumNotifications}) {
	const [sidebarOpen, setSidebarOpen] = useState(true);
	const [expandedCard, setExpandedCard] = useState(null);
	const [users, setUsers] = useState([]);
	useEffect(() => {
		const GetUsersInfo = async () => {
			try{
				const res = await fetch(`http://${API_BASE}:5000/get_users`, {
				credentials: "include",
				})
				const data = await res.json()
				setUsers(data.users)
			}
			catch(error){
				alert("Something Went Wrong Gathering The User's Information")
			}
		}
		GetUsersInfo()
	}, [])
	return (
		<div className="home-container">
			{/* Sidebar is a separate component */}
			<Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

			<div className="main">
				{/* Header is a separate component */}
				<Header
					sidebarOpen={sidebarOpen}
					onMenuToggle={() => setSidebarOpen(true)}
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
						/>
					))}
				</div>
			</div>
		</div>
	);
}

export default UserManagement;
