import React from 'react';
import './Tool.css';

const Tool = ({ name, status, drawer, currentUser, lastUser }) => {
  // `status` can be boolean (true=available, false=taken) or string (legacy).
  let isTaken = false;
  if (typeof status === 'boolean') {
    isTaken = status === false; // false means taken
  } else if (status != null) {
    const s = String(status).toLowerCase();
    if (s.includes('tak')) isTaken = true;
    else if (s.includes('avail') || s.includes('avalib')) isTaken = false;
    else isTaken = !!currentUser;
  } else {
    isTaken = !!currentUser;
  }

  return (
    <div className={`tool ${isTaken ? 'taken' : 'available'}`}>
      <div className="tool-header">
        <h3 className="tool-name">{name}</h3>
        <span className={`tool-status ${isTaken ? 'taken' : 'available'}`}>
          {isTaken ? 'Taken' : 'Available'}
        </span>
      </div>
      
      <div className="tool-details">
        <div className="tool-detail-row">
          <label>Drawer:</label>
          <span className="tool-drawer">#{drawer}</span>
        </div>
        
        {isTaken && (
          <div className="tool-detail-row">
            <label>Current User:</label>
            <span className="tool-current-user">{currentUser || 'Unknown'}</span>
          </div>
        )}
        
        {lastUser && (
          <div className="tool-detail-row">
            <label>Last Used By:</label>
            <span className="tool-last-user">{lastUser}</span>
          </div>
        )}
      </div>
    </div>
  );
};

export default Tool;
