import React from 'react';

function LoadingScreen({ message = 'Loading...', fullScreen = false }) {
  const containerStyle = fullScreen ? {
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    background: 'linear-gradient(135deg, #0284c7 0%, #0891b2 100%)',
    zIndex: 9999,
  } : {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    padding: '4rem 2rem',
  };

  return (
    <div style={containerStyle}>
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        animation: 'fadeInScale 0.5s ease-out',
      }}>
        {/* App Logo with Animation */}
        <div style={{
          position: 'relative',
          marginBottom: '2rem',
        }}>
          <svg 
            style={{
              width: '100px',
              height: '100px',
              animation: 'pulse 2s ease-in-out infinite',
              filter: 'drop-shadow(0 10px 30px rgba(0, 0, 0, 0.3))',
            }}
            viewBox="0 0 24 24" 
            fill={fullScreen ? '#ffffff' : '#0284c7'}
          >
            <path d="M12 14l9-5-9-5-9 5 9 5z"/>
            <path d="M12 14l6.16-3.422a12.083 12.083 0 01.665 6.479A11.952 11.952 0 0012 20.055a11.952 11.952 0 00-6.824-2.998 12.078 12.078 0 01.665-6.479L12 14z"/>
            <path d="M12 14l9-5-9-5-9 5 9 5zm0 0l6.16-3.422a12.083 12.083 0 01.665 6.479A11.952 11.952 0 0012 20.055a11.952 11.952 0 00-6.824-2.998 12.078 12.078 0 01.665-6.479L12 14zm-4 6v-7.5l4-2.222"/>
          </svg>
          
          {/* Animated Ring Around Logo */}
          <div style={{
            position: 'absolute',
            top: '-10px',
            left: '-10px',
            right: '-10px',
            bottom: '-10px',
            border: `3px solid ${fullScreen ? 'rgba(255, 255, 255, 0.3)' : 'rgba(2, 132, 199, 0.3)'}`,
            borderRadius: '50%',
            borderTopColor: fullScreen ? '#ffffff' : '#0284c7',
            animation: 'spin 1.5s linear infinite',
          }}></div>
        </div>

        {/* Brand Name */}
        <h2 style={{
          fontSize: '1.75rem',
          fontWeight: '700',
          color: fullScreen ? '#ffffff' : '#0f172a',
          marginBottom: '0.5rem',
          letterSpacing: '-0.5px',
          textAlign: 'center',
          textShadow: fullScreen ? '0 2px 10px rgba(0, 0, 0, 0.2)' : 'none',
        }}>
          Call Intelligence Platform
        </h2>

        {/* Loading Message */}
        <p style={{
          fontSize: '1rem',
          color: fullScreen ? 'rgba(255, 255, 255, 0.9)' : '#64748b',
          marginBottom: '2rem',
          textAlign: 'center',
          fontWeight: '500',
        }}>
          {message}
        </p>

        {/* Progress Dots */}
        <div style={{
          display: 'flex',
          gap: '0.5rem',
          alignItems: 'center',
        }}>
          <div style={{
            width: '10px',
            height: '10px',
            borderRadius: '50%',
            backgroundColor: fullScreen ? '#ffffff' : '#0284c7',
            animation: 'bounce 1.4s ease-in-out 0s infinite',
          }}></div>
          <div style={{
            width: '10px',
            height: '10px',
            borderRadius: '50%',
            backgroundColor: fullScreen ? '#ffffff' : '#0284c7',
            animation: 'bounce 1.4s ease-in-out 0.2s infinite',
          }}></div>
          <div style={{
            width: '10px',
            height: '10px',
            borderRadius: '50%',
            backgroundColor: fullScreen ? '#ffffff' : '#0284c7',
            animation: 'bounce 1.4s ease-in-out 0.4s infinite',
          }}></div>
        </div>
      </div>
    </div>
  );
}

export default LoadingScreen;
