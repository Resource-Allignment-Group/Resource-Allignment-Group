import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { AuthProvider } from "../../Authentication";
import Login from "../login";

// Test all sections of the Login page
// This includes form inputs, buttons, and expected responses

// Mock useNavigate so we can assert redirects
const mockNavigate = jest.fn();
jest.mock("react-router-dom", () => ({
	...jest.requireActual("react-router-dom"),
	useNavigate: () => mockNavigate,
}));

// Helper - renders Login inside the minimum required providers
function renderLogin() {
	return render(
		<MemoryRouter>
			<AuthProvider>
				<Login />
			</AuthProvider>
		</MemoryRouter>,
	);
}

beforeEach(() => {
	jest.clearAllMocks();
	window.alert = jest.fn();

	// Default: check-session returns not logged in
	global.fetch = jest.fn((url) => {
		if (url.includes("check-session")) {
			return Promise.resolve({
				ok: true,
				status: 200,
				json: () => Promise.resolve({ result: false, user: null, role: null }),
			});
		}
		return Promise.reject(new Error(`Unhandled fetch: ${url}`));
	});
});

// --- Rendering ---

test("renders the Login heading", async () => {
	renderLogin();
	expect(await screen.findByText("Login")).toBeInTheDocument();
});

test("renders email and password inputs", async () => {
	renderLogin();
	expect(
		await screen.findByPlaceholderText("Enter your email"),
	).toBeInTheDocument();
	expect(
		screen.getByPlaceholderText("Enter your password"),
	).toBeInTheDocument();
});

test("renders Sign In, Sign Up, and Forgot Password buttons", async () => {
	renderLogin();
	expect(await screen.findByText("Sign In")).toBeInTheDocument();
	expect(screen.getByText("Sign Up")).toBeInTheDocument();
	expect(screen.getByText("Forgot Password")).toBeInTheDocument();
});

// --- Successful login ---

test("navigates to /home on successful login", async () => {
	global.fetch = jest.fn((url) => {
		if (url.includes("check-session")) {
			return Promise.resolve({
				ok: true,
				status: 200,
				json: () => Promise.resolve({ result: false }),
			});
		}
		if (url.includes("authenticate")) {
			return Promise.resolve({
				ok: true,
				json: () =>
					Promise.resolve({ result: true, message: "success", role: "u" }),
			});
		}
		return Promise.reject(new Error(`Unhandled: ${url}`));
	});

	renderLogin();
	await userEvent.type(
		await screen.findByPlaceholderText("Enter your email"),
		"user@example.com",
	);
	await userEvent.type(
		screen.getByPlaceholderText("Enter your password"),
		"Password1!",
	);
	fireEvent.click(screen.getByText("Sign In"));

	await waitFor(() => expect(mockNavigate).toHaveBeenCalledWith("/home"));
});

// --- Failed login ---

test("shows alert on wrong credentials", async () => {
	global.fetch = jest.fn((url) => {
		if (url.includes("check-session")) {
			return Promise.resolve({
				ok: true,
				status: 200,
				json: () => Promise.resolve({ result: false }),
			});
		}
		if (url.includes("authenticate")) {
			return Promise.resolve({
				ok: true,
				json: () =>
					Promise.resolve({ result: false, message: "Incorrect Credentials" }),
			});
		}
		return Promise.reject(new Error(`Unhandled: ${url}`));
	});

	renderLogin();
	await userEvent.type(
		await screen.findByPlaceholderText("Enter your email"),
		"wrong@example.com",
	);
	await userEvent.type(
		screen.getByPlaceholderText("Enter your password"),
		"wrongpass",
	);
	fireEvent.click(screen.getByText("Sign In"));

	await waitFor(() =>
		expect(window.alert).toHaveBeenCalledWith("Incorrect Credentials"),
	);
	expect(mockNavigate).not.toHaveBeenCalled();
});

test("shows alert on network error", async () => {
	global.fetch = jest.fn((url) => {
		if (url.includes("check-session")) {
			return Promise.resolve({
				ok: true,
				status: 200,
				json: () => Promise.resolve({ result: false }),
			});
		}
		if (url.includes("authenticate")) {
			return Promise.reject(new Error("Network error"));
		}
		return Promise.reject(new Error(`Unhandled: ${url}`));
	});

	renderLogin();
	await userEvent.type(
		await screen.findByPlaceholderText("Enter your email"),
		"user@example.com",
	);
	await userEvent.type(
		screen.getByPlaceholderText("Enter your password"),
		"Password1!",
	);
	fireEvent.click(screen.getByText("Sign In"));

	await waitFor(() =>
		expect(window.alert).toHaveBeenCalledWith("Server Connection Failed"),
	);
});

// --- Forgot password ---

test("alerts when Forgot Password clicked with no email entered", async () => {
	renderLogin();
	await screen.findByText("Forgot Password");
	fireEvent.click(screen.getByText("Forgot Password"));
	await waitFor(() =>
		expect(window.alert).toHaveBeenCalledWith("Please Enter Email"),
	);
});

test("sends forgot_password request when email is filled", async () => {
	global.fetch = jest.fn((url) => {
		if (url.includes("check-session")) {
			return Promise.resolve({
				ok: true,
				status: 200,
				json: () => Promise.resolve({ result: false }),
			});
		}
		if (url.includes("forgot_password")) {
			return Promise.resolve({
				ok: true,
				json: () => Promise.resolve({ result: true }),
			});
		}
		return Promise.reject(new Error(`Unhandled: ${url}`));
	});

	renderLogin();
	await userEvent.type(
		await screen.findByPlaceholderText("Enter your email"),
		"user@example.com",
	);
	fireEvent.click(screen.getByText("Forgot Password"));

	await waitFor(() =>
		expect(window.alert).toHaveBeenCalledWith(
			"Password recovery email sent to user@example.com",
		),
	);
});

// --- Navigation ---

test("Sign Up button navigates to /register", async () => {
	renderLogin();
	await screen.findByText("Sign Up");
	fireEvent.click(screen.getByText("Sign Up"));
	expect(mockNavigate).toHaveBeenCalledWith("/register");
});
