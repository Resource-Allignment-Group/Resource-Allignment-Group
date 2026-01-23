
//This is just a mock back end server
//please ask if you have any questions but I beleive it is rather intuative once it is explained
global.fetch = jest.fn((url) => {
  if (url.includes("get_user_info")) {
    return Promise.resolve({
      ok: true,
      json: () =>
        Promise.resolve({
          num_notifications: 3,
        }),
    });
  }

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

  return Promise.reject(new Error(`Unhandled fetch: ${url}`));
});
