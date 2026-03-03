import { createContext, useContext, useState } from "react";

// The context that keeps track of the sidebar being open/closed

const SidebarContext = createContext(null);

export const SidebarProvider = ({ children }) => {
	const [sidebarOpen, setSidebarOpen] = useState(false); // Default to closed

	const openSidebar = () => setSidebarOpen(true);
	const closeSidebar = () => setSidebarOpen(false);
	const toggleSidebar = () => setSidebarOpen((prev) => !prev);

	return (
		<SidebarContext.Provider
			value={{ sidebarOpen, openSidebar, closeSidebar, toggleSidebar }}
		>
			{children}
		</SidebarContext.Provider>
	);
};

export const useSidebar = () => {
	const context = useContext(SidebarContext);
	if (!context) {
		throw new Error("useSidebar must be used within a SidebarProvider");
	}
	return context;
};
