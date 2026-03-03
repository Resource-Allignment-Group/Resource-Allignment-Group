import "../styles/default.css";
import { useState, useEffect } from "react";
import { API_BASE } from "../config";
import Header from "../components/header";
import Sidebar from "../components/sidebar";
import MyEquipmentCard from "../components/myEquipmentCard";
import { useSidebar } from "../SidebarContext";

// Shows all equipment currently checked out by the user

function MyEquipment({ num_of_notifications, setNumNotifications }) {
	const { sidebarOpen, openSidebar, closeSidebar } = useSidebar();
	const [expandedCard, setExpandedCard] = useState(null);
	const [equipment, setEquipment] = useState([]);
	const [isLoading, setIsLoading] = useState(true);

	// Load all of the equip checked out by user
	const fillEquipment = async () => {
		try {
			const res = await fetch(`http://${API_BASE}:5000/get_user_equipment`, {
				credentials: "include",
			});
			const data = await res.json();
			const equip_list = data["equip_list"];
			return Array.isArray(equip_list) ? equip_list : [];
		} catch (error) {
			alert("Failed to Load Equipment");
			return [];
		}
	};
	useEffect(() => {
		setIsLoading(true);
		fillEquipment().then((equip_list) => {
			setEquipment([...equip_list].reverse());
			setIsLoading(false);
		});
	}, []);

	return (
		<div className="home-container">
			{/* Sidebar is a separate component */}
			<Sidebar isOpen={sidebarOpen} onClose={closeSidebar} />

			<div className="main">
				{/* Header is a separate component */}
				<Header
					sidebarOpen={sidebarOpen}
					onMenuToggle={openSidebar}
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
					{isLoading ? (
						<div className="response-text">
							<p>Loading Your Equipment...</p>
						</div>
					) : equipment.length > 0 ? (
						equipment.map((item) => (
							<MyEquipmentCard
								key={item.id}
								equipment={item}
								isExpanded={expandedCard === item.id}
								onToggle={() =>
									setExpandedCard(expandedCard === item.id ? null : item.id)
								}
							/>
						))
					) : (
						<div className="response-text">
							<p>You have no equipment checked out.</p>
						</div>
					)}
				</div>
			</div>
		</div>
	);
}

export default MyEquipment;
