import { useState, useEffect } from 'react';
import api from '../api/axios';
import { useAuth } from '../context/AuthContext';

export default function Coins() {
  const { user } = useAuth();
  const [coins, setCoins] = useState([]);
  const [coinName, setCoinName] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    fetchCoins();
  }, []);

  const fetchCoins = async () => {
    try {
      const res = await api.get('/coins/');
      setCoins(res.data);
    } catch (err) {
      setError('Failed to fetch coins.');
    }
  };

  const handleCreateCoin = async (e) => {
    e.preventDefault();
    try {
      await api.post('/coins/', { coin_name: coinName, coin_complete: false });
      setCoinName('');
      fetchCoins();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create coin');
    }
  };

  return (
    <div style={{ maxWidth: '800px', margin: '0 auto' }}>
      <h2>Coins Dashboard</h2>
      {error && <p style={{ color: 'red' }}>{error}</p>}

      {user?.role === 'admin' && (
        <form onSubmit={handleCreateCoin} style={{ marginBottom: '2rem', padding: '1rem', border: '1px solid #ccc' }}>
          <h3>Add New Coin</h3>
          <input
            type="text"
            placeholder="Coin Name"
            value={coinName}
            onChange={(e) => setCoinName(e.target.value)}
            required
          />
          <button type="submit">Create Coin</button>
        </form>
      )}

      {/* Coin List */}
      <ul style={{ listStyle: 'none', padding: 0 }}>
        {coins.map((coin) => (
          <li key={coin.coin_id} style={{ padding: '0.75rem', borderBottom: '1px solid #eee', display: 'flex', justifyContent: 'space-between' }}>
            <span><strong>{coin.coin_name}</strong></span>
            <span>
              Status: {coin.coin_complete ? 'Completed' : 'Incomplete'}
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}