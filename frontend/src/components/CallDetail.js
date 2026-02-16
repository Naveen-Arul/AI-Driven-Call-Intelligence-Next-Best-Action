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
            <h1 className="page-title">📞 Call Details</h1>
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
                ✅ Approve Action
              </button>
              <button
                className="btn btn-danger"
                onClick={handleReject}
                disabled={actionLoading}
              >
                ❌ Reject Action
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
        <h2 className="card-header">📋 Final Decision</h2>
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
        <h2 className="card-header">📝 Transcript</h2>
        <div style={{padding: '1rem', background: '#f8fafc', borderRadius: '8px', whiteSpace: 'pre-wrap'}}>
          {call.transcript}
        </div>
      </div>

      {/* NLP Analysis */}
      <div className="card mt-3">
        <h2 className="card-header">🧠 NLP Analysis</h2>
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
        <h2 className="card-header">🤖 LLM Intelligence</h2>
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
