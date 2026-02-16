import React, { useState, useEffect } from 'react';
import { getDashboardMetrics } from '../services/api';

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
      <div className="loading-spinner"></div>
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

          <div className="text-center mt-2" style={{color: '#64748b', fontSize: '0.875rem'}}>
            Last updated: {new Date(metrics.last_updated).toLocaleString()}
          </div>
        </>
      )}
    </div>
  );
}

export default Dashboard;
