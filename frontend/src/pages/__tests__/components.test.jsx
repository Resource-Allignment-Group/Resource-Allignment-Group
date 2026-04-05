import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter, Routes, Route } from "react-router-dom";
import ResetPassword from "../resetPassword";
import ProtectedRoute from "../../ProtectedRoute";
import AdminRoute from "../../AdminRoute";
import AdminOrSuperintendentRoute from "../../AdminOrSuperintendentRoute";
import Header from "../../components/header";
import { AuthProvider } from "../../Authentication";
import { SidebarProvider } from "../../SidebarContext";

// -----------------------------------------
// Shared mocks
// -----------------------------------------

// Mock useNavigate so we can assert redirects
const mockNavigate = jest.fn();
jest.mock("react-router-dom", () => ({
	...jest.requireActual("react-router-dom"),
	useNavigate: () => mockNavigate,
}));

beforeEach(() => {
	// Reset mockes before each test
	jest.clearAllMocks();
	window.alert = jest.fn();
	// Default fetch behavior where user is not logged in
	global.fetch = jest.fn((url) => {
		if (url.includes("check-session")) {
			return Promise.resolve({
				ok: true,
				status: 200,
				json: () => Promise.resolve({ result: false, user: null, role: null }),
			});
		}
		// Mock notifs count fecth
		if (url.includes("get_user_info")) {
			return Promise.resolve({
				ok: true,
				json: () => Promise.resolve({ num_notifications: 0 }),
			});
		}
		return Promise.reject(new Error(`Unhandled fetch: ${url}`));
	});
});

// -----------------------------------------
// ResetPassword
// -----------------------------------------

function renderResetPassword() {
	// ResetPassword uses useSearchParams to read the token from the URL.
	// MemoryRouter needs a Routes/Route setup for useSearchParams to work
	return render(
		<MemoryRouter initialEntries={["/reset-password?token=test-token-abc"]}>
			<Routes>
				<Route path="/reset-password" element={<ResetPassword />} />
				<Route path="/login" element={<div>Login Page</div>} />
			</Routes>
		</MemoryRouter>,
	);
}

describe("ResetPassword", () => {
	test("renders heading and password input", () => {
		renderResetPassword();
		expect(screen.getByText("Reset Your Password")).toBeInTheDocument();
		expect(screen.getByLabelText("New Password")).toBeInTheDocument();
		expect(screen.getByText("Reset Password")).toBeInTheDocument();
	});

	test("shows error when submitted with empty password", async () => {
		renderResetPassword();
		fireEvent.click(screen.getByText("Reset Password"));
		await waitFor(() =>
			expect(
				screen.getByText("Please enter a new password."),
			).toBeInTheDocument(),
		);
	});

	test("shows error on weak password", async () => {
		renderResetPassword();
		await userEvent.type(screen.getByLabelText("New Password"), "weak");
		fireEvent.click(screen.getByText("Reset Password"));
		await waitFor(() =>
			expect(
				screen.getByText(
					"Password must be at least 8 characters and include uppercase, lowercase, a number, and a symbol (no spaces).",
				),
			).toBeInTheDocument(),
		);
	});

	test("shows success message and redirects on valid reset", async () => {
		global.fetch = jest.fn(() =>
			Promise.resolve({
				ok: true,
				json: () => Promise.resolve({ result: true }),
			}),
		);

		renderResetPassword();
		await userEvent.type(screen.getByLabelText("New Password"), "NewPass1!");
		fireEvent.click(screen.getByText("Reset Password"));

		await waitFor(() =>
			expect(
				screen.getByText(
					"Password reset successfully! Redirecting to login...",
				),
			).toBeInTheDocument(),
		);
	});

	test("shows error message on failed reset", async () => {
		global.fetch = jest.fn(() =>
			Promise.resolve({
				ok: true,
				json: () =>
					Promise.resolve({
						result: false,
						message: "Invalid or expired token",
					}),
			}),
		);

		renderResetPassword();
		await userEvent.type(screen.getByLabelText("New Password"), "NewPass1!");
		fireEvent.click(screen.getByText("Reset Password"));

		await waitFor(() =>
			expect(screen.getByText("Invalid or expired token")).toBeInTheDocument(),
		);
	});

	test("shows server error message on network failure", async () => {
		global.fetch = jest.fn(() => Promise.reject(new Error("Network down")));

		renderResetPassword();
		await userEvent.type(screen.getByLabelText("New Password"), "NewPass1!");
		fireEvent.click(screen.getByText("Reset Password"));

		await waitFor(() =>
			expect(
				screen.getByText("Server error. Please try again later."),
			).toBeInTheDocument(),
		);
	});
});

