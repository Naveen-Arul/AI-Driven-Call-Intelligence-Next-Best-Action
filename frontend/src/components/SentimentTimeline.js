import React, { useState, useRef, useEffect } from 'react';

function SentimentTimeline({ segments, audioUrl, callId }) {
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [audioLoading, setAudioLoading] = useState(true);
  const [audioError, setAudioError] = useState(null);
  const audioRef = useRef(null);

  useEffect(() => {
    if (audioUrl && audioRef.current) {
      audioRef.current.load();
    }
  }, [audioUrl]);

  const handleTimeUpdate = () => {
    if (audioRef.current) {
      setCurrentTime(audioRef.current.currentTime);
    }
  };

  const handleLoadedMetadata = () => {
    if (audioRef.current) {
      setDuration(audioRef.current.duration);
      setAudioLoading(false);
    }
  };

  const handlePlayPause = () => {
    if (audioRef.current) {
      if (isPlaying) {
        audioRef.current.pause();
      } else {
        audioRef.current.play();
      }
      setIsPlaying(!isPlaying);
    }
  };

  const handleSeek = (time) => {
    if (audioRef.current) {
      audioRef.current.currentTime = time;
      setCurrentTime(time);
    }
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const getSegmentAtTime = (time) => {
    if (!segments || segments.length === 0) return null;
    return segments.find(seg => time >= seg.start_time && time <= seg.end_time);
  };

  const currentSegment = getSegmentAtTime(currentTime);

  const handleAudioError = (e) => {
    console.error('Audio loading error:', e);
    setAudioError('Failed to load audio. The file may not be available.');
    setAudioLoading(false);
  };

  if (!segments || segments.length === 0) {
    return (
      <div className="card">
        <h2 className="card-header">
          <svg className="card-icon" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clipRule="evenodd" />
          </svg>
          Call Recording & Sentiment Timeline
        </h2>
        <div style={{ padding: '2rem', textAlign: 'center', color: '#6b7280' }}>
          <p>No segment data available for sentiment timeline.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="card">
      <h2 className="card-header">
        <svg className="card-icon" viewBox="0 0 20 20" fill="currentColor">
          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clipRule="evenodd" />
        </svg>
        Call Recording & Real-Time Sentiment Timeline
      </h2>

      {/* Audio Player */}
      {audioUrl && (
        <div style={{ padding: '1rem', background: '#f8fafc', borderRadius: '8px', marginBottom: '1rem' }}>
          <audio
            ref={audioRef}
            src={audioUrl}
            onTimeUpdate={handleTimeUpdate}
            onLoadedMetadata={handleLoadedMetadata}
            onEnded={() => setIsPlaying(false)}
            onError={handleAudioError}
            style={{ display: 'none' }}
          />
          
          {audioLoading && !audioError && (
            <div style={{ textAlign: 'center', padding: '1rem', color: '#6b7280' }}>
              Loading audio...
            </div>
          )}

          {audioError && (
            <div style={{ textAlign: 'center', padding: '1rem', color: '#ef4444' }}>
              {audioError}
            </div>
          )}

          {!audioLoading && !audioError && (
            <>
              <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '0.5rem' }}>
                <button
                  onClick={handlePlayPause}
                  style={{
                    width: '48px',
                    height: '48px',
                    borderRadius: '50%',
                    border: 'none',
                    background: 'linear-gradient(135deg, #0284c7 0%, #0891b2 100%)',
                    color: 'white',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '20px'
                  }}
                >
                  {isPlaying ? '⏸' : '▶'}
                </button>
                <div style={{ flex: 1 }}>
                  <div style={{ fontSize: '0.875rem', color: '#6b7280', marginBottom: '0.25rem' }}>
                    {formatTime(currentTime)} / {formatTime(duration)}
                  </div>
                  <input
                    type="range"
                    min="0"
                    max={duration || 0}
                    value={currentTime}
                    onChange={(e) => handleSeek(parseFloat(e.target.value))}
                    style={{ width: '100%', cursor: 'pointer' }}
                  />
                </div>
              </div>

              {/* Current Segment Info */}
              {currentSegment && (
                <div style={{ 
                  padding: '0.75rem', 
                  background: 'white', 
                  borderRadius: '6px',
                  border: '1px solid #e5e7eb',
                  marginTop: '1rem'
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
                    <span style={{ fontSize: '1.5rem' }}>{currentSegment.emoji}</span>
                    <span className={`badge ${
                      currentSegment.emotion_label === 'happy' || currentSegment.emotion_label === 'satisfied' ? 'badge-success' :
                      currentSegment.emotion_label === 'angry' || currentSegment.emotion_label === 'frustrated' ? 'badge-danger' :
                      'badge-secondary'
                    }`}>
                      {currentSegment.emotion_label}
                    </span>
                    <span style={{ fontSize: '0.75rem', color: '#6b7280' }}>
                      {formatTime(currentSegment.start_time)} - {formatTime(currentSegment.end_time)}
                    </span>
                  </div>
                  <div style={{ fontSize: '0.875rem', color: '#374151' }}>
                    "{currentSegment.text}"
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      )}

      {/* Sentiment Timeline Visualization */}
      <div style={{ marginTop: '1.5rem' }}>
        <h3 style={{ fontSize: '1rem', fontWeight: '600', marginBottom: '1rem', color: '#1f2937' }}>
          Emotion Timeline
        </h3>
        
        <div style={{ 
          position: 'relative', 
          height: '80px', 
          background: '#f8fafc', 
          borderRadius: '8px',
          padding: '0.5rem',
          overflow: 'hidden'
        }}>
          {/* Timeline segments */}
          <div style={{ display: 'flex', height: '100%', gap: '2px' }}>
            {segments.map((segment, index) => {
              const segmentWidth = duration > 0 
                ? ((segment.end_time - segment.start_time) / duration * 100) 
                : (100 / segments.length);
              
              let bgColor = '#94a3b8'; // neutral
              if (segment.emotion_label === 'happy' || segment.emotion_label === 'satisfied') {
                bgColor = '#10b981'; // green
              } else if (segment.emotion_label === 'angry' || segment.emotion_label === 'frustrated') {
                bgColor = '#ef4444'; // red
              }

              const isActive = currentSegment && currentSegment.start_time === segment.start_time;
              
              return (
                <div
                  key={index}
                  onClick={() => handleSeek(segment.start_time)}
                  style={{
                    width: `${segmentWidth}%`,
                    background: bgColor,
                    opacity: isActive ? 1 : 0.7,
                    cursor: 'pointer',
                    borderRadius: '4px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '1.25rem',
                    transition: 'all 0.2s',
                    border: isActive ? '2px solid #1f2937' : 'none',
                    transform: isActive ? 'scale(1.05)' : 'scale(1)'
                  }}
                  title={`${segment.emotion_label}: "${segment.text.substring(0, 50)}..."`}
                >
                  {segment.emoji}
                </div>
              );
            })}
          </div>

          {/* Playhead indicator */}
          {duration > 0 && (
            <div
              style={{
                position: 'absolute',
                top: 0,
                left: `${(currentTime / duration) * 100}%`,
                width: '2px',
                height: '100%',
                background: '#1f2937',
                pointerEvents: 'none',
                transition: 'left 0.1s linear'
              }}
            />
          )}
        </div>

        {/* Legend */}
        <div style={{ 
          display: 'flex', 
          gap: '1rem', 
          marginTop: '1rem', 
          fontSize: '0.875rem',
          flexWrap: 'wrap'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span style={{ fontSize: '1.25rem' }}>😊</span>
            <span>Happy/Satisfied</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span style={{ fontSize: '1.25rem' }}>😶</span>
            <span>Neutral</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span style={{ fontSize: '1.25rem' }}>😠</span>
            <span>Frustrated/Angry</span>
          </div>
        </div>
      </div>

      {/* Critical Moments Detection */}
      {segments.filter(s => s.emotion_label === 'angry' || s.emotion_label === 'frustrated').length > 0 && (
        <div style={{ 
          marginTop: '1.5rem', 
          padding: '1rem', 
          background: '#fef2f2', 
          border: '1px solid #fecaca',
          borderRadius: '8px'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
            <svg style={{ width: '20px', height: '20px', color: '#ef4444' }} viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
            <strong style={{ color: '#991b1b' }}>Critical Moments Detected</strong>
          </div>
          <div style={{ fontSize: '0.875rem', color: '#7f1d1d' }}>
            {segments.filter(s => s.emotion_label === 'angry' || s.emotion_label === 'frustrated').length} segment(s) 
            with negative sentiment detected. Click on the red sections above to review.
          </div>
        </div>
      )}
    </div>
  );
}

export default SentimentTimeline;
