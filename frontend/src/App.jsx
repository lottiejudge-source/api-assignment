import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import Coins from '../Coins';
import { AuthContext } from '../../context/AuthContext';

vi.mock('../../api/axios', () => ({
  default: {
    get: vi.fn(() => Promise.resolve({ 
      data: [{ coin_id: '123e4567-e89b-12d3-a456-426614174000', coin_name: 'Front End Coin', coin_complete: false }] 
    })),
  },
}));

const renderWithAuth = (ui, user) => {
  return render(
    <AuthContext.Provider value={{ user, logout: vi.fn() }}>
      {ui}
    </AuthContext.Provider>
  );
};

describe('Coins Page (TDD)', () => {
  it('renders coin list with completion status but hides admin controls for standard users', async () => {
    const standardUser = { user_id: '1', user_name: 'alex', role: 'user' };
    renderWithAuth(<Coins />, standardUser);

    expect(await screen.findByText('Supervision Duty Coin')).toBeInTheDocument();
    expect(screen.getByText(/Pending/i)).toBeInTheDocument();
    expect(screen.queryByText(/Add New Coin/i)).not.toBeInTheDocument();
  });

  it('renders admin controls for admin users', async () => {
    const adminUser = { user_id: '2', user_name: 'admin', role: 'admin' };
    renderWithAuth(<Coins />, adminUser);

    expect(await screen.findByText('Supervision Duty Coin')).toBeInTheDocument();
    expect(screen.getByText(/Add New Coin/i)).toBeInTheDocument();
  });
});