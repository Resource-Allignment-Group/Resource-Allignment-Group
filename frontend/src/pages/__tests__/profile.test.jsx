import { screen } from "@testing-library/react";
import Profile from "../profile";
import { renderWithProviders } from "../../test-utils/renderWithProviders";

// Test all sections of the Profile page
// This includes form inputs, buttons, and expected responses

// Mock fetch and alert before the tests run
beforeEach(() => {
	global.fetch = jest.fn(() =>
		Promise.resolve({
			ok: true,
			json: () =>
				Promise.resolve({
					user: {
						name: "John Smith",
						email: "john@example.com",
						phone: "1234567890",
						position: "Researcher",
						department: "MAFES",
					},
					num_notifications: 0,
				}),
		}),
	);

	// Mock window.alert to prevent crashes
	window.alert = jest.fn();
});

test("profile test", async () => {
	renderWithProviders(
		<Profile num_of_notifications={0} setNumNotifications={jest.fn()} />,
	);

	// Return a promise and wait for the element to appear.
	const personalDetailsHeader = await screen.findByText(/Personal Details/i);
	expect(personalDetailsHeader).toBeInTheDocument();

	// Verify the loaded data is actually there
	expect(screen.getByDisplayValue("John")).toBeInTheDocument();
	expect(screen.getByDisplayValue("Smith")).toBeInTheDocument();
});
