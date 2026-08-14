import { useEffect, useState } from 'react';

export const useJobEvents = (onEvent) => {
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) return;

    const wsBase = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/api/v1';
    const ws = new WebSocket(`${wsBase}/ws/jobs?token=${token}`);

    ws.onopen = () => setConnected(true);

    ws.onmessage = (event) => {
      try {
        const parsed = JSON.parse(event.data);
        if (onEvent) onEvent(parsed);
      } catch {
        // ignore invalid payload
      }
    };

    ws.onclose = () => setConnected(false);

    return () => {
      ws.close();
    };
  }, [onEvent]);

  return { connected };
};
