import React from 'react';
import { useNavigate } from 'react-router-dom';

function Home() {
  const navigate = useNavigate();

  const features = [
    {
      title: 'Speech-to-Text Transcription',
      description: 'Advanced AI-powered transcription using OpenAI Whisper model. Convert sales calls into accurate text transcripts with timestamp tracking and language detection.',
      image: '/images/feature-speech-to-text.png',
      highlights: ['Real-time processing', 'Multi-language support', 'High accuracy']
    },
    {
      title: 'NLP-Based Analysis',
      description: 'Comprehensive natural language processing to extract sentiment, intent, keywords, and entities from every conversation. Get deep insights automatically.',
      image: '/images/feature-nlp-analysis.png',
      highlights: ['Sentiment detection', 'Intent classification', 'Entity extraction']
    },
    {
      title: 'Next-Best-Action Engine',
      description: 'Intelligent recommendation engine powered by AI and business rules. Get actionable insights with priority scoring, risk assessment, and opportunity detection.',
      image: '/images/feature-action-engine.png',
      highlights: ['Smart recommendations', 'Risk scoring', 'Priority management']
    },
    {
      title: 'Review & Approval Dashboard',
      description: 'Comprehensive dashboard for reviewing call analytics, approving or rejecting recommended actions, and tracking key performance metrics in real-time.',
      image: '/images/feature-dashboard.png',
      highlights: ['Real-time metrics', 'Approval workflow', 'Analytics tracking']
    }
  ];

  return (
    <div className="home-container">
      {/* Hero Section */}
      <section className="hero-section">
        <div className="hero-content">
          <h1 className="hero-title">Call Intelligence Platform</h1>
          <p className="hero-subtitle">
            Transform your sales calls into actionable insights with AI-powered analysis
          </p>
          <div className="hero-cta">
            <button className="btn btn-hero-primary" onClick={() => navigate('/process')}>
              Start Processing Calls
            </button>
            <button className="btn btn-hero-secondary" onClick={() => navigate('/dashboard')}>
              View Dashboard
            </button>
          </div>
        </div>
        <div className="hero-image">
          <img 
            src="/images/hero-call-intelligence.png" 
            alt="Call Intelligence Platform"
          />
        </div>
      </section>

      {/* Features Section */}
      <section className="features-section">
        <div className="features-header">
          <h2 className="section-title">Core Features</h2>
          <p className="section-subtitle">
            Our platform provides end-to-end call intelligence automation
          </p>
        </div>

        <div className="features-grid">
          {features.map((feature, index) => (
            <div key={index} className="feature-card">
              <div className="feature-image-wrapper">
                <img src={feature.image} alt={feature.title} className="feature-image" />
              </div>
              <div className="feature-content">
                <h3 className="feature-title">{feature.title}</h3>
                <p className="feature-description">{feature.description}</p>
                <ul className="feature-highlights">
                  {feature.highlights.map((highlight, idx) => (
                    <li key={idx} className="feature-highlight-item">
                      <svg className="check-icon" viewBox="0 0 20 20" fill="currentColor">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                      {highlight}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* How It Works Section */}
      <section className="how-it-works-section">
        <h2 className="section-title">How It Works</h2>
        <div className="process-steps">
          <div className="process-step">
            <div className="step-number">1</div>
            <h3 className="step-title">Upload Audio</h3>
            <p className="step-description">
              Upload your sales call recordings in any common audio format
            </p>
          </div>
          <div className="step-arrow">→</div>
          <div className="process-step">
            <div className="step-number">2</div>
            <h3 className="step-title">AI Processing</h3>
            <p className="step-description">
              Our AI analyzes transcript, sentiment, intent, and extracts key insights
            </p>
          </div>
          <div className="step-arrow">→</div>
          <div className="process-step">
            <div className="step-number">3</div>
            <h3 className="step-title">Get Recommendations</h3>
            <p className="step-description">
              Receive intelligent action recommendations with priority and risk scores
            </p>
          </div>
          <div className="step-arrow">→</div>
          <div className="process-step">
            <div className="step-number">4</div>
            <h3 className="step-title">Review & Approve</h3>
            <p className="step-description">
              Review insights on dashboard and approve or reject recommended actions
            </p>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="cta-section">
        <div className="cta-content">
          <h2 className="cta-title">Ready to Get Started?</h2>
          <p className="cta-text">
            Process your first call now and see the power of AI-driven call intelligence
          </p>
          <button className="btn btn-cta" onClick={() => navigate('/process')}>
            Process Your First Call
          </button>
        </div>
      </section>
    </div>
  );
}

export default Home;
