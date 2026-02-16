import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getCallById, approveAction, rejectAction } from '../services/api';

function CallDetail() {
  const { callId } = useParams();
  const navigate = useNavigate();
  const [call, setCall] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [actionLoading, setActionLoading] = useState(false);
  const [notes, setNotes] = useState('');

  const loadCallDetails = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await getCallById(callId);
      setCall(response.data);
    } catch (err) {
      setError('Failed to load call details.');
      console.error('Load call details error:', err);
    } finally {
      setLoading(false);
    }
  }, [callId]);

  useEffect(() => {
    loadCallDetails();
  }, [loadCallDetails]);

  const handleApprove = async () => {
    if (!window.confirm('Are you sure you want to approve this action?')) {
      return;
    }

    setActionLoading(true);
    try {
      await approveAction(callId, notes || null);
      await loadCallDetails();
      setNotes('');
    } catch (err) {
      alert('Failed to approve action: ' + (err.response?.data?.detail || err.message));
    } finally {
      setActionLoading(false);
    }
  };

  const handleReject = async () => {
    if (!window.confirm('Are you sure you want to reject this action?')) {
      return;
    }

    setActionLoading(true);
    try {
      await rejectAction(callId, notes || null);
      await loadCallDetails();
      setNotes('');
    } catch (err) {
      alert('Failed to reject action: ' + (err.response?.data?.detail || err.message));
    } finally {
      setActionLoading(false);
    }
  };

  if (loading) {
    return <div className="loading-spinner"></div>;
  }

  if (error || !call) {
    return (
      <div>
        <div className="alert alert-error">
          <strong>Error:</strong> {error || 'Call not found'}
        </div>
        <button className="btn btn-secondary" onClick={() => navigate('/calls')}>
          ← Back to Calls
        </button>
      </div>
    );
  }

  return (
    <div>
      <div className="page-header">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="page-title">
              <svg className="page-icon" viewBox="0 0 20 20" fill="currentColor">
                <path d="M2 3a1 1 0 011-1h2.153a1 1 0 01.986.836l.74 4.435a1 1 0 01-.54 1.06l-1.548.773a11.037 11.037 0 006.105 6.105l.774-1.548a1 1 0 011.059-.54l4.435.74a1 1 0 01.836.986V17a1 1 0 01-1 1h-2C7.82 18 2 12.18 2 5V3z" />
              </svg>
              Call Details
            </h1>
            <p className="page-subtitle">ID: {call._id}</p>
          </div>
          <button className="btn btn-secondary" onClick={() => navigate('/calls')}>
            ← Back to Calls
          </button>
        </div>
      </div>

      {/* Status and Actions */}
      <div className="card">
        <h2 className="card-header">Status & Actions</h2>
        <div className="detail-grid">
          <div className="detail-item">
            <div className="detail-label">Current Status</div>
            <div className="detail-value">
              <span className={`badge ${
                call.status === 'approved' ? 'badge-success' :
                call.status === 'rejected' ? 'badge-danger' :
                'badge-warning'
              }`}>
                {call.status.toUpperCase()}
              </span>
            </div>
          </div>
          <div className="detail-item">
            <div className="detail-label">Created At</div>
            <div className="detail-value">{new Date(call.created_at).toLocaleString()}</div>
          </div>
          <div className="detail-item">
            <div className="detail-label">Last Updated</div>
            <div className="detail-value">{new Date(call.updated_at).toLocaleString()}</div>
          </div>
          {call.audio_filename && (
            <div className="detail-item">
              <div className="detail-label">Audio File</div>
              <div className="detail-value">{call.audio_filename}</div>
            </div>
          )}
        </div>

        {call.status === 'pending' && (
          <div className="mt-3">
            <div className="form-group">
              <label className="form-label">Approval Notes (Optional)</label>
              <textarea
                className="form-textarea"
                placeholder="Add notes about your decision..."
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
              />
            </div>
            <div className="flex gap-2">
              <button
                className="btn btn-success"
                onClick={handleApprove}
                disabled={actionLoading}
              >
                Approve Action
              </button>
              <button
                className="btn btn-danger"
                onClick={handleReject}
                disabled={actionLoading}
              >
                Reject Action
              </button>
            </div>
          </div>
        )}

        {call.approval_notes && (
          <div className="mt-3 alert alert-info">
            <strong>Approval Notes:</strong> {call.approval_notes}
          </div>
        )}
      </div>

      {/* Final Decision */}
      <div className="card mt-3">
        <h2 className="card-header">
          <svg className="card-icon" viewBox="0 0 20 20" fill="currentColor">
            <path d="M9 2a1 1 0 000 2h2a1 1 0 100-2H9z" />
            <path fillRule="evenodd" d="M4 5a2 2 0 012-2 3 3 0 003 3h2a3 3 0 003-3 2 2 0 012 2v11a2 2 0 01-2 2H6a2 2 0 01-2-2V5zm3 4a1 1 0 000 2h.01a1 1 0 100-2H7zm3 0a1 1 0 000 2h3a1 1 0 100-2h-3zm-3 4a1 1 0 100 2h.01a1 1 0 100-2H7zm3 0a1 1 0 100 2h3a1 1 0 100-2h-3z" clipRule="evenodd" />
          </svg>
          Final Decision
        </h2>
        <div className="detail-grid">
          <div className="detail-item">
            <div className="detail-label">Recommended Action</div>
            <div className="detail-value">{call.final_decision.final_action}</div>
          </div>
          <div className="detail-item">
            <div className="detail-label">Priority Score</div>
            <div className="detail-value">
              <span className={`badge ${
                call.final_decision.priority_score >= 80 ? 'badge-danger' :
                call.final_decision.priority_score >= 60 ? 'badge-warning' :
                'badge-info'
              }`}>
                {call.final_decision.priority_score}/100
              </span>
            </div>
          </div>
          <div className="detail-item">
            <div className="detail-label">Risk Level</div>
            <div className="detail-value">
              <span className={`badge ${
                call.final_decision.risk_level === 'high' ? 'badge-danger' :
                call.final_decision.risk_level === 'medium' ? 'badge-warning' :
                'badge-success'
              }`}>
                {call.final_decision.risk_level}
              </span>
            </div>
          </div>
          <div className="detail-item">
            <div className="detail-label">Opportunity Level</div>
            <div className="detail-value">
              <span className={`badge ${
                call.final_decision.opportunity_level === 'high' ? 'badge-success' :
                call.final_decision.opportunity_level === 'medium' ? 'badge-info' :
                'badge-secondary'
              }`}>
                {call.final_decision.opportunity_level}
              </span>
            </div>
          </div>
          <div className="detail-item">
            <div className="detail-label">Confidence Score</div>
            <div className="detail-value">{call.final_decision.confidence_score}%</div>
          </div>
          <div className="detail-item">
            <div className="detail-label">Escalation Required</div>
            <div className="detail-value">
              <span className={`badge ${call.final_decision.escalation_required ? 'badge-danger' : 'badge-success'}`}>
                {call.final_decision.escalation_required ? 'Yes' : 'No'}
              </span>
            </div>
          </div>
          <div className="detail-item">
            <div className="detail-label">Revenue Opportunity</div>
            <div className="detail-value">
              <span className={`badge ${call.final_decision.revenue_opportunity ? 'badge-success' : 'badge-secondary'}`}>
                {call.final_decision.revenue_opportunity ? 'Yes' : 'No'}
              </span>
            </div>
          </div>
          <div className="detail-item">
            <div className="detail-label">Urgent Flag</div>
            <div className="detail-value">
              <span className={`badge ${call.final_decision.urgent_flag ? 'badge-danger' : 'badge-secondary'}`}>
                {call.final_decision.urgent_flag ? 'Yes' : 'No'}
              </span>
            </div>
          </div>
        </div>

        <div className="mt-3">
          <div className="detail-item w-full">
            <div className="detail-label">Reasoning</div>
            <div className="detail-value">{call.final_decision.reasoning}</div>
          </div>
        </div>

        {call.final_decision.rules_applied && call.final_decision.rules_applied.length > 0 && (
          <div className="mt-3">
            <div className="detail-label">Business Rules Applied</div>
            <div style={{marginTop: '0.5rem'}}>
              {call.final_decision.rules_applied.map((rule, index) => (
                <span key={index} className="badge badge-info" style={{marginRight: '0.5rem'}}>
                  {rule}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Transcript */}
      <div className="card mt-3">
        <h2 className="card-header">
          <svg className="card-icon" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z" clipRule="evenodd" />
          </svg>
          Transcript
        </h2>
        <div style={{padding: '1rem', background: '#f8fafc', borderRadius: '8px', whiteSpace: 'pre-wrap'}}>
          {call.transcript}
        </div>
      </div>

      {/* NLP Analysis */}
      <div className="card mt-3">
        <h2 className="card-header">
          <svg className="card-icon" viewBox="0 0 20 20" fill="currentColor">
            <path d="M9 4.804A7.968 7.968 0 005.5 4c-1.255 0-2.443.29-3.5.804v10A7.969 7.969 0 015.5 14c1.669 0 3.218.51 4.5 1.385A7.962 7.962 0 0114.5 14c1.255 0 2.443.29 3.5.804v-10A7.968 7.968 0 0014.5 4c-1.255 0-2.443.29-3.5.804V12a1 1 0 11-2 0V4.804z" />
          </svg>
          NLP Analysis
        </h2>
        <div className="detail-grid">
          <div className="detail-item">
            <div className="detail-label">Sentiment</div>
            <div className="detail-value">
              <span className={`badge ${
                call.nlp_analysis.sentiment.sentiment_label === 'positive' ? 'badge-success' :
                call.nlp_analysis.sentiment.sentiment_label === 'negative' ? 'badge-danger' :
                'badge-secondary'
              }`}>
                {call.nlp_analysis.sentiment.sentiment_label}
              </span>
            </div>
          </div>
          <div className="detail-item">
            <div className="detail-label">Compound Score</div>
            <div className="detail-value">{call.nlp_analysis.sentiment.compound.toFixed(3)}</div>
          </div>
          <div className="detail-item">
            <div className="detail-label">Intent</div>
            <div className="detail-value">
              <span className="badge badge-info">{call.nlp_analysis.intent}</span>
            </div>
          </div>
        </div>

        {call.nlp_analysis.keywords && Object.keys(call.nlp_analysis.keywords).length > 0 && (
          <div className="mt-3">
            <div className="detail-label">Detected Keywords</div>
            <div style={{marginTop: '0.5rem'}}>
              {Object.entries(call.nlp_analysis.keywords).map(([category, words]) => (
                words.length > 0 && (
                  <div key={category} style={{marginBottom: '0.5rem'}}>
                    <strong>{category}:</strong>{' '}
                    {words.map((word, i) => (
                      <span key={i} className="badge badge-secondary" style={{marginLeft: '0.25rem'}}>
                        {word}
                      </span>
                    ))}
                  </div>
                )
              ))}
            </div>
          </div>
        )}
      </div>

      {/* LLM Output */}
      <div className="card mt-3">
        <h2 className="card-header">
          <svg className="card-icon" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M6.267 3.455a3.066 3.066 0 001.745-.723 3.066 3.066 0 013.976 0 3.066 3.066 0 001.745.723 3.066 3.066 0 012.812 2.812c.051.643.304 1.254.723 1.745a3.066 3.066 0 010 3.976 3.066 3.066 0 00-.723 1.745 3.066 3.066 0 01-2.812 2.812 3.066 3.066 0 00-1.745.723 3.066 3.066 0 01-3.976 0 3.066 3.066 0 00-1.745-.723 3.066 3.066 0 01-2.812-2.812 3.066 3.066 0 00-.723-1.745 3.066 3.066 0 010-3.976 3.066 3.066 0 00.723-1.745 3.066 3.066 0 012.812-2.812zm7.44 5.252a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
          </svg>
          LLM Intelligence
        </h2>
        <div className="detail-grid">
          <div className="detail-item">
            <div className="detail-label">Risk Assessment</div>
            <div className="detail-value">
              <span className={`badge ${
                call.llm_output.risk_level === 'high' ? 'badge-danger' :
                call.llm_output.risk_level === 'medium' ? 'badge-warning' :
                'badge-success'
              }`}>
                {call.llm_output.risk_level}
              </span>
            </div>
          </div>
          <div className="detail-item">
            <div className="detail-label">Opportunity Assessment</div>
            <div className="detail-value">
              <span className={`badge ${
                call.llm_output.opportunity_level === 'high' ? 'badge-success' :
                call.llm_output.opportunity_level === 'medium' ? 'badge-info' :
                'badge-secondary'
              }`}>
                {call.llm_output.opportunity_level}
              </span>
            </div>
          </div>
          <div className="detail-item">
            <div className="detail-label">LLM Priority Score</div>
            <div className="detail-value">{call.llm_output.priority_score}</div>
          </div>
        </div>

        <div className="mt-3">
          <div className="detail-item w-full">
            <div className="detail-label">Call Summary (Short)</div>
            <div className="detail-value">{call.llm_output.call_summary_short}</div>
          </div>
        </div>

        <div className="mt-3">
          <div className="detail-item w-full">
            <div className="detail-label">Call Summary (Detailed)</div>
            <div className="detail-value">{call.llm_output.call_summary_detailed}</div>
          </div>
        </div>

        <div className="mt-3">
          <div className="detail-item w-full">
            <div className="detail-label">Recommended Action</div>
            <div className="detail-value">{call.llm_output.recommended_action}</div>
          </div>
        </div>

        <div className="mt-3">
          <div className="detail-item w-full">
            <div className="detail-label">Reasoning</div>
            <div className="detail-value">{call.llm_output.reasoning}</div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default CallDetail;
