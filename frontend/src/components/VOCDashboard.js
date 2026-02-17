import React, { useState, useEffect } from 'react';
import { getVOCInsights } from '../services/api';
import LoadingScreen from './LoadingScreen';

function VOCDashboard() {
  const [insights, setInsights] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [daysFilter, setDaysFilter] = useState(30);

  useEffect(() => {
    loadInsights();
  }, [daysFilter]);

  const loadInsights = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await getVOCInsights(daysFilter);
      setInsights(response.data);
    } catch (err) {
      setError('Failed to load VOC insights. Please ensure calls have been processed.');
      console.error('VOC insights error:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading && !insights) {
    return <LoadingScreen message="Analyzing Voice of Customer insights..." />;
  }

  if (error) {
    return (
      <div>
        <div className="page-header">
          <h1 className="page-title">
            <svg className="page-icon" viewBox="0 0 20 20" fill="currentColor">
              <path d="M10 12a2 2 0 100-4 2 2 0 000 4z" />
              <path fillRule="evenodd" d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clipRule="evenodd" />
            </svg>
            Voice of Customer Insights
          </h1>
          <p className="page-subtitle">Strategic business intelligence from customer calls</p>
        </div>
        <div className="alert alert-error">
          <strong>Error:</strong> {error}
        </div>
      </div>
    );
  }

  const totalCalls = insights?.total_calls_analyzed || 0;

  return (
    <div>
      <div className="page-header">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', width: '100%' }}>
          <div>
            <h1 className="page-title">
              <svg className="page-icon" viewBox="0 0 20 20" fill="currentColor">
                <path d="M10 12a2 2 0 100-4 2 2 0 000 4z" />
                <path fillRule="evenodd" d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clipRule="evenodd" />
              </svg>
              Voice of Customer Insights
            </h1>
            <p className="page-subtitle">
              Analyzing {totalCalls} calls from the last {daysFilter} days
            </p>
          </div>
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <button 
              className={`btn ${daysFilter === 7 ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setDaysFilter(7)}
              style={{ padding: '0.5rem 1rem' }}
            >
              7 Days
            </button>
            <button 
              className={`btn ${daysFilter === 30 ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setDaysFilter(30)}
              style={{ padding: '0.5rem 1rem' }}
            >
              30 Days
            </button>
            <button 
              className={`btn ${daysFilter === 90 ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setDaysFilter(90)}
              style={{ padding: '0.5rem 1rem' }}
            >
              90 Days
            </button>
          </div>
        </div>
      </div>

      {totalCalls === 0 ? (
        <div className="card">
          <div className="empty-state">
            <svg className="empty-state-icon" viewBox="0 0 20 20" fill="currentColor">
              <path d="M2 3a1 1 0 011-1h2.153a1 1 0 01.986.836l.74 4.435a1 1 0 01-.54 1.06l-1.548.773a11.037 11.037 0 006.105 6.105l.774-1.548a1 1 0 011.059-.54l4.435.74a1 1 0 01.836.986V17a1 1 0 01-1 1h-2C7.82 18 2 12.18 2 5V3z" />
            </svg>
            <div className="empty-state-title">No calls to analyze yet</div>
            <div className="empty-state-subtitle">Process some calls to see Voice of Customer insights</div>
          </div>
        </div>
      ) : (
        <>
          {/* Product Feedback Overview */}
          <div className="card">
            <h2 className="card-header">
              <svg className="card-icon" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
              </svg>
              Overall Customer Sentiment
            </h2>
            <div className="stats-grid">
              <div className="stat-card" style={{ borderLeftColor: '#10b981' }}>
                <div className="stat-label">Positive Calls</div>
                <div className="stat-value">{insights?.product_feedback?.positive || 0}</div>
                <div style={{ fontSize: '0.875rem', color: '#6b7280', marginTop: '0.25rem' }}>
                  {totalCalls > 0 ? Math.round((insights?.product_feedback?.positive / totalCalls) * 100) : 0}%
                </div>
              </div>
              <div className="stat-card" style={{ borderLeftColor: '#94a3b8' }}>
                <div className="stat-label">Neutral Calls</div>
                <div className="stat-value">{insights?.product_feedback?.neutral || 0}</div>
                <div style={{ fontSize: '0.875rem', color: '#6b7280', marginTop: '0.25rem' }}>
                  {totalCalls > 0 ? Math.round((insights?.product_feedback?.neutral / totalCalls) * 100) : 0}%
                </div>
              </div>
              <div className="stat-card" style={{ borderLeftColor: '#ef4444' }}>
                <div className="stat-label">Negative Calls</div>
                <div className="stat-value">{insights?.product_feedback?.negative || 0}</div>
                <div style={{ fontSize: '0.875rem', color: '#6b7280', marginTop: '0.25rem' }}>
                  {totalCalls > 0 ? Math.round((insights?.product_feedback?.negative / totalCalls) * 100) : 0}%
                </div>
              </div>
            </div>
          </div>

          {/* Top Topics Mentioned */}
          <div className="card mt-3">
            <h2 className="card-header">
              <svg className="card-icon" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M7 2a1 1 0 00-.707 1.707L7 4.414v3.758a1 1 0 01-.293.707l-4 4C.817 14.769 2.156 18 4.828 18h10.343c2.673 0 4.012-3.231 2.122-5.121l-4-4A1 1 0 0113 8.172V4.414l.707-.707A1 1 0 0013 2H7zm2 6.172V4h2v4.172a3 3 0 00.879 2.12l1.027 1.028a4 4 0 00-2.171.102l-.47.156a4 4 0 01-2.53 0l-.563-.187a1.993 1.993 0 00-.114-.035l1.063-1.063A3 3 0 009 8.172z" clipRule="evenodd" />
              </svg>
              Most Mentioned Topics (Last {daysFilter} Days)
            </h2>
            {insights?.top_topics && insights.top_topics.length > 0 ? (
              <div style={{ padding: '0' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                  <thead>
                    <tr style={{ borderBottom: '2px solid #e5e7eb' }}>
                      <th style={{ padding: '1rem', textAlign: 'left', fontWeight: '600', color: '#1f2937' }}>#</th>
                      <th style={{ padding: '1rem', textAlign: 'left', fontWeight: '600', color: '#1f2937' }}>Topic</th>
                      <th style={{ padding: '1rem', textAlign: 'left', fontWeight: '600', color: '#1f2937' }}>Mentions</th>
                      <th style={{ padding: '1rem', textAlign: 'left', fontWeight: '600', color: '#1f2937' }}>% of Calls</th>
                    </tr>
                  </thead>
                  <tbody>
                    {insights.top_topics.map((topic, index) => (
                      <tr key={index} style={{ borderBottom: '1px solid #e5e7eb' }}>
                        <td style={{ padding: '1rem' }}>{index + 1}</td>
                        <td style={{ padding: '1rem' }}>
                          <span className="badge badge-info">{topic.topic}</span>
                        </td>
                        <td style={{ padding: '1rem', fontWeight: '600', color: '#1f2937' }}>{topic.mentions}</td>
                        <td style={{ padding: '1rem' }}>
                          <span className="badge badge-secondary">{topic.percentage}%</span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div style={{ padding: '2rem', textAlign: 'center', color: '#6b7280' }}>
                No topics detected yet
              </div>
            )}
          </div>

          {/* Feature Requests */}
          {insights?.feature_requests && insights.feature_requests.length > 0 && (
            <div className="card mt-3">
              <h2 className="card-header">
                <svg className="card-icon" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M11.3 1.046A1 1 0 0112 2v5h4a1 1 0 01.82 1.573l-7 10A1 1 0 018 18v-5H4a1 1 0 01-.82-1.573l7-10a1 1 0 011.12-.38z" clipRule="evenodd" />
                </svg>
                Top Feature Requests
              </h2>
              <div style={{ padding: '1rem' }}>
                {insights.feature_requests.map((request, index) => (
                  <div 
                    key={index}
                    style={{ 
                      display: 'flex', 
                      justifyContent: 'space-between', 
                      alignItems: 'center',
                      padding: '0.75rem',
                      marginBottom: '0.5rem',
                      background: '#f8fafc',
                      borderRadius: '6px',
                      border: '1px solid #e5e7eb'
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                      <span style={{ 
                        fontSize: '1.25rem', 
                        fontWeight: '700', 
                        color: '#6b7280',
                        minWidth: '30px'
                      }}>
                        {index + 1}
                      </span>
                      <span style={{ fontSize: '0.95rem', color: '#1f2937' }}>
                        "{request.request}"
                      </span>
                    </div>
                    <span className="badge badge-warning" style={{ fontSize: '0.875rem', padding: '0.375rem 0.75rem' }}>
                      {request.count} requests
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Competitor Analysis */}
          {insights?.competitor_mentions && insights.competitor_mentions.length > 0 && (
            <div className="card mt-3">
              <h2 className="card-header">
                <svg className="card-icon" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M3 6a3 3 0 013-3h10a1 1 0 01.8 1.6L14.25 8l2.55 3.4A1 1 0 0116 13H6a1 1 0 00-1 1v3a1 1 0 11-2 0V6z" clipRule="evenodd" />
                </svg>
                Competitor Mentions
              </h2>
              <div className="detail-grid">
                {insights.competitor_mentions.map((comp, index) => (
                  <div key={index} className="detail-item">
                    <div className="detail-label">{comp.competitor}</div>
                    <div className="detail-value">
                      <span className="badge badge-danger">{comp.mentions} mentions</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Common Pain Points */}
          {insights?.common_pain_points && insights.common_pain_points.length > 0 && (
            <div className="card mt-3">
              <h2 className="card-header">
                <svg className="card-icon" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
                Common Pain Points ⚠️
              </h2>
              <div style={{ padding: '1rem' }}>
                {insights.common_pain_points.map((pain, index) => (
                  <div 
                    key={index}
                    style={{ 
                      padding: '0.875rem',
                      marginBottom: '0.5rem',
                      background: '#fef2f2',
                      border: '1px solid #fecaca',
                      borderRadius: '6px',
                      color: '#991b1b',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.5rem'
                    }}
                  >
                    <svg style={{ width: '20px', height: '20px', flexShrink: 0 }} viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                    </svg>
                    <span style={{ fontSize: '0.95rem', fontWeight: '500' }}>{pain}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Word Cloud Data */}
          {insights?.word_cloud && Object.keys(insights.word_cloud).length > 0 && (
            <div className="card mt-3">
              <h2 className="card-header">
                <svg className="card-icon" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M4 4a2 2 0 012-2h8a2 2 0 012 2v12a1 1 0 110 2h-3a1 1 0 01-1-1v-2a1 1 0 00-1-1H9a1 1 0 00-1 1v2a1 1 0 01-1 1H4a1 1 0 110-2V4zm3 1h2v2H7V5zm2 4H7v2h2V9zm2-4h2v2h-2V5zm2 4h-2v2h2V9z" clipRule="evenodd" />
                </svg>
                Most Frequently Used Words
              </h2>
              <div style={{ padding: '1.5rem', display: 'flex', flexWrap: 'wrap', gap: '0.75rem', justifyContent: 'center' }}>
                {Object.entries(insights.word_cloud)
                  .slice(0, 30)
                  .map(([word, count], index) => {
                    const maxCount = Math.max(...Object.values(insights.word_cloud));
                    const fontSize = 0.75 + (count / maxCount) * 1.5;
                    const opacity = 0.5 + (count / maxCount) * 0.5;
                    
                    return (
                      <span
                        key={index}
                        style={{
                          fontSize: `${fontSize}rem`,
                          fontWeight: '600',
                          color: '#0284c7',
                          opacity: opacity,
                          padding: '0.25rem 0.5rem',
                          background: '#f0f9ff',
                          borderRadius: '4px',
                          whiteSpace: 'nowrap'
                        }}
                        title={`Mentioned ${count} times`}
                      >
                        {word}
                      </span>
                    );
                  })}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}

export default VOCDashboard;
