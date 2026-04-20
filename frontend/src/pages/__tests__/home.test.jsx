import { screen } from "@testing-library/react";
import Home from "../home";
import { renderWithProviders } from "../../test-utils/renderWithProviders";

beforeEach(() => {
  global.fetch = jest.fn((url) => {
    // Mock equipment fetch
    if (url.includes("get_equipment")) {
      return Promise.resolve({
        ok: true,
        json: () =>
          Promise.resolve({
            equip_list: [
              { id: 1, name: "Tractor" },
              { id: 2, name: "Plow" },
            ],
          }),
      });
    }

    // Mock filter options fetch
    if (url.includes("get_filter_options")) {
      return Promise.resolve({
        ok: true,
        json: () =>
          Promise.resolve({
            result: true,
            farms: [],
            classes: [],
            makes: [],
            statuses: [],
          }),
      });
    }
    if (url.includes("get_user_info")) {
    return Promise.resolve({
        ok: true,
        json: () =>
        Promise.resolve({
            num_notifications: 0,
        }),
    });
    }
    return Promise.reject(new Error(`Unhandled fetch: ${url}`));
  });

  window.alert = jest.fn();
  window.confirm = jest.fn(() => true);
});

test("home page renders equipment after loading", async () => {
  renderWithProviders(
    <Home num_of_notifications={0} setNumNotifications={jest.fn()} />
  );

  expect(screen.getByText(/Equipment Overview/i)).toBeInTheDocument();
  expect(screen.getByText(/Manage and track farm equipment/i)).toBeInTheDocument();

  expect(screen.getByText(/Loading Equipment/i)).toBeInTheDocument();

  const tractor = await screen.findByText("Tractor");
  const plow = await screen.findByText("Plow");

  expect(tractor).toBeInTheDocument();
  expect(plow).toBeInTheDocument();
});