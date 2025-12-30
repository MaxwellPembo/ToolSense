import React from 'react';
import Drawer from './Drawer';
import { usePolling } from '../hooks/usePolling';

export function Home() {
  const { data: drawers, error } = usePolling('/api/drawers', 2000);

  return (
    <div>
      <h1>Drawers</h1>

      {error && <p style={{ color: 'red' }}>Error loading drawers: {String(error)}</p>}

      {!drawers && !error && <p>Loading...</p>}

      {Array.isArray(drawers) && (
        <div>
          {drawers.map((d) => (
            <Drawer key={d.number} number={d.number} tool={d.tool} isOpen={d.isOpen} />
          ))}
        </div>
      )}
    </div>
  );
}
