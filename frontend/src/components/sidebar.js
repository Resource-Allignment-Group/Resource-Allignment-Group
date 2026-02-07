import { useState, useEffect } from "react";
import { MdArrowBack } from "react-icons/md";

// This component is used across all pages

function Sidebar({
	isOpen,
	onClose,
	onFilter,
	filterOptions = {},
	onClearFilters,
	savedFilters = null,
}) {
	const [selectedFarm, setSelectedFarm] = useState("All Farms");
	const [searchQuery, setSearchQuery] = useState("");
	const [equipmentClass, setEquipmentClass] = useState("All Classes");
	const [equipmentMake, setEquipmentMake] = useState("All Makes");
	const [status, setStatus] = useState("All Statuses");

	// Load the saved filters on start and when the filters change
	useEffect(() => {
		if (savedFilters) {
			setSelectedFarm(savedFilters.farm || "All Farms");
			setSearchQuery(savedFilters.search || "");
			setEquipmentClass(savedFilters.class || "All Classes");
			setEquipmentMake(savedFilters.make || "All Makes");
			setStatus(savedFilters.status || "All Statuses");
		} else {
			// Reset to defaults when filters are cleared
			setSelectedFarm("All Farms");
			setSearchQuery("");
			setEquipmentClass("All Classes");
			setEquipmentMake("All Makes");
			setStatus("All Statuses");
		}
	}, [savedFilters]);

	// Get the farms from the database
	const farms = ["All Farms"];
	// If there are farms, add all of them
	if (filterOptions.farms) {
		farms.push(...filterOptions.farms);
	}

	// Trigger when the user submits their filter/search query
	const handleSubmit = () => {
		if (onFilter) {
			const filters = {
				farm: selectedFarm,
				search: searchQuery,
				class: equipmentClass,
				make: equipmentMake,
				status: status,
			};
			onFilter(filters);
		}
	};

	// Don't display the sidebar the menu icon wasn't clicked
	if (!isOpen) return null;

	return (
		<div className="sidebar">
			{/* Make sure core components don't scroll with sidebar */}
			<div className="sidebar-fixed">
				<div className="sidebar-header">
					{/* Back Arrow */}
					<button className="back-button" onClick={onClose}>
						<MdArrowBack />
					</button>

					{/* Top submit button */}
					<button className="sidebar-submit" onClick={handleSubmit}>
						Apply
					</button>
				</div>

				{/* Divider line */}
				<hr className="sidebar-divider" />

				{/* Search bar for equipment lookup */}
				<div className="search-box">
					<input
						type="text"
						placeholder="Search"
						value={searchQuery}
						onChange={(e) => setSearchQuery(e.target.value)}
						onKeyDown={(e) => {
							if (e.key === "Enter") {
								handleSubmit();
							}
						}}
					/>
				</div>
			</div>

			{/* All of the farm buttons, as a list  */}
			<h3>Sort by Farm</h3>
			<div className="farm-list">
				{farms.map((farm) => (
					<button
						key={farm}
						className={`farm-item ${selectedFarm === farm ? "active" : ""}`}
						onClick={() => setSelectedFarm(farm)}
					>
						{farm}
					</button>
				))}
			</div>

			{/* The filtering options at the bottom of the sidebar  */}
			{/* Update with actual items later, or from db  */}
			<h3>Filter Options</h3>
			<div className="filter-group">
				<label>Equipment Class</label>
				<select
					value={equipmentClass}
					onChange={(e) => setEquipmentClass(e.target.value)}
				>
					<option>All Classes</option>
					{filterOptions.classes &&
						filterOptions.classes.map((equipclass) => (
							<option key={equipclass} value={equipclass}>
								{equipclass}
							</option>
						))}
				</select>
			</div>

			{/* These are hardcoded since they are the only statuses */}
			<div className="filter-group">
				<label>Equipment Status</label>
				<select value={status} onChange={(e) => setStatus(e.target.value)}>
					<option>All Statuses</option>
					{filterOptions.statuses &&
						filterOptions.statuses.map((statusOption) => (
							<option key={statusOption} value={statusOption}>
								{statusOption}
							</option>
						))}
				</select>
			</div>

			<div className="filter-group">
				<label>Equipment Make</label>
				<select
					value={equipmentMake}
					onChange={(e) => setEquipmentMake(e.target.value)}
				>
					<option>All Makes</option>
					{filterOptions.makes &&
						filterOptions.makes.map((make) => (
							<option key={make} value={make}>
								{make}
							</option>
						))}
				</select>
			</div>

			{/* Let the user clear the loaded filters */}
			<div className="sidebar-fixed">
				<button className="sidebar-submit" onClick={onClearFilters}>
					Clear Filters
				</button>
			</div>
		</div>
	);
}

export default Sidebar;
