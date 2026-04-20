import React from "react";
import { render, screen } from "@testing-library/react";
import Notifications from "../notifications";

// ----- MOCKS ----- //

// Mock Sidebar context
jest.mock("../../SidebarContext", () => ({
  useSidebar: () => ({
    sidebarOpen: false,
    openSidebar: jest.fn(),
    closeSidebar: jest.fn(),
  }),
  SidebarProvider: ({ children }) => <>{children}</>,
}));

// Mock Header component
jest.mock("../../components/header", () => (props) => <div>Header Mock</div>);

// Mock Sidebar component
jest.mock("../../components/sidebar", () => (props) => <div>Sidebar Mock</div>);

// Mock NotificationCard component
jest.mock("../../components/notificationCard", () => (props) => (
  <div>Notification Card Mock</div>
));

// Mock global fetch
global.fetch = jest.fn(() =>
  Promise.resolve({
    ok: true,
    json: () =>
      Promise.resolve({
        messages: [{ _id: 1, message: "Test notification" }],
      }),
  })
);

// ----- TESTS ----- //

test("renders Notifications component without crashing", async () => {
  render(<Notifications num_of_notifications={0} setNumNotifications={jest.fn()} />);

  // Check for loading first
  expect(screen.getByText(/loading notifications/i)).toBeInTheDocument();

  // Wait for mock fetch to resolve
//   const card = await screen.findByText("Notification Card Mock");
//   expect(card).toBeInTheDocument();
});

test("renders Header and Sidebar mocks", () => {
  render(<Notifications num_of_notifications={0} setNumNotifications={jest.fn()} />);

  expect(screen.getByText("Header Mock")).toBeInTheDocument();
  expect(screen.getByText("Sidebar Mock")).toBeInTheDocument();
});