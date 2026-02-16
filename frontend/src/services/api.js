import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Health & Service Info
export const getServiceInfo = () => api.get('/');
export const getHealthCheck = () => api.get('/health');

// Complete Pipeline
export const processCall = (audioFile) => {
  const formData = new FormData();
  formData.append('file', audioFile);
  return api.post('/process-call', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
};

// Dashboard & Analytics
export const getDashboardMetrics = () => api.get('/dashboard/metrics');
export const getCalls = (params = {}) => api.get('/calls', { params });
export const getCallById = (callId) => api.get(`/calls/${callId}`);

// Action Workflow
export const approveAction = (callId, notes = null) => {
  return api.post(`/approve-action/${callId}`, notes ? { notes } : {});
};

export const rejectAction = (callId, notes = null) => {
  return api.post(`/reject-action/${callId}`, notes ? { notes } : {});
};

// Company Context (RAG)
export const storeCompanyContext = (policyText, metadata = null) => {
  return api.post('/company-context', {
    company_policy_text: policyText,
    metadata,
  });
};

export const getRagStats = () => api.get('/rag/stats');

// Email & CRM Integration
export const sendEmail = (callId, recipientEmail, emailType = 'action') => {
  return api.post('/send-email', {
    call_id: callId,
    recipient_email: recipientEmail,
    email_type: emailType,
  });
};

export const syncToCRM = (callId, actions = ['create_lead', 'create_task', 'log_activity']) => {
  return api.post('/crm/sync', {
    call_id: callId,
    actions,
  });
};

export const getCRMStatus = (callId) => api.get(`/crm/status/${callId}`);

// Individual Layer Endpoints (for debugging)
export const transcribeAudio = (audioFile) => {
  const formData = new FormData();
  formData.append('file', audioFile);
  return api.post('/transcribe', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
};

export const analyzeTranscript = (transcript) => {
  return api.post('/analyze', { transcript });
};

export const generateIntelligence = (transcript, nlpAnalysis) => {
  return api.post('/intelligence', {
    transcript,
    nlp_analysis: nlpAnalysis,
  });
};

export const makeDecision = (nlpAnalysis, llmOutput) => {
  return api.post('/decision', {
    nlp_analysis: nlpAnalysis,
    llm_output: llmOutput,
  });
};

export default api;
