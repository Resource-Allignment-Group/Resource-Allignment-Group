import "../styles/default.css";
import { useState } from "react";

// Import componets that will make up the user management page
import Header from "../components/header";
import Sidebar from "../components/sidebar";
import UserManagementCard from "../components/userManagementCard";

function UserManagement() {
	const [sidebarOpen, setSidebarOpen] = useState(true);
	const [expandedCard, setExpandedCard] = useState(null);

	// Sample user data, will be replaced with backend info later
	const users = [
		{
		  id: 1,
		  name: 'John Smith',
		  email: 'john.smith@gmail.com',
		  phone: '(123) 456-789',
		  role: 'Admin',
		  position: 'Example Position',
		  department: 'Example Department',
		  checkedOutEquipment: [
			{
			  name: 'Snow Plow Truck - Ford',
			  checkedOutDate: 'Nov 12, 2025'
			}
		  ]
		},
		{
		  id: 2,
		  name: 'Jane Doe',
		  email: 'jane.doe@gmail.com',
		  phone: '(987) 654-321',
		  role: 'Superintendent',
		  position: 'Farm Manager',
		  department: 'Operations',
		  checkedOutEquipment: [
			{
			  name: 'Tractor - John Deere 4040',
			  checkedOutDate: 'Nov 10, 2025'
			},
			{
			  name: 'Sprayer - Case IH',
			  checkedOutDate: 'Nov 8, 2025'
			}
		  ]
		},
		{
		  id: 3,
		  name: 'John Doe',
		  email: 'john.doe@gmail.com',
		  phone: 'N/A',
		  role: 'User',
		  position: 'Research Assistant',
		  department: 'Research',
		  checkedOutEquipment: []
		},
	];

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
				/>

				{/* The title and brief description of the user management page  */}
				<div className="hero-section">
					<h2>User Management</h2>
					<p>Monitor user accounts and permissions</p>
				</div>

				{/* Scrollable content  */}
				<div className="content">
					{/* Scrollable users are a seperate component */}
					{users.map((item) => (
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