// -----------------------------------------
// ProtectedRoute
// -----------------------------------------

// Helper to mock authentication responses
function makeAuthFetch(result, user = null, role = null) {
	return jest.fn((url) => {
		if (url.includes("check-session")) {
			return Promise.resolve({
				ok: true,
				status: 200,
				json: () => Promise.resolve({ result, user, role }),
			});
		}
		return Promise.reject(new Error(`Unhandled: ${url}`));
	});
}

describe("ProtectedRoute", () => {
	// Ensures loading state appears while auth check is pending
	test("shows loading state initially", () => {
		// test for fetch that never resolves
		global.fetch = jest.fn(() => new Promise(() => {}));
		render(
			<MemoryRouter>
				<AuthProvider>
					<ProtectedRoute>
						<div>Protected Content</div>
					</ProtectedRoute>
				</AuthProvider>
			</MemoryRouter>,
		);
		expect(screen.getByText("Loading...")).toBeInTheDocument();
	});

	// Allows access if user is authenticated
	test("renders children when user is logged in", async () => {
		global.fetch = makeAuthFetch(true, "user@example.com", "u");
		render(
			<MemoryRouter>
				<AuthProvider>
					<ProtectedRoute>
						<div>Protected Content</div>
					</ProtectedRoute>
				</AuthProvider>
			</MemoryRouter>,
		);
		expect(await screen.findByText("Protected Content")).toBeInTheDocument();
	});

	test("redirects to /login when user is not logged in", async () => {
		global.fetch = makeAuthFetch(false);
		render(
			<MemoryRouter initialEntries={["/home"]}>
				<AuthProvider>
					<Routes>
						<Route
							path="/home"
							element={
								<ProtectedRoute>
									<div>Protected Content</div>
								</ProtectedRoute>
							}
						/>
						<Route path="/login" element={<div>Login Page</div>} />
					</Routes>
				</AuthProvider>
			</MemoryRouter>,
		);
		expect(await screen.findByText("Login Page")).toBeInTheDocument();
	});
});

// -----------------------------------------
// AdminRoute
// -----------------------------------------

describe("AdminRoute", () => {
	// Only admins can access content
	test("renders children for admin users", async () => {
		global.fetch = makeAuthFetch(true, "admin@example.com", "a");
		render(
			<MemoryRouter>
				<AuthProvider>
					<AdminRoute>
						<div>Admin Content</div>
					</AdminRoute>
				</AuthProvider>
			</MemoryRouter>,
		);
		expect(await screen.findByText("Admin Content")).toBeInTheDocument();
	});

	// Non-admin users are redirected
	test("redirects non-admin users to /home", async () => {
		global.fetch = makeAuthFetch(true, "user@example.com", "u");
		render(
			<MemoryRouter initialEntries={["/dashboard"]}>
				<AuthProvider>
					<Routes>
						<Route
							path="/dashboard"
							element={
								<AdminRoute>
									<div>Admin Content</div>
								</AdminRoute>
							}
						/>
						<Route path="/home" element={<div>Home Page</div>} />
					</Routes>
				</AuthProvider>
			</MemoryRouter>,
		);
		expect(await screen.findByText("Home Page")).toBeInTheDocument();
	});

	test("redirects unauthenticated users to /home", async () => {
		global.fetch = makeAuthFetch(false);
		render(
			<MemoryRouter initialEntries={["/dashboard"]}>
				<AuthProvider>
					<Routes>
						<Route
							path="/dashboard"
							element={
								<AdminRoute>
									<div>Admin Content</div>
								</AdminRoute>
							}
						/>
						<Route path="/home" element={<div>Home Page</div>} />
					</Routes>
				</AuthProvider>
			</MemoryRouter>,
		);
		expect(await screen.findByText("Home Page")).toBeInTheDocument();
	});
});

// -----------------------------------------
// AdminOrSuperintendentRoute
// -----------------------------------------

