import React, { useState } from 'react';
import { processCall, batchProcessCalls } from '../services/api';
import { useNavigate } from 'react-router-dom';

function ProcessCall() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [isBatchMode, setIsBatchMode] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [result, setResult] = useState(null);
  const [batchResult, setBatchResult] = useState(null);
  const [error, setError] = useState(null);
  const [currentStep, setCurrentStep] = useState(0);
  const navigate = useNavigate();

  const processingSteps = [
    { id: 1, name: 'Uploading Audio', icon: '📤', description: 'Sending audio file to server', duration: 1000 },
    { id: 2, name: 'Speech-to-Text', icon: '🎙️', description: 'Converting speech using OpenAI Whisper', duration: 3000 },
    { id: 3, name: 'NLP Analysis', icon: '🧠', description: 'Analyzing sentiment, keywords, entities', duration: 2000 },
    { id: 4, name: 'RAG Context', icon: '📚', description: 'Retrieving company policies', duration: 1500 },
    { id: 5, name: 'LLM Intelligence', icon: '🤖', description: 'Generating AI recommendations with Groq', duration: 2500 },
    { id: 6, name: 'Business Rules', icon: '⚖️', description: 'Applying validation rules', duration: 1000 },
    { id: 7, name: 'Database Storage', icon: '💾', description: 'Saving to MongoDB', duration: 1000 },
    { id: 8, name: 'Complete', icon: '✅', description: 'Analysis ready!', duration: 500 }
  ];

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
    
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      if (isBatchMode) {
        setSelectedFiles(Array.from(e.dataTransfer.files));
      } else {
        setSelectedFile(e.dataTransfer.files[0]);
      }
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      if (isBatchMode) {
        setSelectedFiles(Array.from(e.target.files));
      } else {
        setSelectedFile(e.target.files[0]);
      }
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (isBatchMode) {
      if (!selectedFiles || selectedFiles.length === 0) {
        setError('Please select audio files for batch processing');
        return;
      }
      
      if (selectedFiles.length > 10) {
        setError('Maximum 10 files can be processed at once');
        return;
      }
      
      setProcessing(true);
      setError(null);
      setBatchResult(null);
      
      try {
        const response = await batchProcessCalls(selectedFiles);
        setBatchResult(response.data);
      } catch (err) {
        setError(err.response?.data?.detail || 'Failed to process batch. Please try again.');
        console.error('Batch process error:', err);
      } finally {
        setProcessing(false);
      }
    } else {
      if (!selectedFile) {
        setError('Please select an audio file');
        return;
      }

      setProcessing(true);
      setError(null);
      setResult(null);
      setCurrentStep(0);

      // Animate through processing steps
      const animateSteps = async () => {
        for (let i = 0; i < processingSteps.length - 1; i++) {
          setCurrentStep(i);
          await new Promise(resolve => setTimeout(resolve, processingSteps[i].duration));
        }
      };

      // Start animation
      animateSteps();

      try {
        const response = await processCall(selectedFile);
        setCurrentStep(processingSteps.length - 1); // Set to complete step
        await new Promise(resolve => setTimeout(resolve, 500)); // Show complete for a moment
        setResult(response.data);
      } catch (err) {
        setError(err.response?.data?.detail || 'Failed to process call. Please try again.');
        console.error('Process call error:', err);
      } finally {
        setProcessing(false);
        setCurrentStep(0);
      }
    }
  };

  const resetForm = () => {
    setSelectedFile(null);
    setSelectedFiles([]);
    setResult(null);
    setBatchResult(null);
    setError(null);
  };

  const toggleBatchMode = () => {
    setIsBatchMode(!isBatchMode);
    setSelectedFile(null);
    setSelectedFiles([]);
    setError(null);
  };

  if (result || batchResult) {
    return (
      <div>
        <div className="page-header">
          <h1 className="page-title">
            <svg className="page-icon" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
            </svg>
            {batchResult ? 'Batch Processing Complete' : 'Call Processed Successfully'}
          </h1>
          {result && <p className="page-subtitle">Call ID: {result.call_id}</p>}
          {batchResult && <p className="page-subtitle">Processed {batchResult.total_files} files</p>}
        </div>

        <div className="alert alert-success">
          <strong>Success!</strong> {batchResult ? `${batchResult.successful} calls processed successfully` : 'Call has been processed and stored in the database.'}
        </div>

        {/* Batch Results */}
        {batchResult && (
          <div className="card">
            <h2 className="card-header">Batch Processing Results</h2>
            <div className="stats-grid" style={{ marginBottom: '1.5rem' }}>
              <div className="stat-card" style={{ borderLeftColor: '#10b981' }}>
                <div className="stat-label">Successful</div>
                <div className="stat-value">{batchResult.successful}</div>
              </div>
              <div className="stat-card" style={{ borderLeftColor: '#ef4444' }}>
                <div className="stat-label">Failed</div>
                <div className="stat-value">{batchResult.failed}</div>
              </div>
            </div>
            
            <div style={{ maxHeight: '400px', overflowY: 'auto' }}>
              {batchResult.results.map((item, index) => (
                <div 
                  key={index}
                  style={{ 
                    padding: '1rem',
                    marginBottom: '0.5rem',
                    background: item.status === 'success' ? '#f0fdf4' : '#fef2f2',
                    border: `1px solid ${item.status === 'success' ? '#86efac' : '#fecaca'}`,
                    borderRadius: '8px'
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                      <div style={{ fontWeight: '600', marginBottom: '0.25rem' }}>{item.filename}</div>
                      {item.status === 'success' ? (
                        <div style={{ fontSize: '0.875rem', color: '#15803d' }}>
                          Priority: {item.priority_score}/100 | Risk: {item.risk_level}
                        </div>
                      ) : (
                        <div style={{ fontSize: '0.875rem', color: '#991b1b' }}>
                          Error: {item.error}
                        </div>
                      )}
                    </div>
                    {item.status === 'success' && (
                      <button 
                        className="btn btn-primary"
                        onClick={() => navigate(`/calls/${item.call_id}`)}
                        style={{ padding: '0.5rem 1rem' }}
                      >
                        View Details
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Single Call Result - Final Decision */}
        {result && (
          <>
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
          </>
        )}

        {/* Actions */}
        <div className="flex gap-2 mt-3">
          {result && (
            <button className="btn btn-primary" onClick={() => navigate(`/calls/${result.call_id}`)}>
              View Full Details
            </button>
          )}
          <button className="btn btn-secondary" onClick={resetForm}>
            Process {isBatchMode ? 'Another Batch' : 'Another Call'}
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
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', width: '100%' }}>
          <div>
            <h1 className="page-title">
              <svg className="page-icon" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M7 4a3 3 0 016 0v4a3 3 0 11-6 0V4zm4 10.93A7.001 7.001 0 0017 8a1 1 0 10-2 0A5 5 0 015 8a1 1 0 00-2 0 7.001 7.001 0 006 6.93V17H6a1 1 0 100 2h8a1 1 0 100-2h-3v-2.07z" clipRule="evenodd" />
              </svg>
              Process Call Recording
            </h1>
            <p className="page-subtitle">Upload audio {isBatchMode ? 'files' : 'file'} for complete AI analysis</p>
          </div>
          <button 
            className={`btn ${isBatchMode ? 'btn-primary' : 'btn-secondary'}`}
            onClick={toggleBatchMode}
            style={{ padding: '0.5rem 1rem' }}
          >
            {isBatchMode ? '⚡ Batch Mode ON' : '📁 Enable Batch Mode'}
          </button>
        </div>
      </div>

      {isBatchMode && (
        <div className="alert alert-info" style={{ marginBottom: '1.5rem' }}>
          <strong>Batch Processing Mode:</strong> You can upload up to 10 audio files at once. All files will be processed sequentially.
        </div>
      )}

      {error && (
        <div className="alert alert-error">
          <strong>Error!</strong> {error}
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
                multiple={isBatchMode}
                onChange={handleFileChange}
                disabled={processing}
              />
              
              {(isBatchMode && selectedFiles && selectedFiles.length > 0) ? (
                <div>
                  <svg style={{width: '60px', height: '60px', margin: '0 auto 1rem', color: '#0284c7'}} viewBox="0 0 20 20" fill="currentColor">
                    <path d="M7 3a1 1 0 000 2h6a1 1 0 100-2H7zM4 7a1 1 0 011-1h10a1 1 0 110 2H5a1 1 0 01-1-1zM2 11a2 2 0 012-2h12a2 2 0 012 2v4a2 2 0 01-2 2H4a2 2 0 01-2-2v-4z" />
                  </svg>
                  <div style={{fontSize: '1.25rem', fontWeight: 600, color: '#1e293b'}}>
                    {selectedFiles.length} file{selectedFiles.length > 1 ? 's' : ''} selected
                  </div>
                  <div style={{color: '#64748b', marginTop: '0.5rem'}}>
                    Total: {(selectedFiles.reduce((sum, f) => sum + f.size, 0) / 1024 / 1024).toFixed(2)} MB
                  </div>
                  <div style={{marginTop: '1rem', maxHeight: '150px', overflowY: 'auto', fontSize: '0.875rem'}}>
                    {selectedFiles.map((file, idx) => (
                      <div key={idx} style={{padding: '0.25rem', color: '#64748b'}}>
                        • {file.name} ({(file.size / 1024 / 1024).toFixed(2)} MB)
                      </div>
                    ))}
                  </div>
                  <div style={{marginTop: '1rem', color: '#64748b'}}>
                    Click to change files
                  </div>
                </div>
              ) : (!isBatchMode && selectedFile) ? (
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
                    Drop audio {isBatchMode ? 'files' : 'file'} here or click to browse
                  </div>
                  <div style={{color: '#64748b'}}>
                    Supported formats: WAV, MP3, M4A, OGG, FLAC{isBatchMode && ' (Max 10 files)'}
                  </div>
                </div>
              )}
            </div>
          </div>

          <div className="flex gap-2">
            <button
              type="submit"
              className="btn btn-primary"
              disabled={(isBatchMode ? (!selectedFiles || selectedFiles.length === 0) : !selectedFile) || processing}
            >
              {processing ? (
                <>
                  <span className="loading-spinner" style={{width: '20px', height: '20px', margin: '0'}}></span>
                  Processing...
                </>
              ) : (
                isBatchMode ? `Process ${selectedFiles?.length || 0} Call${selectedFiles?.length > 1 ? 's' : ''}` : 'Process Call'
              )}
            </button>
            
            {((selectedFile || (selectedFiles && selectedFiles.length > 0)) && !processing) && (
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
          <div className="mt-3" style={{
            background: 'linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%)',
            border: '2px solid #0284c7',
            borderRadius: '12px',
            padding: '2rem',
            boxShadow: '0 8px 24px rgba(2, 132, 199, 0.15)'
          }}>
            <div style={{
              textAlign: 'center',
              marginBottom: '1.5rem'
            }}>
              <h3 style={{
                fontSize: '1.25rem',
                fontWeight: '700',
                color: '#0f172a',
                marginBottom: '0.5rem',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '0.5rem'
              }}>
                {processingSteps[currentStep]?.icon}
                {processingSteps[currentStep]?.name}
              </h3>
              <p style={{
                color: '#64748b',
                fontSize: '0.875rem'
              }}>
                {processingSteps[currentStep]?.description}
              </p>
            </div>

            {/* Progress Info */}
            <div style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              marginBottom: '1rem'
            }}>
              <span style={{
                fontSize: '0.875rem',
                fontWeight: '600',
                color: '#0284c7'
              }}>
                Step {currentStep + 1} of {processingSteps.length}
              </span>
              <span style={{
                fontSize: '0.875rem',
                color: '#64748b'
              }}>
                Processing...
              </span>
            </div>

            {/* Progress Bar */}
            <div style={{
              width: '100%',
              height: '12px',
              background: '#cbd5e1',
              borderRadius: '6px',
              overflow: 'hidden',
              marginBottom: '1.5rem',
              boxShadow: 'inset 0 2px 4px rgba(0,0,0,0.1)'
            }}>
              <div style={{
                width: `${((currentStep + 1) / processingSteps.length) * 100}%`,
                height: '100%',
                background: 'linear-gradient(90deg, #0284c7 0%, #0891b2 100%)',
                transition: 'width 0.5s ease-in-out',
                boxShadow: '0 0 10px rgba(2,132,199,0.5)'
              }}></div>
            </div>

            {/* Processing Steps */}
            <div style={{display: 'flex', flexDirection: 'column', gap: '0.75rem'}}>
              {processingSteps.map((step, index) => {
                const isComplete = index < currentStep;
                const isCurrent = index === currentStep;
                const isPending = index > currentStep;

                return (
                  <div
                    key={step.id}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      padding: '1rem',
                      background: isCurrent ? '#ffffff' : isComplete ? '#e0f2fe' : '#f8fafc',
                      borderRadius: '8px',
                      border: isCurrent ? '2px solid #0284c7' : '1px solid #e2e8f0',
                      transform: isCurrent ? 'scale(1.02)' : 'scale(1)',
                      transition: 'all 0.3s ease-in-out',
                      boxShadow: isCurrent ? '0 4px 12px rgba(2,132,199,0.2)' : 'none',
                      opacity: isPending ? 0.5 : 1
                    }}
                  >
                    <div style={{
                      fontSize: '2rem',
                      marginRight: '1rem',
                      filter: isPending ? 'grayscale(100%)' : 'none',
                      animation: isCurrent ? 'bounce 1s ease-in-out infinite' : 'none'
                    }}>
                      {step.icon}
                    </div>
                    <div style={{flex: 1}}>
                      <div style={{
                        fontWeight: '600',
                        color: isCurrent ? '#0284c7' : isComplete ? '#059669' : '#64748b',
                        fontSize: '1rem',
                        marginBottom: '0.25rem'
                      }}>
                        {step.name}
                        {isComplete && ' ✓'}
                        {isCurrent && ' ⚡'}
                      </div>
                      <div style={{
                        fontSize: '0.875rem',
                        color: '#64748b'
                      }}>
                        {step.description}
                      </div>
                    </div>
                    {isCurrent && (
                      <div className="loading-spinner" style={{
                        width: '20px',
                        height: '20px',
                        borderWidth: '2px',
                        margin: '0'
                      }}></div>
                    )}
                    {isComplete && (
                      <svg style={{width: '24px', height: '24px', color: '#059669'}} viewBox="0 0 20 20" fill="currentColor">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                      </svg>
                    )}
                  </div>
                );
              })}
            </div>

            <div style={{
              marginTop: '1rem',
              padding: '1rem',
              background: '#fef3c7',
              borderRadius: '8px',
              borderLeft: '4px solid #f59e0b'
            }}>
              <p style={{
                fontSize: '0.875rem',
                color: '#92400e',
                margin: 0,
                fontWeight: '500'
              }}>
                💡 <strong>Tip:</strong> Our AI is analyzing your call through multiple layers - this typically takes 8-12 seconds for a complete analysis.
              </p>
            </div>
          </div>
        )}
      </div>

      <style>{`
        @keyframes pulse {
          0%, 100% {
            box-shadow: 0 0 0 0 rgba(2, 132, 199, 0.4);
          }
          50% {
            box-shadow: 0 0 0 10px rgba(2, 132, 199, 0);
          }
        }

        @keyframes bounce {
          0%, 100% {
            transform: translateY(0);
          }
          50% {
            transform: translateY(-5px);
          }
        }
      `}</style>

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
