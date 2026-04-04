import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import Login from "../login";
import { renderWithProviders } from "../../test-utils/renderWithProviders";

// Mock useNavigate
const mockNavigate = jest.fn();
jest.mock("react-router-dom", () => ({
  ...jest.requireActual("react-router-dom"),
  useNavigate: () => mockNavigate,
}));
const mockLogin = jest.fn();
// Mock useAuth
jest.mock("../../Authentication", () => {
  const actual = jest.requireActual("../../Authentication");
  return {
    ...actual,
    useAuth: () => ({
      login: mockLogin,
    }),
  };
});

beforeEach(() => {
  jest.clearAllMocks();
  window.alert = jest.fn();
});

test("successful login redirects to home", async () => {
  mockLogin.mockResolvedValue({ success: true });

  renderWithProviders(<Login />);

  await userEvent.type(screen.getByPlaceholderText(/enter your email/i), "test@example.com");
  await userEvent.type(screen.getByPlaceholderText(/enter your password/i), "password123");

  await userEvent.click(screen.getByText(/sign in/i));

  expect(mockLogin).toHaveBeenCalledWith("test@example.com", "password123");
  expect(mockNavigate).toHaveBeenCalledWith("/home");
});

test("failed login shows alert", async () => {
  mockLogin.mockResolvedValue({ success: false, message: "Invalid credentials" });

  renderWithProviders(<Login />);

  await userEvent.type(screen.getByPlaceholderText(/enter your email/i), "test@example.com");
  await userEvent.type(screen.getByPlaceholderText(/enter your password/i), "wrongpass");

  await userEvent.click(screen.getByText(/sign in/i));

  expect(window.alert).toHaveBeenCalledWith("Invalid credentials");
});

test("forgot password without email shows alert", async () => {
  renderWithProviders(<Login />);

  await userEvent.click(screen.getByText(/forgot password/i));

  expect(window.alert).toHaveBeenCalledWith("Please Enter Email");
});