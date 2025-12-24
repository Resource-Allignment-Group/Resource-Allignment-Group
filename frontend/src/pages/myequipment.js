import "../styles/default.css";
import { useState, useEffect } from "react";

// Import componets that will make up the my equipment page
import Header from "../components/header";
import Sidebar from "../components/sidebar";
import MyEquipmentCard from "../components/myEquipmentCard";

function MyEquipment({num_of_notifications, setNumNotifications}) {
	const [sidebarOpen, setSidebarOpen] = useState(true);
	const [expandedCard, setExpandedCard] = useState(null);
	const [equipment, setEquipment] = useState([]);

	// Sample equipment data, will be replaced with backend info later
	const fillEquipment = async () => {
		try {
			const res = await fetch("http://localhost:5000/get_user_equipment", {
				credentials: "include",
			});
			const data = await res.json();
			return Array.isArray(data) ? data : [];
		} 
		catch (error) {
			console.log(error);
			return []
		}
	}
	useEffect(() => {
			fillEquipment().then((data) =>{
				 setEquipment(data)});
		}, []);

	return (
		<div className="home-container">
			{/* Sidebar is a separate component */}
			<Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

			<div className="main">
				{/* Header is a separate component */}
				<Header
					sidebarOpen={sidebarOpen}
					onMenuToggle={() => setSidebarOpen(true)}
					activeTab="My Equipment"
					num_of_notifications={num_of_notifications}
					setNotificationsNum={setNumNotifications}
				/>

				{/* The title and brief description of the my equipment page  */}
				<div className="hero-section">
					<h2>My Equipment</h2>
					<p>Equipment currently checked out to you</p>
				</div>

				{/* Scrollable content  */}
				<div className="content">
					{/* Scrollable equipment items are a seperate component */}
					{equipment.map((item) => (
						<MyEquipmentCard
							key={item.id}
							equipment={item}
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

export default MyEquipment;
