import React, { useState, useEffect } from 'react';
import { storeCompanyContext, getRagStats } from '../services/api';

function CompanyContext() {
  const [policyText, setPolicyText] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(null);
  const [error, setError] = useState(null);
  const [stats, setStats] = useState(null);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      const response = await getRagStats();
      setStats(response.data);
    } catch (err) {
      console.error('Failed to load RAG stats:', err);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!policyText.trim()) {
      setError('Please enter company policy text');
      return;
    }

    setLoading(true);
    setSuccess(null);
    setError(null);

    try {
      const response = await storeCompanyContext(policyText);
      
      if (response.data.success) {
        setSuccess(`Successfully stored ${response.data.chunks_stored} policy chunks`);
        setPolicyText('');
        loadStats();
      } else {
        setError(response.data.error || 'Failed to store context');
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to store company context');
      console.error('Store context error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">🧠 Company Knowledge Base</h1>
        <p className="page-subtitle">Store company policies for context-aware AI decisions</p>
      </div>

      {/* RAG Service Status */}
      {stats && (
        <div className="card mb-3">
          <h2 className="card-header">RAG Service Status</h2>
          <div className="detail-grid">
            <div className="detail-item">
              <div className="detail-label">Service Status</div>
              <div className="detail-value">
                <span className={`badge ${stats.status === 'active' ? 'badge-success' : 'badge-warning'}`}>
                  {stats.status}
                </span>
              </div>
            </div>
            <div className="detail-item">
              <div className="detail-label">Total Documents</div>
              <div className="detail-value">{stats.total_documents}</div>
            </div>
            <div className="detail-item">
              <div className="detail-label">Embedding Model</div>
              <div className="detail-value">{stats.embedding_model}</div>
            </div>
            <div className="detail-item">
              <div className="detail-label">Collection</div>
              <div className="detail-value">{stats.collection_name}</div>
            </div>
          </div>

          {stats.status === 'disabled' && (
            <div className="alert alert-info mt-3">
              <strong>Note:</strong> RAG service is currently disabled. Company context will not be available for LLM decisions. The system will continue to work with transcript and NLP analysis only.
            </div>
          )}
        </div>
      )}

      {success && (
        <div className="alert alert-success">
          <strong>Success!</strong> {success}
        </div>
      )}

      {error && (
        <div className="alert alert-error">
          <strong>Error:</strong> {error}
        </div>
      )}

      {/* Upload Form */}
      <div className="card">
        <h2 className="card-header">Upload Company Policy</h2>
        
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">Company Policy Text</label>
            <textarea
              className="form-textarea"
              style={{minHeight: '300px'}}
              placeholder="Enter your company policies, guidelines, or knowledge base content here...&#10;&#10;Example:&#10;- Customer refund policy&#10;- Product information&#10;- Service level agreements&#10;- Company values and mission&#10;- Standard operating procedures"
              value={policyText}
              onChange={(e) => setPolicyText(e.target.value)}
              disabled={loading}
            />
            <div style={{color: '#64748b', fontSize: '0.875rem', marginTop: '0.5rem'}}>
              The system will automatically chunk and embed this text for semantic search.
            </div>
          </div>

          <button
            type="submit"
            className="btn btn-primary"
            disabled={loading || !policyText.trim()}
          >
            {loading ? (
              <>
                <span className="loading-spinner" style={{width: '20px', height: '20px', margin: '0'}}></span>
                Storing...
              </>
            ) : (
              <>📚 Store Company Context</>
            )}
          </button>
        </form>
      </div>

      {/* Information Card */}
      <div className="card mt-3">
        <h2 className="card-header">💡 How It Works</h2>
        <div style={{color: '#475569', lineHeight: '1.8'}}>
          <p><strong>Company Context Retrieval-Augmented Generation (RAG):</strong></p>
          <ul style={{marginLeft: '1.5rem', marginTop: '0.5rem'}}>
            <li>Your company policies are automatically chunked into smaller segments</li>
            <li>Each chunk is converted into embeddings using sentence transformers</li>
            <li>Stored in ChromaDB vector database for semantic search</li>
            <li>During call processing, relevant policy chunks are retrieved</li>
            <li>LLM uses this context to make policy-aware decisions</li>
            <li>Ensures recommendations align with your company guidelines</li>
          </ul>
          
          <p className="mt-3"><strong>What to include:</strong></p>
          <ul style={{marginLeft: '1.5rem', marginTop: '0.5rem'}}>
            <li>Customer service policies and escalation procedures</li>
            <li>Product specifications and pricing guidelines</li>
            <li>Refund and return policies</li>
            <li>Service level agreements (SLAs)</li>
            <li>Company values and communication standards</li>
            <li>Compliance requirements and regulations</li>
          </ul>
        </div>
      </div>

      {/* Example Template */}
      <div className="card mt-3">
        <h2 className="card-header">📝 Example Template</h2>
        <div style={{
          padding: '1rem',
          background: '#f8fafc',
          borderRadius: '8px',
          fontFamily: 'monospace',
          fontSize: '0.875rem',
          whiteSpace: 'pre-wrap'
        }}>
{`COMPANY POLICY - CUSTOMER SERVICE

Refund Policy:
- Full refunds available within 30 days of purchase
- Partial refunds (50%) available within 60 days
- No refunds after 60 days without manager approval

Escalation Procedure:
- High-risk churn situations must be escalated immediately
- Revenue opportunities over $10,000 require sales manager review
- Complaints about product quality go to QA team

Response Time SLA:
- Critical issues: 1 hour response time
- High priority: 4 hour response time
- Medium priority: 24 hour response time
- Low priority: 48 hour response time

Pricing Authority:
- Representatives can offer up to 15% discount
- Discounts 15-25% require team lead approval
- Discounts above 25% require VP approval`}
        </div>
      </div>
    </div>
  );
}

export default CompanyContext;
