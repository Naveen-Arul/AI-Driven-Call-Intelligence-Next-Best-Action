import React, { useState, useEffect } from 'react';
import { getDashboardMetrics } from '../services/api';
import LoadingScreen from './LoadingScreen';

function Dashboard() {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadDashboardData();
    // Refresh every 30 seconds
    const interval = setInterval(loadDashboardData, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const metricsRes = await getDashboardMetrics();
      setMetrics(metricsRes.data);
    } catch (err) {
      setError('Failed to load dashboard data. Please ensure the backend is running.');
      console.error('Dashboard error:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading && !metrics) {
    return (
      <LoadingScreen message="Loading dashboard metrics..." />
    );
  }

  if (error) {
    return (
      <div className="alert alert-error">
        <strong>Error:</strong> {error}
      </div>
    );
  }

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">
          <svg className="page-icon" viewBox="0 0 20 20" fill="currentColor">
            <path d="M2 10a8 8 0 018-8v8h8a8 8 0 11-16 0z" />
            <path d="M12 2.252A8.014 8.014 0 0117.748 8H12V2.252z" />
          </svg>
          Dashboard
        </h1>
        <p className="page-subtitle">Real-time analytics and insights</p>
      </div>

      {/* Key Metrics */}
      {metrics && (
        <>
          <div className="stats-grid">
            <div className="stat-card" style={{borderLeftColor: '#3b82f6'}}>
              <div className="stat-label">Total Calls</div>
              <div className="stat-value">{metrics.total_calls}</div>
            </div>

            <div className="stat-card" style={{borderLeftColor: '#ef4444'}}>
              <div className="stat-label">High Risk Calls</div>
              <div className="stat-value">{metrics.high_risk_calls}</div>
            </div>

            <div className="stat-card" style={{borderLeftColor: '#10b981'}}>
              <div className="stat-label">Revenue Opportunities</div>
              <div className="stat-value">{metrics.revenue_opportunities}</div>
            </div>

            <div className="stat-card" style={{borderLeftColor: '#f59e0b'}}>
              <div className="stat-label">Avg Priority Score</div>
              <div className="stat-value">{metrics.avg_priority_score}</div>
            </div>
          </div>

          {/* Sentiment Distribution */}
          <div className="card">
            <h2 className="card-header">
              <svg className="card-icon" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM7 9a1 1 0 100-2 1 1 0 000 2zm7-1a1 1 0 11-2 0 1 1 0 012 0zm-.464 5.535a1 1 0 10-1.415-1.414 3 3 0 01-4.242 0 1 1 0 00-1.415 1.414 5 5 0 007.072 0z" clipRule="evenodd" />
              </svg>
              Sentiment Distribution
            </h2>
            {Object.keys(metrics.sentiment_distribution).length > 0 ? (
              <div className="detail-grid">
                {Object.entries(metrics.sentiment_distribution).map(([sentiment, count]) => (
                  <div key={sentiment} className="detail-item">
                    <div className="detail-label">{sentiment}</div>
                    <div className="detail-value">
                      <span className={`badge ${
                        sentiment === 'positive' ? 'badge-success' :
                        sentiment === 'negative' ? 'badge-danger' :
                        'badge-secondary'
                      }`}>
                        {count} calls
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="empty-state">
                <svg className="empty-state-icon" viewBox="0 0 20 20" fill="currentColor">
                  <path d="M2 10a8 8 0 018-8v8h8a8 8 0 11-16 0z" />
                  <path d="M12 2.252A8.014 8.014 0 0117.748 8H12V2.252z" />
                </svg>
                <div className="empty-state-title">No sentiment data yet</div>
              </div>
            )}
          </div>

          {/* Status Distribution */}
          <div className="card mt-3">
            <h2 className="card-header">
              <svg className="card-icon" viewBox="0 0 20 20" fill="currentColor">
                <path d="M9 2a1 1 0 000 2h2a1 1 0 100-2H9z" />
                <path fillRule="evenodd" d="M4 5a2 2 0 012-2 3 3 0 003 3h2a3 3 0 003-3 2 2 0 012 2v11a2 2 0 01-2 2H6a2 2 0 01-2-2V5zm3 4a1 1 0 000 2h.01a1 1 0 100-2H7zm3 0a1 1 0 000 2h3a1 1 0 100-2h-3zm-3 4a1 1 0 100 2h.01a1 1 0 100-2H7zm3 0a1 1 0 100 2h3a1 1 0 100-2h-3z" clipRule="evenodd" />
              </svg>
              Status Distribution
            </h2>
            {Object.keys(metrics.status_distribution).length > 0 ? (
              <div className="detail-grid">
                {Object.entries(metrics.status_distribution).map(([status, count]) => (
                  <div key={status} className="detail-item">
                    <div className="detail-label">{status}</div>
                    <div className="detail-value">
                      <span className={`badge ${
                        status === 'approved' ? 'badge-success' :
                        status === 'rejected' ? 'badge-danger' :
                        'badge-warning'
                      }`}>
                        {count} calls
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="empty-state">
                <svg className="empty-state-icon" viewBox="0 0 20 20" fill="currentColor">
                  <path d="M9 2a1 1 0 000 2h2a1 1 0 100-2H9z" />
                  <path fillRule="evenodd" d="M4 5a2 2 0 012-2 3 3 0 003 3h2a3 3 0 003-3 2 2 0 012 2v11a2 2 0 01-2 2H6a2 2 0 01-2-2V5zm9 4a1 1 0 102 0 1 1 0 00-2 0zm-3 1a1 1 0 100 2h3a1 1 0 100-2h-3zm-3 4a1 1 0 100 2h.01a1 1 0 100-2H7zm3 0a1 1 0 100 2h3a1 1 0 100-2h-3z" clipRule="evenodd" />
                </svg>
                <div className="empty-state-title">No status data yet</div>
              </div>
            )}
          </div>

          {/* Language Distribution */}
          {metrics.language_statistics && metrics.language_statistics.length > 0 && (
            <div className="card mt-3">
              <h2 className="card-header">
                <svg className="card-icon" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M7 2a1 1 0 011 1v1h3a1 1 0 110 2H9.578a18.87 18.87 0 01-1.724 4.78c.29.354.596.696.914 1.026a1 1 0 11-1.44 1.389c-.188-.196-.373-.396-.554-.6a19.098 19.098 0 01-3.107 3.567 1 1 0 01-1.334-1.49 17.087 17.087 0 003.13-3.733 18.992 18.992 0 01-1.487-2.494 1 1 0 111.79-.89c.234.47.489.928.764 1.372.417-.934.752-1.913.997-2.927H3a1 1 0 110-2h3V3a1 1 0 011-1zm6 6a1 1 0 01.894.553l2.991 5.982a.869.869 0 01.02.037l.99 1.98a1 1 0 11-1.79.895L15.383 16h-4.764l-.724 1.447a1 1 0 11-1.788-.894l.99-1.98.019-.038 2.99-5.982A1 1 0 0113 8zm-1.382 6h2.764L13 11.236 11.618 14z" clipRule="evenodd" />
                </svg>
                Language Distribution
              </h2>
              <div className="detail-grid">
                {metrics.language_statistics.map((lang, index) => (
                  <div key={index} className="detail-item">
                    <div className="detail-label">
                      <span style={{ marginRight: '8px' }}>
                        {lang.language_name === 'English' ? '🇺🇸' : 
                         lang.language_name === 'Tamil' ? '🟠' : 
                         lang.language_name === 'Hindi' ? '🇮🇳' : 
                         lang.language_name === 'Spanish' ? '🇪🇸' : 
                         lang.language_name === 'French' ? '🇫🇷' : 
                         '🌐'}
                      </span>
                      {lang.language_name || lang.language_code}
                    </div>
                    <div className="detail-value">
                      <span className={`badge ${
                        lang.language_name === 'English' ? 'badge-info' : 
                        lang.language_name === 'Tamil' ? 'badge-warning' : 
                        'badge-secondary'
                      }`}>
                        {lang.count} calls
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="text-center mt-2" style={{color: '#64748b', fontSize: '0.875rem'}}>
            Last updated: {new Date(metrics.last_updated).toLocaleString('en-IN', {
              timeZone: 'Asia/Kolkata',
              year: 'numeric',
              month: '2-digit',
              day: '2-digit',
              hour: '2-digit',
              minute: '2-digit',
              second: '2-digit',
              hour12: false
            })} IST
          </div>
        </>
      )}
    </div>
  );
}

export default Dashboard;
