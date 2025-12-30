import React from 'react';
import Tool from './Tool';
import { usePolling } from '../hooks/usePolling';

export function ToolManager() {
  const { data: drawers, error } = usePolling('/api/drawers', 2000);

  return (
    <div>
      <h2>Tools</h2>
      {error && <p style={{ color: 'red' }}>Error loading drawers: {String(error)}</p>}

      {!drawers && !error && <p>Loading...</p>}

      {Array.isArray(drawers) && (
        <div>
          {drawers.map((d) => {
            // API `Status` is now a boolean: true = available, false = taken.
            // But support older string shapes too.
            let computedStatus;
            const rawStatus = d.status !== undefined ? d.status : (d.Status !== undefined ? d.Status : null);

            if (typeof rawStatus === 'boolean') {
              computedStatus = rawStatus ? 'available' : 'taken';
            } else if (rawStatus !== null) {
              const raw = String(rawStatus).trim().toLowerCase();
              if (raw.includes('tak')) computedStatus = 'taken';
              else if (raw.includes('avail') || raw.includes('avalib') || raw === 'true' || raw === '1') computedStatus = 'available';
              else computedStatus = d.currentUser ? 'taken' : 'available';
            } else {
              computedStatus = d.currentUser ? 'taken' : 'available';
            }

            return (
              <Tool
                key={d.number}
                name={d.tool}
                status={computedStatus}
                drawer={d.number}
                currentUser={d.currentUser}
                lastUser={d.lastUser}
              />
            );
          })}
        </div>
      )}
    </div>
  );
}