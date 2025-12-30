import React from 'react';
import './Drawer.css';

const Drawer = ({ number, tool, isOpen }) => {
  return (
    <div className={`drawer ${isOpen ? 'open' : 'closed'}`}>
      <div className="drawer-header">
        <h3 className="drawer-number">Drawer #{number}</h3>
        <span className={`drawer-status ${isOpen ? 'open' : 'closed'}`}>
          {isOpen ? 'Open' : 'Closed'}
        </span>
      </div>
      <div className="drawer-content">
        <p className="drawer-tool">
          <strong>Tool:</strong> {tool || 'Empty'}
        </p>
      </div>
    </div>
  );
};

export default Drawer;
