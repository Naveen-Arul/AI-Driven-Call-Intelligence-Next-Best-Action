import React, { useState } from 'react';
import { processCall } from '../services/api';
import { useNavigate } from 'react-router-dom';

function ProcessCall() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setSelectedFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!selectedFile) {
      setError('Please select an audio file');
      return;
    }

    setProcessing(true);
    setError(null);
    setResult(null);

    try {
      const response = await processCall(selectedFile);
      setResult(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to process call. Please try again.');
      console.error('Process call error:', err);
    } finally {
      setProcessing(false);
    }
  };

  const resetForm = () => {
    setSelectedFile(null);
    setResult(null);
    setError(null);
  };

  if (result) {
    return (
      <div>
        <div className="page-header">
          <h1 className="page-title">
            <svg className="page-icon" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
            </svg>
            Call Processed Successfully
          </h1>
          <p className="page-subtitle">Call ID: {result.call_id}</p>
        </div>

        <div className="alert alert-success">
          <strong>Success!</strong> Call has been processed and stored in the database.
        </div>

        {/* Final Decision */}
        <div className="card">
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
              <div className="detail-value">{result.final_decision.final_action}</div>
            </div>
            <div className="detail-item">
              <div className="detail-label">Priority Score</div>
              <div className="detail-value">
                <span className={`badge ${
                  result.final_decision.priority_score >= 80 ? 'badge-danger' :
                  result.final_decision.priority_score >= 60 ? 'badge-warning' :
                  'badge-info'
                }`}>
                  {result.final_decision.priority_score}/100
                </span>
              </div>
            </div>
            <div className="detail-item">
              <div className="detail-label">Risk Level</div>
              <div className="detail-value">
                <span className={`badge ${
                  result.final_decision.risk_level === 'high' ? 'badge-danger' :
                  result.final_decision.risk_level === 'medium' ? 'badge-warning' :
                  'badge-success'
                }`}>
                  {result.final_decision.risk_level}
                </span>
              </div>
            </div>
            <div className="detail-item">
              <div className="detail-label">Opportunity Level</div>
              <div className="detail-value">
                <span className={`badge ${
                  result.final_decision.opportunity_level === 'high' ? 'badge-success' :
                  result.final_decision.opportunity_level === 'medium' ? 'badge-info' :
                  'badge-secondary'
                }`}>
                  {result.final_decision.opportunity_level}
                </span>
              </div>
            </div>
            <div className="detail-item">
              <div className="detail-label">Escalation Required</div>
              <div className="detail-value">
                <span className={`badge ${result.final_decision.escalation_required ? 'badge-danger' : 'badge-success'}`}>
                  {result.final_decision.escalation_required ? 'Yes' : 'No'}
                </span>
              </div>
            </div>
            <div className="detail-item">
              <div className="detail-label">Confidence Score</div>
              <div className="detail-value">{result.final_decision.confidence_score}%</div>
            </div>
          </div>
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
            {result.transcript}
          </div>
        </div>

        {/* Sentiment */}
        <div className="card mt-3">
          <h2 className="card-header">
            <svg className="card-icon" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM7 9a1 1 0 100-2 1 1 0 000 2zm7-1a1 1 0 11-2 0 1 1 0 012 0zm-.464 5.535a1 1 0 10-1.415-1.414 3 3 0 01-4.242 0 1 1 0 00-1.415 1.414 5 5 0 007.072 0z" clipRule="evenodd" />
            </svg>
            Sentiment Analysis
          </h2>
          <div className="detail-grid">
            <div className="detail-item">
              <div className="detail-label">Overall Sentiment</div>
              <div className="detail-value">
                <span className={`badge ${
                  result.nlp_analysis.sentiment.sentiment_label === 'positive' ? 'badge-success' :
                  result.nlp_analysis.sentiment.sentiment_label === 'negative' ? 'badge-danger' :
                  'badge-secondary'
                }`}>
                  {result.nlp_analysis.sentiment.sentiment_label}
                </span>
              </div>
            </div>
            <div className="detail-item">
              <div className="detail-label">Compound Score</div>
              <div className="detail-value">{result.nlp_analysis.sentiment.compound.toFixed(3)}</div>
            </div>
            <div className="detail-item">
              <div className="detail-label">Intent</div>
              <div className="detail-value">
                <span className="badge badge-info">{result.nlp_analysis.intent}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Actions */}
        <div className="flex gap-2 mt-3">
          <button className="btn btn-primary" onClick={() => navigate(`/calls/${result.call_id}`)}>
            View Full Details
          </button>
          <button className="btn btn-secondary" onClick={resetForm}>
            Process Another Call
          </button>
          <button className="btn btn-secondary" onClick={() => navigate('/calls')}>
            View All Calls
          </button>
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">
          <svg className="page-icon" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M7 4a3 3 0 016 0v4a3 3 0 11-6 0V4zm4 10.93A7.001 7.001 0 0017 8a1 1 0 10-2 0A5 5 0 015 8a1 1 0 00-2 0 7.001 7.001 0 006 6.93V17H6a1 1 0 100 2h8a1 1 0 100-2h-3v-2.07z" clipRule="evenodd" />
          </svg>
          Process Call Recording
        </h1>
        <p className="page-subtitle">Upload an audio file for complete AI analysis</p>
      </div>

      {error && (
        <div className="alert alert-error">
          <strong>Error:</strong> {error}
        </div>
      )}

      <div className="card">
        <h2 className="card-header">
          <svg className="card-icon" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zM6.293 6.707a1 1 0 010-1.414l3-3a1 1 0 011.414 0l3 3a1 1 0 01-1.414 1.414L11 5.414V13a1 1 0 11-2 0V5.414L7.707 6.707a1 1 0 01-1.414 0z" clipRule="evenodd" />
          </svg>
          Upload Audio File
        </h2>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <div
              className={`file-upload-area ${dragActive ? 'drag-active' : ''}`}
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
              onClick={() => document.getElementById('file-input').click()}
            >
              <input
                id="file-input"
                type="file"
                className="file-input"
                accept=".wav,.mp3,.m4a,.ogg,.flac"
                onChange={handleFileChange}
                disabled={processing}
              />
              
              {selectedFile ? (
                <div>
                  <svg style={{width: '60px', height: '60px', margin: '0 auto 1rem', color: '#0284c7'}} viewBox="0 0 20 20" fill="currentColor">
                    <path d="M18 3a1 1 0 00-1.196-.98l-10 2A1 1 0 006 5v9.114A4.369 4.369 0 005 14c-1.657 0-3 .895-3 2s1.343 2 3 2 3-.895 3-2V7.82l8-1.6v5.894A4.37 4.37 0 0015 12c-1.657 0-3 .895-3 2s1.343 2 3 2 3-.895 3-2V3z" />
                  </svg>
                  <div style={{fontSize: '1.25rem', fontWeight: 600, color: '#1e293b'}}>
                    {selectedFile.name}
                  </div>
                  <div style={{color: '#64748b', marginTop: '0.5rem'}}>
                    {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                  </div>
                  <div style={{marginTop: '1rem', color: '#64748b'}}>
                    Click to change file
                  </div>
                </div>
              ) : (
                <div>
                  <svg style={{width: '60px', height: '60px', margin: '0 auto 1rem', color: '#cbd5e1'}} viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zM6.293 6.707a1 1 0 010-1.414l3-3a1 1 0 011.414 0l3 3a1 1 0 01-1.414 1.414L11 5.414V13a1 1 0 11-2 0V5.414L7.707 6.707a1 1 0 01-1.414 0z" clipRule="evenodd" />
                  </svg>
                  <div style={{fontSize: '1.25rem', fontWeight: 600, color: '#1e293b', marginBottom: '0.5rem'}}>
                    Drop audio file here or click to browse
                  </div>
                  <div style={{color: '#64748b'}}>
                    Supported formats: WAV, MP3, M4A, OGG, FLAC
                  </div>
                </div>
              )}
            </div>
          </div>

          <div className="flex gap-2">
            <button
              type="submit"
              className="btn btn-primary"
              disabled={!selectedFile || processing}
            >
              {processing ? (
                <>
                  <span className="loading-spinner" style={{width: '20px', height: '20px', margin: '0'}}></span>
                  Processing...
                </>
              ) : (
                'Process Call'
              )}
            </button>
            
            {selectedFile && !processing && (
              <button
                type="button"
                className="btn btn-secondary"
                onClick={resetForm}
              >
                Clear
              </button>
            )}
          </div>
        </form>

        {processing && (
          <div className="alert alert-info mt-3">
            <strong>Processing Pipeline:</strong>
            <ol style={{marginTop: '0.5rem', marginLeft: '1.5rem'}}>
              <li>Transcribing audio (Whisper STT)</li>
              <li>Analyzing transcript (NLP)</li>
              <li>Retrieving company context (RAG)</li>
              <li>Generating intelligence (LLM)</li>
              <li>Applying business rules</li>
              <li>Storing in database</li>
            </ol>
          </div>
        )}
      </div>

      <div className="card mt-3">
        <h2 className="card-header">
          <svg className="card-icon" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
          </svg>
          What Happens Next?
        </h2>
        <div style={{color: '#475569', lineHeight: '1.8'}}>
          <p><strong>The system will automatically:</strong></p>
          <ul style={{marginLeft: '1.5rem', marginTop: '0.5rem'}}>
            <li>Convert speech to text using OpenAI Whisper</li>
            <li>Analyze sentiment, keywords, entities, and intent</li>
            <li>Generate AI-powered intelligence and recommendations</li>
            <li>Apply business rules and governance</li>
            <li>Calculate priority and confidence scores</li>
            <li>Store complete analysis in MongoDB</li>
            <li>Present actionable insights and next steps</li>
          </ul>
        </div>
      </div>
    </div>
  );
}

export default ProcessCall;
