import "../styles/default.css";
import { useState, useEffect, useCallback } from "react";

// Import componets that will make up the home page
import Header from "../components/header";
import Sidebar from "../components/sidebar";
import HomeEquipmentCard from "../components/homeEquipmentCard";

function Home({ num_of_notifications, setNumNotifications }) {
	const [sidebarOpen, setSidebarOpen] = useState(true);
	const [expandedCard, setExpandedCard] = useState(null);
	const [equipment, setEquipment] = useState([]);
	const [selectedEquipment, setSelectedEquipment] = useState(new Set());
	const [selectAll, setSelectAll] = useState(false);
	const [filteredEquipment, setFilteredEquipment] = useState([]);
	const [activeFilters, setActiveFilters] = useState(() => {
		// Initialize the filter states from localStorage instead of defaults
		const saved = localStorage.getItem("equipmentFilters");
		return saved ? JSON.parse(saved) : null;
	});
	const [filterOptions, setFilterOptions] = useState({
		farms: [],
		classes: [],
		makes: [],
		statuses: [],
	});

	// Use to display equipment in database
	const GetEquipment = async () => {
		try {
			const res = await fetch("http://localhost:5000/get_equipment", {
				credentials: "include",
			});
			const data = await res.json();
			const equip_list = data["equip_list"];
			return Array.isArray(equip_list) ? equip_list : [];
		} catch (error) {
			console.log(error);
		}
	};

	// Look through the database and get the possible values
	// that equipment can be filtered by
	const GetFilterOptions = async () => {
		try {
			const res = await fetch("http://localhost:5000/get_filter_options", {
				credentials: "include",
			});
			const data = await res.json();
			if (data.result) {
				setFilterOptions({
					farms: data.farms || [],
					classes: data.classes || [],
					makes: data.makes || [],
					statuses: data.statuses || [],
				});
			}
		} catch (error) {
			console.log("Error fetching filter options:", error);
		}
	};

	// On page load, fetch the equipment and the filter options for the sidebar
	useEffect(() => {
		// Fetch both equipment and filter options on load
		GetEquipment().then((equip_list) => {
			setEquipment(equip_list);
			setFilteredEquipment(equip_list);
		});
		GetFilterOptions();
	}, []);

	// Filter logic to determine what equipment should be displayed
	// Must use useCallback so that the filters aren't infinitely rendered
	// This method allows the filters to only be reloaded when the equipment changes
	// allowing for the most up-to-date info
	const applyFilters = useCallback(
		(filters) => {
			let filtered = [...equipment];

			// Filter by farm
			if (filters.farm && filters.farm !== "All Farms") {
				filtered = filtered.filter((item) => {
					const itemFarm = item.farm ? item.farm.toUpperCase() : "";
					const filterFarm = filters.farm.toUpperCase();
					return itemFarm === filterFarm;
				});
			}

			// Filter by status
			if (filters.status && filters.status !== "All Status") {
				filtered = filtered.filter((item) => {
					switch (filters.status) {
						case "Available":
							return !item.checked_out && !item.damaged && !item.unavailable;
						case "Checked Out":
							return item.checked_out === true;
						case "Damaged":
							return item.damaged === true;
						case "Unavailable":
							return item.unavailable === true;
						default:
							return true;
					}
				});
			}

			// Filter by equipment class
			if (filters.class && filters.class !== "All Classes") {
				filtered = filtered.filter((item) => {
					const itemClass = item.class ? item.class.toLowerCase() : "";
					const filterClass = filters.class.toLowerCase();
					return itemClass === filterClass;
				});
			}

			// Filter by equipment make
			if (filters.make && filters.make !== "All Makes") {
				filtered = filtered.filter((item) => {
					const itemMake = item.make ? item.make.toLowerCase() : "";
					const filterMake = filters.make.toLowerCase();
					return itemMake === filterMake;
				});
			}

			setFilteredEquipment(filtered);
			// Clear selections when filtering
			setSelectedEquipment(new Set());
			setSelectAll(false);
		},
		[equipment],
	);

	// On page load, apply the saved filters after the equipment loads
	useEffect(() => {
		if (equipment.length > 0) {
			const savedFilters = localStorage.getItem("equipmentFilters");
			if (savedFilters) {
				try {
					const filters = JSON.parse(savedFilters);
					applyFilters(filters);
				} catch (e) {
					console.log("Error loading saved filters:", e);
				}
			}
		}
	}, [equipment, applyFilters]);

	// Filter equipment based on the selected filters
	const handleFilter = (filters) => {
		setActiveFilters(filters);

		// Save the filters to the users local storage
		localStorage.setItem("equipmentFilters", JSON.stringify(filters));
		applyFilters(filters, equipment);
	};

	// Allow the user to clear the loaded filter params
	const handleClearFilters = () => {
		localStorage.removeItem("equipmentFilters");
		setActiveFilters(null);
		setFilteredEquipment(equipment);
		setSelectedEquipment(new Set());
		setSelectAll(false);
	};

	// Handle individual checkbox toggle
	const handleEquipmentSelect = (equipmentId) => {
		const newSelected = new Set(selectedEquipment);
		if (newSelected.has(equipmentId)) {
			newSelected.delete(equipmentId);
		} else {
			newSelected.add(equipmentId);
		}
		setSelectedEquipment(newSelected);

		// Update select all checkbox state
		setSelectAll(
			newSelected.size === filteredEquipment.length &&
				filteredEquipment.length > 0,
		);
	};

	// Handle select all toggle
	const handleSelectAll = () => {
		if (selectAll) {
			setSelectedEquipment(new Set());
		} else {
			const allFilteredIds = new Set(filteredEquipment.map((item) => item.id));
			setSelectedEquipment(allFilteredIds);
		}
		setSelectAll(!selectAll);
	};

	// Mark selected equipment as unavailable
	const handleMarkUnavailable = async (makeUnavailable = true) => {
		if (selectedEquipment.size === 0) {
			alert("Please select at least one equipment item");
			return;
		}

		const action = makeUnavailable ? "unavailable" : "available";
		const confirmMessage = `Are you sure you want to mark ${selectedEquipment.size} item(s) as ${action}?`;
		// Confirmation messages before action
		if (!window.confirm(confirmMessage)) {
			return;
		}
		// Mark the item as unavailable/available
		try {
			const res = await fetch(
				"http://localhost:5000/mark_equipment_unavailable",
				{
					method: "POST",
					credentials: "include",
					headers: { "Content-Type": "application/json" },
					body: JSON.stringify({
						equipment_ids: Array.from(selectedEquipment),
						unavailable: makeUnavailable,
					}),
				},
			);

			const data = await res.json();

			if (res.ok && data.result) {
				// Output response for marking equipment as unavailable/available
				alert(data.message);

				// Refresh equipment list
				const updatedEquipment = await GetEquipment();
				setEquipment(updatedEquipment);

				// Re-apply filters if they exist
				if (activeFilters) {
					handleFilter(activeFilters);
				} else {
					setFilteredEquipment(updatedEquipment);
				}
				// Clear selections
				setSelectedEquipment(new Set());
				setSelectAll(false);
			} else {
				alert(data.error || "Failed to update equipment");
			}
		} catch (error) {
			console.log("Error marking equipment unavailable:", error);
			alert("An error occurred while updating equipment");
		}
	};

	return (
		<div className="home-container">
			{/* Sidebar is a separate component */}
			<Sidebar
				isOpen={sidebarOpen}
				onClose={() => setSidebarOpen(false)}
				onFilter={handleFilter}
				filterOptions={filterOptions}
				onClearFilters={handleClearFilters}
				savedFilters={activeFilters}
			/>

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

				{/* The "select all" checkbox */}
				{filteredEquipment.length > 0 && (
					<div className="admin-controls">
						<p className="filter-indicator">
							Showing {filteredEquipment.length} of {equipment.length} items
						</p>
						<div className="select-all">
							<label className="checkbox-label">
								<input
									type="checkbox"
									checked={selectAll}
									onChange={handleSelectAll}
								/>
								Select All ({selectedEquipment.size} selected)
							</label>
						</div>

						{/* Buttons to make equipment as unavailable/available */}
						<div className="mark-buttons">
							<button
								className="btn-secondary"
								onClick={() => handleMarkUnavailable(true)}
								disabled={selectedEquipment.size === 0}
							>
								Mark as Unavailable
							</button>
							<button
								className="btn-secondary"
								onClick={() => handleMarkUnavailable(false)}
								disabled={selectedEquipment.size === 0}
							>
								Mark as Available
							</button>
						</div>
					</div>
				)}

				{/* Scrollable content  */}
				<div className="content">
					{/* Scrollable equipment items are a seperate component */}
					{filteredEquipment.length === 0 ? (
						<div className="no-results">
							<p>No equipment found matching your filters.</p>
						</div>
					) : (
						filteredEquipment.map((item) => (
							<HomeEquipmentCard
								key={item.id}
								equipment={item}
								isExpanded={expandedCard === item.id}
								onToggle={() =>
									setExpandedCard(expandedCard === item.id ? null : item.id)
								}
								isSelected={selectedEquipment.has(item.id)}
								onSelect={handleEquipmentSelect}
							/>
						))
					)}
				</div>
			</div>
		</div>
	);
}

export default Home;
