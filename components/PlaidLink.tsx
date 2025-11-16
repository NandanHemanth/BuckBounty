'use client';

import { useEffect, useState } from 'react';
import { usePlaidLink } from 'react-plaid-link';
import axios from 'axios';

interface PlaidLinkProps {
  userId: string;
  onSuccess: () => void;
  onSkip?: () => void;
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
      className="w-full glass border border-green-500/30 hover:glow hover:bg-green-500 hover:text-black disabled:opacity-50 text-green-500 font-semibold py-3.5 px-6 rounded-lg transition-all duration-200 text-base inline-flex items-center justify-center gap-2 hover-lift"
    >
      {ready ? (
        <>
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
          </svg>
          Connect Bank Account
        </>
      ) : (
        <>
          <svg className="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          Loading...
        </>
      )}
    </button>
  );
}
