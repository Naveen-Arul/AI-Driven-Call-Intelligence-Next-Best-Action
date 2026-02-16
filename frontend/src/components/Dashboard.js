import React, { useState, useEffect } from 'react';
import { getDashboardMetrics, getHealthCheck } from '../services/api';

function Dashboard() {
  const [metrics, setMetrics] = useState(null);
  const [health, setHealth] = useState(null);
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
      
      const [metricsRes, healthRes] = await Promise.all([
        getDashboardMetrics(),
        getHealthCheck()
      ]);
      
      setMetrics(metricsRes.data);
      setHealth(healthRes.data);
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
        <h1 className="page-title">📊 Dashboard</h1>
        <p className="page-subtitle">Real-time analytics and system health</p>
      </div>

      {/* Service Health */}
      {health && (
        <div className="card mb-3">
          <h2 className="card-header">System Health</h2>
          <div className="detail-grid">
            <div className="detail-item">
              <div className="detail-label">Status</div>
              <div className="detail-value">
                <span className="badge badge-success">
                  {health.status.toUpperCase()}
                </span>
              </div>
            </div>
            <div className="detail-item">
              <div className="detail-label">Version</div>
              <div className="detail-value">{health.version}</div>
            </div>
            <div className="detail-item">
              <div className="detail-label">Database</div>
              <div className="detail-value">
                <span className={`badge ${health.services.database_service === 'ready' ? 'badge-success' : 'badge-warning'}`}>
                  {health.services.database_service}
                </span>
              </div>
            </div>
            <div className="detail-item">
              <div className="detail-label">RAG Service</div>
              <div className="detail-value">
                <span className={`badge ${health.services.rag_service === 'ready' ? 'badge-success' : 'badge-secondary'}`}>
                  {health.services.rag_service}
                </span>
              </div>
            </div>
          </div>
        </div>
      )}

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
            <h2 className="card-header">Sentiment Distribution</h2>
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
                <div className="empty-state-icon">📊</div>
                <div className="empty-state-title">No sentiment data yet</div>
              </div>
            )}
          </div>

          {/* Status Distribution */}
          <div className="card mt-3">
            <h2 className="card-header">Status Distribution</h2>
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
                <div className="empty-state-icon">📋</div>
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
