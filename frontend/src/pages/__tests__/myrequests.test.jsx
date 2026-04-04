import React from "react";
import { render, screen } from "@testing-library/react";
import MyRequests from "../myrequests";

// ----- MOCKS ----- //

// Mock Sidebar context so useSidebar() doesn't throw
jest.mock("../../SidebarContext", () => ({
  useSidebar: () => ({
    sidebarOpen: false,
    openSidebar: jest.fn(),
    closeSidebar: jest.fn(),
  }),
  SidebarProvider: ({ children }) => <>{children}</>,
}));

// Mock Auth if Header uses it (optional)
jest.mock("../../components/header", () => (props) => (
  <div>Header Mock</div>
));

// Mock Sidebar component
jest.mock("../../components/sidebar", () => (props) => <div>Sidebar Mock</div>);

// Mock MyRequestsCard component
jest.mock("../../components/myRequestsCard", () => (props) => (
  <div>Request Card Mock</div>
));

// Mock fetch globally
global.fetch = jest.fn(() =>
  Promise.resolve({
    ok: true,
    json: () =>
      Promise.resolve({
        notifications: [{ _id: 1 }],
        equipment: [{ name: "Excavator" }],
      }),
  })
);

// ----- TESTS ----- //

test("renders MyRequests without crashing", async () => {
  render(<MyRequests num_of_notifications={0} setNumNotifications={jest.fn()} />);

  // Check for loading text first
  expect(screen.getByText(/loading requests/i)).toBeInTheDocument();

});

test("renders Header and Sidebar mocks", () => {
  render(<MyRequests num_of_notifications={0} setNumNotifications={jest.fn()} />);

  expect(screen.getByText("Header Mock")).toBeInTheDocument();
  expect(screen.getByText("Sidebar Mock")).toBeInTheDocument();
});