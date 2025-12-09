import { useState } from "react";
import { MdArrowBack } from "react-icons/md";

// This component is used across all pages

function Sidebar({ isOpen, onClose }) {
	const [selectedFarm, setSelectedFarm] = useState("All Farms");

	// All of the quick selection farms for filtering
	const farms = [
		"All Farms",
		"Aroostook",
		"Blueberry Hill",
		"Highmoor",
		"Rogers",
		"Witter",
		"Greenhouse/Gardens",
	];

	// IMPORTANT NOTE: The sidebar won't save any of the selected filtering parameters
	// once it's closed. We may wan't to maintain the last used filters for the user.

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
					<button className="sidebar-submit">Submit</button>
				</div>

				{/* Divider line */}
				<hr className="sidebar-divider" />

				{/* Search bar for equipment lookup */}
				<div className="search-box">
					<input type="text" placeholder="Search" />
				</div>
			</div>

			{/* All of the farm buttons, as a list  */}
			{/* Adjust styling for the active/selected item  */}
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
				<label>Equipment Type</label>
				<select>
					<option>All Types</option>
					<option>Tractor</option>
					<option>Truck</option>
					<option>Forklift</option>
				</select>
			</div>

			<div className="filter-group">
				<label>Equipment Make</label>
				<select>
					<option>All Makes</option>
					<option>John Deere</option>
					<option>Ford</option>
					<option>Yale</option>
				</select>
			</div>

			<div className="filter-group">
				<label>Equipment Year</label>
				<select>
					<option>All Years</option>
					<option>2020</option>
					<option>2019</option>
					<option>2018</option>
				</select>
			</div>

			<div className="filter-group">
				<label>Accessibility</label>
				<select>
					<option>All Users</option>
					<option>Researchers</option>
					<option>Farm Staff</option>
					<option>Superintendent</option>
				</select>
			</div>
		</div>
	);
}

export default Sidebar;
