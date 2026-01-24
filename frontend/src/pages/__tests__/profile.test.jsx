import { screen, waitFor } from '@testing-library/react';
import Profile from '../profile';
import { renderWithProviders } from '../../test-utils/renderWithProviders';

test('profile test', async () => {
  renderWithProviders(
    <Profile num_of_notifications={0} setNumNotifications={jest.fn()} />
  );

  expect(
    screen.getByText(/Personal Details/i)
  ).toBeInTheDocument();

});
