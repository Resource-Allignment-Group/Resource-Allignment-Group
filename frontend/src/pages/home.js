import "../styles/default.css";
import { useState, useEffect } from "react";

// Import componets that will make up the home page
import Header from "../components/header";
import Sidebar from "../components/sidebar";
import HomeEquipmentCard from "../components/homeEquipmentCard";
import { API_BASE } from "../config";
function Home({num_of_notifications, setNumNotifications}) {
	const [sidebarOpen, setSidebarOpen] = useState(true);
	const [expandedCard, setExpandedCard] = useState(null);
	const [equipment, setEquipment] = useState([]);

	const GetEquipment = async () => {
		try {
			const res = await fetch(`http://${API_BASE}:5000/get_equipment`, {
				credentials: "include",
			});
			const data = await res.json();
			const equip_list = data["equip_list"]
			return Array.isArray(equip_list) ? equip_list : [];
		} catch (error) {
			console.log(error);
		}		
	}
	useEffect(() => {
        GetEquipment().then((equip_list) =>{
			 setEquipment(equip_list)});
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
					activeTab="Home"
					num_of_notifications={num_of_notifications}
					setNotificationsNum={setNumNotifications}
				/>

				{/* The title and brief description of the home page  */}
				<div className="hero-section">
					<h2>Equipment Overview</h2>
					<p>Manage and track farm equipment</p>
				</div>

				{/* Scrollable content  */}
				<div className="content">
					{/* Scrollable equipment items are a seperate component */}
					{equipment.map((item) => (
						<HomeEquipmentCard
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

export default Home;
