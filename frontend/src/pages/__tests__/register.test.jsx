import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import Register from "../register";

// Test all sections of the Login page
// This includes form inputs, buttons, and expected responses

// Mock useNavigate so we can assert redirects
const mockNavigate = jest.fn();
jest.mock("react-router-dom", () => ({
	...jest.requireActual("react-router-dom"),
	useNavigate: () => mockNavigate,
}));

// Helper - renders Login inside the minimum required providers
function renderRegister() {
	return render(
		<MemoryRouter>
			<Register />
		</MemoryRouter>,
	);
}

// Fill out the register form inputs for testing
async function fillForm({
	fname = "John",
	lname = "Doe",
	email = "john@example.com",
	password = "Password1!",
	phone = "2223334444",
} = {}) {
	const inputs = screen.getAllByRole("textbox");
	await userEvent.type(inputs[0], fname);
	await userEvent.type(inputs[1], lname);
	await userEvent.type(inputs[2], email);
	await userEvent.type(
		document.querySelector("input[type='password']"),
		password,
	);
	await userEvent.type(inputs[3], phone);
}

beforeEach(() => {
	jest.clearAllMocks();
	window.alert = jest.fn();
});

// --- Rendering ---

test("renders the Register heading", () => {
	renderRegister();
	expect(screen.getByText("Register")).toBeInTheDocument();
});

test("renders all form labels", () => {
	renderRegister();
	expect(screen.getByText("First Name")).toBeInTheDocument();
	expect(screen.getByText("Last Name")).toBeInTheDocument();
	expect(screen.getByText("Email")).toBeInTheDocument();
	expect(screen.getByText("Password")).toBeInTheDocument();
	expect(screen.getByText("Phone Number")).toBeInTheDocument();
});

test("renders Sign Up and Back to Login buttons", () => {
	renderRegister();
	expect(screen.getByText("Sign Up")).toBeInTheDocument();
	expect(screen.getByText("Back to Login")).toBeInTheDocument();
});

// --- Validation ---

test("alerts when name fields are empty", async () => {
	renderRegister();
	fireEvent.click(screen.getByText("Sign Up"));
	await waitFor(() =>
		expect(window.alert).toHaveBeenCalledWith(
			"Please enter your first and last name",
		),
	);
});

test("alerts on invalid email format", async () => {
	renderRegister();
	await fillForm({ email: "not-an-email" });
	fireEvent.click(screen.getByText("Sign Up"));
	await waitFor(() =>
		expect(window.alert).toHaveBeenCalledWith(
			"Please enter a valid email address",
		),
	);
});

test("alerts on weak password", async () => {
	renderRegister();
	await fillForm({ password: "weak" });
	fireEvent.click(screen.getByText("Sign Up"));
	await waitFor(() =>
		expect(window.alert).toHaveBeenCalledWith(
			expect.stringContaining("Password must be at least 8 characters"),
		),
	);
});

test("alerts on invalid phone number", async () => {
	renderRegister();
	await fillForm({ phone: "123" });
	fireEvent.click(screen.getByText("Sign Up"));
	await waitFor(() =>
		expect(window.alert).toHaveBeenCalledWith(
			"Please enter a valid phone number",
		),
	);
});

// --- Successful registration ---

test("shows success alert and navigates to /login on success", async () => {
	global.fetch = jest.fn(() =>
		Promise.resolve({
			ok: true,
			json: () => Promise.resolve({ result: true }),
		}),
	);

	renderRegister();
	await fillForm();
	fireEvent.click(screen.getByText("Sign Up"));

	await waitFor(() =>
		expect(window.alert).toHaveBeenCalledWith(
			"Account Request has been sent to Admin\nAwaiting Approval",
		),
	);
	expect(mockNavigate).toHaveBeenCalledWith("/login");
});

// --- Failed registration ---

test("shows error alert when backend returns failure", async () => {
	global.fetch = jest.fn(() =>
		Promise.resolve({
			ok: true,
			json: () =>
				Promise.resolve({ result: false, message: "Email already exists" }),
		}),
	);

	renderRegister();
	await fillForm({ email: "existing@example.com" });
	fireEvent.click(screen.getByText("Sign Up"));

	await waitFor(() =>
		expect(window.alert).toHaveBeenCalledWith("Email already exists"),
	);
});

// --- Navigation ---

test("Back to Login navigates to /login", () => {
	renderRegister();
	fireEvent.click(screen.getByText("Back to Login"));
	expect(mockNavigate).toHaveBeenCalledWith("/login");
});
