import "../styles/default.css";
import { useState, useEffect } from "react";

// Import componets that will make up the home page
import Header from "../components/header";
import Sidebar from "../components/sidebar";
import HomeEquipmentCard from "../components/homeEquipmentCard";

function Home({num_of_notifications, setNumNotifications}) {
	const [sidebarOpen, setSidebarOpen] = useState(true);
	const [expandedCard, setExpandedCard] = useState(null);
	const [equipment, setEquipment] = useState([]);

	const GetEquipment = async () => {
		try {
			const res = await fetch("http://localhost:5000/get_equipment", {
				credentials: "include",
			});
			const data = await res.json();

			return Array.isArray(data) ? data : [];
		} catch (error) {
			console.log(error);
		}		
		









	}
	useEffect(() => {
        GetEquipment().then((data) =>{console.log("Equipment returned from backend:", data);
			 setEquipment(data)}); // <-- sets state
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
