import React, { useState, useEffect, useCallback } from 'react';
import { getCalls, searchCalls } from '../services/api';
import { useNavigate } from 'react-router-dom';
import LoadingScreen from './LoadingScreen';

function CallsList() {
  const [calls, setCalls] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [statusFilter, setStatusFilter] = useState('');
  const [showAdvancedSearch, setShowAdvancedSearch] = useState(false);
  const [searchFilters, setSearchFilters] = useState({
    query: '',
    sentiment: '',
    minPriority: '',
    maxPriority: '',
    riskLevel: '',
    startDate: '',
    endDate: ''
  });
  const navigate = useNavigate();

  const loadCalls = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Check if advanced search filters are active
      const hasAdvancedFilters = searchFilters.query || searchFilters.sentiment || 
        searchFilters.minPriority || searchFilters.maxPriority || 
        searchFilters.riskLevel || searchFilters.startDate || searchFilters.endDate;
      
      if (hasAdvancedFilters) {
        // Use search API
        const filters = {};
        if (searchFilters.query) filters.query = searchFilters.query;
        if (searchFilters.sentiment) filters.sentiment = searchFilters.sentiment;
        if (searchFilters.minPriority) filters.min_priority = parseInt(searchFilters.minPriority);
        if (searchFilters.maxPriority) filters.max_priority = parseInt(searchFilters.maxPriority);
        if (searchFilters.riskLevel) filters.risk_level = searchFilters.riskLevel;
        if (searchFilters.startDate) filters.start_date = searchFilters.startDate;
        if (searchFilters.endDate) filters.end_date = searchFilters.endDate;
        if (statusFilter) filters.status = statusFilter;
        
        const response = await searchCalls(filters);
        // Sort by created_at descending (newest first)
        const sortedCalls = response.data.calls.sort((a, b) => 
          new Date(b.created_at) - new Date(a.created_at)
        );
        setCalls(sortedCalls);
      } else {
        // Use regular getCalls API
        const params = statusFilter ? { status: statusFilter } : {};
        const response = await getCalls(params);
        // Sort by created_at descending (newest first)
        const sortedCalls = response.data.calls.sort((a, b) => 
          new Date(b.created_at) - new Date(a.created_at)
        );
        setCalls(sortedCalls);
      }
    } catch (err) {
      setError('Failed to load calls. Please ensure the backend is running.');
      console.error('Load calls error:', err);
    } finally {
      setLoading(false);
    }
  }, [statusFilter, searchFilters]);

  const handleSearchFilterChange = (field, value) => {
    setSearchFilters(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const clearSearchFilters = () => {
    setSearchFilters({
      query: '',
      sentiment: '',
      minPriority: '',
      maxPriority: '',
      riskLevel: '',
      startDate: '',
      endDate: ''
    });
  };

  useEffect(() => {
    loadCalls();
  }, [loadCalls]);

  const formatDate = (dateString) => {
    // Convert to Indian Standard Time (IST)
    const date = new Date(dateString);
    return date.toLocaleString('en-IN', {
      timeZone: 'Asia/Kolkata',
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: false
    });
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
        <h1 className="page-title">
          <svg className="page-icon" viewBox="0 0 20 20" fill="currentColor">
            <path d="M9 2a1 1 0 000 2h2a1 1 0 100-2H9z" />
            <path fillRule="evenodd" d="M4 5a2 2 0 012-2 3 3 0 003 3h2a3 3 0 003-3 2 2 0 012 2v11a2 2 0 01-2 2H6a2 2 0 01-2-2V5zm3 4a1 1 0 000 2h.01a1 1 0 100-2H7zm3 0a1 1 0 000 2h3a1 1 0 100-2h-3zm-3 4a1 1 0 100 2h.01a1 1 0 100-2H7zm3 0a1 1 0 100 2h3a1 1 0 100-2h-3z" clipRule="evenodd" />
          </svg>
          Calls Management
        </h1>
        <p className="page-subtitle">View and manage all processed calls</p>
      </div>

      {error && (
        <div className="alert alert-error">
          <strong>Error:</strong> {error}
        </div>
      )}

      {/* Filters */}
      <div className="card mb-3">
        <div className="flex items-center justify-between" style={{ marginBottom: '1rem' }}>
          <h2 className="card-header" style={{marginBottom: 0, paddingBottom: 0, border: 'none'}}>
            Status Filters
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

        {/* Advanced Search Toggle */}
        <div style={{ borderTop: '1px solid #e2e8f0', paddingTop: '1rem' }}>
          <button
            className="btn btn-secondary"
            onClick={() => setShowAdvancedSearch(!showAdvancedSearch)}
            style={{ width: '100%', display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '0.5rem' }}
          >
            {showAdvancedSearch ? '▼' : '▶'} Advanced Search & Filters
          </button>
        </div>

        {/* Advanced Search Panel */}
        {showAdvancedSearch && (
          <div style={{ borderTop: '1px solid #e2e8f0', paddingTop: '1rem', marginTop: '1rem' }}>
            <div className="form-group" style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '1rem' }}>
              {/* Text Search */}
              <div style={{ gridColumn: '1 / -1' }}>
                <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '600' }}>
                  🔍 Search Text
                </label>
                <input
                  type="text"
                  className="form-control"
                  placeholder="Search in transcript..."
                  value={searchFilters.query}
                  onChange={(e) => handleSearchFilterChange('query', e.target.value)}
                />
              </div>

              {/* Sentiment Filter */}
              <div>
                <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '600' }}>
                  😊 Sentiment
                </label>
                <select
                  className="form-control"
                  value={searchFilters.sentiment}
                  onChange={(e) => handleSearchFilterChange('sentiment', e.target.value)}
                >
                  <option value="">All Sentiments</option>
                  <option value="positive">Positive</option>
                  <option value="neutral">Neutral</option>
                  <option value="negative">Negative</option>
                </select>
              </div>

              {/* Risk Level Filter */}
              <div>
                <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '600' }}>
                  ⚠️ Risk Level
                </label>
                <select
                  className="form-control"
                  value={searchFilters.riskLevel}
                  onChange={(e) => handleSearchFilterChange('riskLevel', e.target.value)}
                >
                  <option value="">All Risk Levels</option>
                  <option value="high">High</option>
                  <option value="medium">Medium</option>
                  <option value="low">Low</option>
                </select>
              </div>

              {/* Priority Range */}
              <div>
                <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '600' }}>
                  📊 Min Priority
                </label>
                <input
                  type="number"
                  className="form-control"
                  placeholder="0"
                  min="0"
                  max="100"
                  value={searchFilters.minPriority}
                  onChange={(e) => handleSearchFilterChange('minPriority', e.target.value)}
                />
              </div>

              <div>
                <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '600' }}>
                  📊 Max Priority
                </label>
                <input
                  type="number"
                  className="form-control"
                  placeholder="100"
                  min="0"
                  max="100"
                  value={searchFilters.maxPriority}
                  onChange={(e) => handleSearchFilterChange('maxPriority', e.target.value)}
                />
              </div>

              {/* Date Range */}
              <div>
                <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '600' }}>
                  📅 Start Date
                </label>
                <input
                  type="date"
                  className="form-control"
                  value={searchFilters.startDate}
                  onChange={(e) => handleSearchFilterChange('startDate', e.target.value)}
                />
              </div>

              <div>
                <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '600' }}>
                  📅 End Date
                </label>
                <input
                  type="date"
                  className="form-control"
                  value={searchFilters.endDate}
                  onChange={(e) => handleSearchFilterChange('endDate', e.target.value)}
                />
              </div>
            </div>

            {/* Search Actions */}
            <div className="flex gap-2" style={{ marginTop: '1rem' }}>
              <button className="btn btn-primary" onClick={loadCalls}>
                🔍 Apply Filters
              </button>
              <button className="btn btn-secondary" onClick={clearSearchFilters}>
                ✖ Clear Filters
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Calls Table */}
      <div className="card">
        <div className="flex items-center justify-between mb-3">
          <h2 className="card-header" style={{marginBottom: 0, paddingBottom: 0, border: 'none'}}>
            Calls ({calls.length})
          </h2>
          <button className="btn btn-secondary" onClick={loadCalls}>
            <svg style={{width: '18px', height: '18px'}} viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clipRule="evenodd" />
            </svg>
            Refresh
          </button>
        </div>

        {loading ? (
          <LoadingScreen message="Loading calls..." />
        ) : calls.length === 0 ? (
          <div className="empty-state">
              <svg className="empty-state-icon" viewBox="0 0 20 20" fill="currentColor">
                <path d="M2 3a1 1 0 011-1h2.153a1 1 0 01.986.836l.74 4.435a1 1 0 01-.54 1.06l-1.548.773a11.037 11.037 0 006.105 6.105l.774-1.548a1 1 0 011.059-.54l4.435.74a1 1 0 01.836.986V17a1 1 0 01-1 1h-2C7.82 18 2 12.18 2 5V3z" />
              </svg>
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