// Validate role-based app views
describe("AdminOrSuperintendentRoute", () => {
	test("renders children for admin", async () => {
		global.fetch = makeAuthFetch(true, "admin@example.com", "a");
		render(
			<MemoryRouter>
				<AuthProvider>
					<AdminOrSuperintendentRoute>
						<div>Restricted Content</div>
					</AdminOrSuperintendentRoute>
				</AuthProvider>
			</MemoryRouter>,
		);
		expect(await screen.findByText("Restricted Content")).toBeInTheDocument();
	});

	test("renders children for superintendent", async () => {
		global.fetch = makeAuthFetch(true, "super@example.com", "s");
		render(
			<MemoryRouter>
				<AuthProvider>
					<AdminOrSuperintendentRoute>
						<div>Restricted Content</div>
					</AdminOrSuperintendentRoute>
				</AuthProvider>
			</MemoryRouter>,
		);
		expect(await screen.findByText("Restricted Content")).toBeInTheDocument();
	});

	test("redirects regular users to /home", async () => {
		global.fetch = makeAuthFetch(true, "user@example.com", "u");
		render(
			<MemoryRouter initialEntries={["/usermanagement"]}>
				<AuthProvider>
					<Routes>
						<Route
							path="/usermanagement"
							element={
								<AdminOrSuperintendentRoute>
									<div>Restricted Content</div>
								</AdminOrSuperintendentRoute>
							}
						/>
						<Route path="/home" element={<div>Home Page</div>} />
					</Routes>
				</AuthProvider>
			</MemoryRouter>,
		);
		expect(await screen.findByText("Home Page")).toBeInTheDocument();
	});
});

// -----------------------------------------
// Header
// -----------------------------------------

// Helper to render header with role + notification count
function renderHeader(role = "u", num_notifications = 0) {
	global.fetch = jest.fn((url) => {
		if (url.includes("check-session")) {
			return Promise.resolve({
				ok: true,
				status: 200,
				json: () =>
					Promise.resolve({ result: true, user: "user@example.com", role }),
			});
		}
		if (url.includes("get_user_info")) {
			return Promise.resolve({
				ok: true,
				json: () => Promise.resolve({ num_notifications }),
			});
		}
		return Promise.reject(new Error(`Unhandled: ${url}`));
	});

	return render(
		<MemoryRouter>
			<AuthProvider>
				<SidebarProvider>
					<Header
						sidebarOpen={false}
						onMenuToggle={jest.fn()}
						num_of_notifications={num_notifications}
						setNotificationsNum={jest.fn()}
						activeTab={null}
					/>
				</SidebarProvider>
			</AuthProvider>
		</MemoryRouter>,
	);
}

describe("Header", () => {
	test("renders the system title", async () => {
		renderHeader();
		expect(
			await screen.findByText("MAFES Equipment Management System"),
		).toBeInTheDocument();
	});

	test("shows Home, My Requests, My Equipment nav tabs for regular users", async () => {
		renderHeader("u");
		expect(await screen.findByText("Home")).toBeInTheDocument();
		expect(screen.getByText("My Requests")).toBeInTheDocument();
		expect(screen.getByText("My Equipment")).toBeInTheDocument();
	});

	test("shows Dashboard tab only for admins", async () => {
		renderHeader("a");
		expect(await screen.findByText("Dashboard")).toBeInTheDocument();
	});

	test("does not show Dashboard tab for regular users", async () => {
		renderHeader("u");
		await screen.findByText("Home");
		expect(screen.queryByText("Dashboard")).not.toBeInTheDocument();
	});

	test("shows User Management tab for admins", async () => {
		renderHeader("a");
		expect(await screen.findByText("User Management")).toBeInTheDocument();
	});

	test("shows User Management tab for superintendents", async () => {
		renderHeader("s");
		expect(await screen.findByText("User Management")).toBeInTheDocument();
	});

	test("does not show User Management tab for regular users", async () => {
		renderHeader("u");
		await screen.findByText("Home");
		expect(screen.queryByText("User Management")).not.toBeInTheDocument();
	});

	test("shows notification bubble when there are notifications", async () => {
		renderHeader("u", 5);
		expect(await screen.findByText("5")).toBeInTheDocument();
	});

	test("shows 99+ when notification count exceeds 99", async () => {
		renderHeader("u", 150);
		expect(await screen.findByText("99+")).toBeInTheDocument();
	});

	test("does not show bubble when there are no notifications", async () => {
		renderHeader("u", 0);
		await screen.findByText("Home");
		expect(screen.queryByText("0")).not.toBeInTheDocument();
	});

	test("clicking Home tab navigates to /home", async () => {
		renderHeader("u");
		fireEvent.click(await screen.findByText("Home"));
		expect(mockNavigate).toHaveBeenCalledWith("/home");
	});

	test("clicking My Requests navigates to /myrequests", async () => {
		renderHeader("u");
		fireEvent.click(await screen.findByText("My Requests"));
		expect(mockNavigate).toHaveBeenCalledWith("/myrequests");
	});
});
