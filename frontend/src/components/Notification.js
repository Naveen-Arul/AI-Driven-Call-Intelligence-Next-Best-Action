import React, { useEffect } from 'react';

function Notification({ type = 'info', message, onClose, duration = 5000 }) {
  useEffect(() => {
    if (duration > 0) {
      const timer = setTimeout(() => {
        onClose();
      }, duration);
      return () => clearTimeout(timer);
    }
  }, [duration, onClose]);

  const styles = {
    success: {
      background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
      borderLeft: '4px solid #065f46',
    },
    error: {
      background: 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)',
      borderLeft: '4px solid #991b1b',
    },
    warning: {
      background: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
      borderLeft: '4px solid #92400e',
    },
    info: {
      background: 'linear-gradient(135deg, #0284c7 0%, #0891b2 100%)',
      borderLeft: '4px solid #075985',
    },
  };

  const icons = {
    success: (
      <svg style={{ width: '24px', height: '24px', flexShrink: 0 }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    ),
    error: (
      <svg style={{ width: '24px', height: '24px', flexShrink: 0 }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    ),
    warning: (
      <svg style={{ width: '24px', height: '24px', flexShrink: 0 }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
      </svg>
    ),
    info: (
      <svg style={{ width: '24px', height: '24px', flexShrink: 0 }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    ),
  };

  return (
    <div
      style={{
        position: 'fixed',
        top: '20px',
        right: '20px',
        zIndex: 10000,
        maxWidth: '400px',
        ...styles[type],
        color: '#ffffff',
        padding: '16px 20px',
        borderRadius: '8px',
        boxShadow: '0 10px 25px rgba(0, 0, 0, 0.3)',
        display: 'flex',
        alignItems: 'center',
        gap: '12px',
        animation: 'slideInRight 0.3s ease-out',
      }}
    >
      {icons[type]}
      <p style={{ margin: 0, flex: 1, fontSize: '14px', lineHeight: '1.5', fontWeight: '500' }}>
        {message}
      </p>
      <button
        onClick={onClose}
        style={{
          background: 'rgba(255, 255, 255, 0.2)',
          border: 'none',
          color: '#ffffff',
          borderRadius: '4px',
          padding: '4px 8px',
          cursor: 'pointer',
          fontSize: '18px',
          fontWeight: 'bold',
          transition: 'background 0.2s',
        }}
        onMouseEnter={(e) => (e.target.style.background = 'rgba(255, 255, 255, 0.3)')}
        onMouseLeave={(e) => (e.target.style.background = 'rgba(255, 255, 255, 0.2)')}
      >
        ×
      </button>
      <style>
        {`
          @keyframes slideInRight {
            from {
              transform: translateX(100%);
              opacity: 0;
            }
            to {
              transform: translateX(0);
              opacity: 1;
            }
          }
        `}
      </style>
    </div>
  );
}

export default Notification;
