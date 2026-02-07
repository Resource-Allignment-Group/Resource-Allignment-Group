import { render } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { AuthProvider } from '../Authentication';
import { SidebarProvider } from '../SidebarContext';

export function renderWithProviders(ui) {
  return render(
    <BrowserRouter>
      <AuthProvider>
        <SidebarProvider>
          {ui}
        </SidebarProvider>
      </AuthProvider>
    </BrowserRouter>
  );
}
