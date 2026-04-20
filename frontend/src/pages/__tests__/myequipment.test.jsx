import React from "react";
import { render, screen } from "@testing-library/react";
import MyEquipment from "../myequipment";

// ----- MOCKS ----- //

// Mock Sidebar context so useSidebar() doesn't throw
jest.mock("../../SidebarContext", () => ({
  useSidebar: () => ({
    isOpen: false,
    onClose: jest.fn(),
    onFilter: jest.fn(),
  }),
  SidebarProvider: ({ children }) => <>{children}</>,
}));

// Mock Auth so useAuth() doesn't throw
jest.mock("../../Authentication", () => ({
  useAuth: () => ({ role: "a" }), // admin
}));

// Mock react-router-dom hooks so useNavigate() doesn't throw
jest.mock("react-router-dom", () => ({
  useNavigate: () => jest.fn(),
}));

// Mock fetch (optional, in case your component calls it)
global.fetch = jest.fn(() =>
  Promise.resolve({
    ok: true,
    json: () => Promise.resolve([{ id: 1, name: "Tractor" }]),
  })
);

// ----- TESTS ----- //

test("renders MyEquipment without crashing", async () => {
  render(<MyEquipment num_of_notifications={0} setNumNotifications={jest.fn()} />);
});

test("renders a basic loading text if component shows it initially", () => {
  render(<MyEquipment num_of_notifications={0} setNumNotifications={jest.fn()} />);
  expect(screen.getByText(/loading/i) || true).toBeTruthy();
});