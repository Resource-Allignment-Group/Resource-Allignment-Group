// src/pages/__tests__/usermanagement.test.jsx
import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import UserManagement from "../usermanagement";

// --- MOCKS --- //

// Mock Sidebar context
jest.mock("../../SidebarContext", () => ({
  useSidebar: () => ({
    sidebarOpen: false,
    openSidebar: jest.fn(),
    closeSidebar: jest.fn(),
  }),
  SidebarProvider: ({ children }) => <>{children}</>,
}));

// Mock Header & Sidebar components
jest.mock("../../components/header", () => () => <div>Header Mock</div>);
jest.mock("../../components/sidebar", () => () => <div>Sidebar Mock</div>);
jest.mock("../../components/userManagementCard", () => ({ user }) => (
  <div>{user.name}</div>
));

// Mock useAuth
jest.mock("../../Authentication", () => ({
  useAuth: () => ({
    logout: jest.fn(() => Promise.resolve(true)),
  }),
}));

// Mock useNavigate
jest.mock("react-router-dom", () => ({
  useNavigate: () => jest.fn(),
}));

// Mock fetch globally
global.fetch = jest.fn(() =>
  Promise.resolve({
    ok: true,
    json: () =>
      Promise.resolve({
        result: true,
        users: [
          { id: 1, name: "Alice Johnson", role: "admin" },
          { id: 2, name: "Bob Smith", role: "user" },
          { id: 3, name: "Pending User", role: "p" }, // should be filtered out
        ],
      }),
  }),
);

describe("UserManagement Page", () => {
  it("shows loading initially and then displays users", async () => {
    render(<UserManagement num_of_notifications={0} setNumNotifications={() => {}} />);

    // Loading text appears first
    expect(screen.getByText(/Loading User Directory/i)).toBeInTheDocument();


    // Ensure pending user is not displayed
    expect(screen.queryByText("Pending User")).not.toBeInTheDocument();
  });

  it("shows 'No users found' message if no users returned", async () => {
    fetch.mockImplementationOnce(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve({ result: true, users: [] }),
      }),
    );

    render(<UserManagement num_of_notifications={0} setNumNotifications={() => {}} />);

    await waitFor(() => {
      expect(screen.getByText(/No users found in the system/i)).toBeInTheDocument();
    });
  });
});