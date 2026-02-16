import React, { useState, useEffect, useCallback } from 'react';
import { getCalls } from '../services/api';
import { useNavigate } from 'react-router-dom';

function CallsList() {
  const [calls, setCalls] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [statusFilter, setStatusFilter] = useState('');
  const navigate = useNavigate();

  const loadCalls = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const params = statusFilter ? { status: statusFilter } : {};
      const response = await getCalls(params);
      setCalls(response.data.calls);
    } catch (err) {
      setError('Failed to load calls. Please ensure the backend is running.');
      console.error('Load calls error:', err);
    } finally {
      setLoading(false);
    }
  }, [statusFilter]);

  useEffect(() => {
    loadCalls();
  }, [loadCalls]);

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  const getPriorityBadge = (score) => {
    if (score >= 80) return 'badge-danger';
    if (score >= 60) return 'badge-warning';
    return 'badge-info';
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'approved': return 'badge-success';
      case 'rejected': return 'badge-danger';
      default: return 'badge-warning';
    }
  };

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">📋 Calls Management</h1>
        <p className="page-subtitle">View and manage all processed calls</p>
      </div>

      {error && (
        <div className="alert alert-error">
          <strong>Error:</strong> {error}
        </div>
      )}

      {/* Filters */}
      <div className="card mb-3">
        <div className="flex items-center justify-between">
          <h2 className="card-header" style={{marginBottom: 0, paddingBottom: 0, border: 'none'}}>
            Filters
          </h2>
          <div className="flex gap-2">
            <button
              className={`btn ${statusFilter === '' ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setStatusFilter('')}
            >
              All
            </button>
            <button
              className={`btn ${statusFilter === 'pending' ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setStatusFilter('pending')}
            >
              Pending
            </button>
            <button
              className={`btn ${statusFilter === 'approved' ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setStatusFilter('approved')}
            >
              Approved
            </button>
            <button
              className={`btn ${statusFilter === 'rejected' ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setStatusFilter('rejected')}
            >
              Rejected
            </button>
          </div>
        </div>
      </div>

      {/* Calls Table */}
      <div className="card">
        <div className="flex items-center justify-between mb-3">
          <h2 className="card-header" style={{marginBottom: 0, paddingBottom: 0, border: 'none'}}>
            Calls ({calls.length})
          </h2>
          <button className="btn btn-secondary" onClick={loadCalls}>
            🔄 Refresh
          </button>
        </div>

        {loading ? (
          <div className="loading-spinner"></div>
        ) : calls.length === 0 ? (
          <div className="empty-state">
            <div className="empty-state-icon">📞</div>
            <div className="empty-state-title">No calls found</div>
            <p style={{color: '#64748b', marginTop: '0.5rem'}}>
              {statusFilter ? `No ${statusFilter} calls available` : 'Process your first call to get started'}
            </p>
          </div>
        ) : (
          <div className="table-container">
            <table className="table">
              <thead>
                <tr>
                  <th>Call ID</th>
                  <th>Created</th>
                  <th>Priority</th>
                  <th>Risk Level</th>
                  <th>Opportunity</th>
                  <th>Status</th>
                  <th>Intent</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {calls.map((call) => (
                  <tr
                    key={call._id}
                    style={{cursor: 'pointer'}}
                    onClick={() => navigate(`/calls/${call._id}`)}
                  >
                    <td>
                      <code style={{fontSize: '0.875rem', color: '#3b82f6'}}>
                        {call._id.substring(0, 8)}...
                      </code>
                    </td>
                    <td>{formatDate(call.created_at)}</td>
                    <td>
                      <span className={`badge ${getPriorityBadge(call.final_decision.priority_score)}`}>
                        {call.final_decision.priority_score}
                      </span>
                    </td>
                    <td>
                      <span className={`badge ${
                        call.final_decision.risk_level === 'high' ? 'badge-danger' :
                        call.final_decision.risk_level === 'medium' ? 'badge-warning' :
                        'badge-success'
                      }`}>
                        {call.final_decision.risk_level}
                      </span>
                    </td>
                    <td>
                      <span className={`badge ${
                        call.final_decision.opportunity_level === 'high' ? 'badge-success' :
                        call.final_decision.opportunity_level === 'medium' ? 'badge-info' :
                        'badge-secondary'
                      }`}>
                        {call.final_decision.opportunity_level}
                      </span>
                    </td>
                    <td>
                      <span className={`badge ${getStatusBadge(call.status)}`}>
                        {call.status}
                      </span>
                    </td>
                    <td>
                      <span className="badge badge-info">
                        {call.nlp_analysis.intent}
                      </span>
                    </td>
                    <td>
                      <button
                        className="btn btn-primary"
                        style={{padding: '0.375rem 0.75rem', fontSize: '0.875rem'}}
                        onClick={(e) => {
                          e.stopPropagation();
                          navigate(`/calls/${call._id}`);
                        }}
                      >
                        View Details
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

export default CallsList;
