'use client';

import { useEffect, useState } from 'react';
import { usePlaidLink } from 'react-plaid-link';
import axios from 'axios';

interface PlaidLinkProps {
  userId: string;
  onSuccess: () => void;
}

export default function PlaidLink({ userId, onSuccess }: PlaidLinkProps) {
  const [linkToken, setLinkToken] = useState<string | null>(null);

  useEffect(() => {
    // Create link token when component mounts
    const createLinkToken = async () => {
      try {
        const response = await axios.post('http://localhost:8000/api/plaid/create_link_token', {
          user_id: userId
        });
        setLinkToken(response.data.link_token);
      } catch (error) {
        console.error('Error creating link token:', error);
      }
    };

    createLinkToken();
  }, [userId]);

  const { open, ready } = usePlaidLink({
    token: linkToken,
    onSuccess: async (public_token) => {
      // Exchange public token for access token
      try {
        await axios.post('http://localhost:8000/api/plaid/exchange_public_token', {
          public_token,
          user_id: userId
        });
        
        // Fetch initial transactions
        await axios.get(`http://localhost:8000/api/transactions/${userId}?days=30`);
        
        onSuccess();
      } catch (error) {
        console.error('Error exchanging token:', error);
      }
    },
  });

  return (
    <button
      onClick={() => open()}
      disabled={!ready}
      className="w-full bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-400 text-white font-bold py-4 px-8 rounded-lg transition-colors text-lg"
    >
      {ready ? '🔗 Connect Bank Account' : '⏳ Loading...'}
    </button>
  );
}
