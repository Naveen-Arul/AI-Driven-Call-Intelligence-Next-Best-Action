// Voice Chat Application - Call Flow Implementation
console.log('🚀 voice-chat.js LOADED');

const API_URL = 'http://localhost:8000';

// Catch all errors
window.addEventListener('error', (e) => {
    console.error('🔴 GLOBAL ERROR:', e.error);
    console.error('Message:', e.message);
    console.error('Stack:', e.error?.stack);
});

// Catch unhandled promise rejections
window.addEventListener('unhandledrejection', (e) => {
    console.error('🔴 UNHANDLED PROMISE REJECTION:', e.reason);
    e.preventDefault(); // Prevent page from reloading
});

class VoiceChat {
    constructor() {
        console.log('🏗️ VoiceChat constructor called');
        // DOM Elements
        this.startCallBtn = document.getElementById('startCallBtn');
        this.micBtn = document.getElementById('micBtn');
        this.endCallBtn = document.getElementById('endCallBtn');
        this.statusDisplay = document.getElementById('statusDisplay');
        this.statusIndicator = document.getElementById('statusIndicator');
        this.statusText = document.getElementById('statusText');
        this.transcriptContainer = document.getElementById('transcriptContainer');
        this.audioPlayer = document.getElementById('audioPlayer');

        // State
        this.callActive = false;
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.isRecording = false;
        this.conversationHistory = [];
        this.detectedLang = null;
        this.callStartTime = null;
        this.sessionId = this.generateSessionId();
        this.audioFiles = [];  // Track saved audio file paths
        this.recordingStartTime = null;  // Track recording duration

        // Initialize
        this.init();
    }

    init() {
        console.log('⚙️ Initializing event handlers...');
        // Event Listeners with preventDefault to prevent page refresh
        this.startCallBtn.addEventListener('click', (e) => {
            console.log('🔘 Start Call button clicked');
            e.preventDefault();
            e.stopPropagation();
            this.startCall();
        });
        this.endCallBtn.addEventListener('click', (e) => {
            console.log('🔘 End Call button clicked');
            e.preventDefault();
            e.stopPropagation();
            this.endCall();
        });
        
        // Toggle recording on click
        this.micBtn.addEventListener('click', (e) => {
            console.log('🔘 Mic button clicked');
            e.preventDefault();
            e.stopPropagation();
            this.toggleRecording();
        });
        
        console.log('✅ Event handlers registered');
        
        // Check browser support
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            this.showError('Your browser does not support audio recording. Please use Chrome or Firefox.');
        }
    }

    generateSessionId() {
        return `call_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    async startCall() {
        try {
            // Request microphone permission
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            stream.getTracks().forEach(track => track.stop()); // Release immediately
            
            this.callActive = true;
            this.callStartTime = new Date();
            this.conversationHistory = [];
            
            // Update UI
            this.startCallBtn.classList.add('hidden');
            this.micBtn.classList.remove('hidden');
            this.endCallBtn.classList.remove('hidden');
            this.updateStatus('active', 'Ready - Click mic to speak');
            
            // Clear transcript
            this.transcriptContainer.innerHTML = '';
            this.addSystemMessage('Call started. Click "Press to Speak" to begin.');
            
        } catch (error) {
            console.error('Error starting call:', error);
            this.showError('Could not access microphone. Please allow microphone permission.');
        }
    }

    toggleRecording() {
        console.log(`🎛️ Toggle recording - Currently recording: ${this.isRecording}, Call active: ${this.callActive}`);
        if (!this.callActive) {
            console.log('⚠️ Call not active, cannot record');
            return;
        }
        
        if (this.isRecording) {
            console.log('🛑 Stopping recording...');
            this.stopRecording();
        } else {
            console.log('▶️ Starting recording...');
            this.startRecording();
        }
    }

    async startRecording() {
        if (this.isRecording) return;
        
        console.log('🎙️ Starting recording...');
        this.recordingStartTime = Date.now();
        
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ 
                audio: {
                    echoCancellation: true,
                    noiseSuppression: true,
                    sampleRate: 44100
                }
            });
            
            // Check for supported MIME types
            let mimeType = 'audio/webm;codecs=opus';
            if (!MediaRecorder.isTypeSupported(mimeType)) {
                mimeType = 'audio/webm';
                if (!MediaRecorder.isTypeSupported(mimeType)) {
                    mimeType = 'audio/ogg;codecs=opus';
                    if (!MediaRecorder.isTypeSupported(mimeType)) {
                        mimeType = ''; // Use default
                    }
                }
            }
            
            const options = mimeType ? { mimeType } : {};
            this.mediaRecorder = new MediaRecorder(stream, options);
            this.audioChunks = [];
            this.isRecording = true;

            this.mediaRecorder.addEventListener('dataavailable', event => {
                if (event.data && event.data.size > 0) {
                    this.audioChunks.push(event.data);
                }
            });

            this.mediaRecorder.addEventListener('stop', () => {
                this.processRecording();
            });

            // Start recording with timeslice to ensure data collection
            this.mediaRecorder.start(100); // Collect data every 100ms
            
            // Update button UI
            this.updateRecordingButton(true);
            this.updateStatus('recording', 'Recording... Click Stop when done');
            
        } catch (error) {
            console.error('Error starting recording:', error);
            this.showError('Could not access microphone.');
        }
    }

    stopRecording() {
        if (!this.isRecording || !this.mediaRecorder) return;
        
        // Check minimum recording duration (at least 500ms)
        const recordingDuration = Date.now() - this.recordingStartTime;
        console.log(`🛑 Stop recording - Duration: ${recordingDuration}ms`);
        
        if (recordingDuration < 500) {
            // Too short - cancel recording
            console.warn('⚠️ Recording too short, cancelled');
            this.mediaRecorder.stop();
            this.isRecording = false;
            
            // Stop all tracks
            if (this.mediaRecorder.stream) {
                this.mediaRecorder.stream.getTracks().forEach(track => track.stop());
            }
            
            this.audioChunks = [];  // Clear chunks
            this.updateRecordingButton(false);
            this.showError('Recording too short. Please record for at least 0.5 seconds.');
            this.updateStatus('active', 'Ready - Click mic to speak');
            return;
        }
        
        this.mediaRecorder.stop();
        this.isRecording = false;
        
        // Stop all tracks
        if (this.mediaRecorder.stream) {
            this.mediaRecorder.stream.getTracks().forEach(track => track.stop());
        }
        
        this.updateRecordingButton(false);
        this.updateStatus('processing', 'Processing...');
    }

    async processRecording() {
        console.log('📦 Processing recording...');
        try {
            // Validate audio chunks
            if (this.audioChunks.length === 0) {
                console.error('❌ No audio chunks');
                this.showError('No audio recorded. Please try again.');
                this.updateStatus('active', 'Ready - Click mic to speak');
                return;
            }

            // Create blob with proper MIME type
            const mimeType = this.mediaRecorder?.mimeType || 'audio/webm';
            const audioBlob = new Blob(this.audioChunks, { type: mimeType });
            
            console.log(`📊 Audio blob created: ${audioBlob.size} bytes, type: ${mimeType}`);
            
            // Validate blob size
            if (audioBlob.size < 5000) { // Less than 5KB is likely too short
                const duration = Date.now() - this.recordingStartTime;
                console.warn(`⚠️ Audio too short: ${audioBlob.size} bytes`);
                this.showError(`Recording too short (${(duration/1000).toFixed(1)}s, ${audioBlob.size} bytes). Please record for at least 1 second and speak clearly.`);
                this.updateStatus('active', 'Ready - Click mic to speak');
                return;
            }
            
            // Step 1: Transcribe with auto language detection
            this.updateStatus('processing', 'Transcribing...');
            console.log('🎙️ Sending audio for transcription...');
            const transcriptionData = await this.transcribeAudio(audioBlob);
            console.log('✅ Transcription received:', transcriptionData);

            let transcription = transcriptionData.text || transcriptionData;
            console.log(`📝 Transcription text: "${transcription}"`);
            
            if (!transcription || transcription.trim() === '') {
                console.warn('⚠️ Empty transcription');
                this.showError('Could not hear anything. Please speak clearly and try again.');
                this.updateStatus('active', 'Ready - Click mic to speak');
                return;
            }

            // Auto-detect language from Whisper (on first speech if not set)
            if (!this.detectedLang && transcriptionData.language) {
                this.detectedLang = transcriptionData.language;
                const langName = this.getLanguageName(this.detectedLang);
                console.log(`🌍 Language detected: ${langName} (${this.detectedLang})`);
                document.getElementById('languageText').textContent = `${langName} (${this.detectedLang.toUpperCase()})`;
                document.getElementById('languageText').style.color = '#0891b2';
                document.getElementById('languageText').style.fontWeight = '600';
            }

            // Track audio file if returned
            if (transcriptionData.audio_file) {
                this.audioFiles.push(transcriptionData.audio_file);
                console.log(`💾 Audio saved: ${transcriptionData.audio_file}`);
            }

            // Add customer message to UI
            console.log('💬 Adding customer message to UI...');
            this.addMessage('customer', transcription);
            console.log('✅ Customer message added');

            // Step 2: Get AI response in detected language
            this.updateStatus('processing', 'AI Thinking...');
            console.log('🤖 Requesting AI response...');
            const aiResponse = await this.getAIResponse(transcription);
            console.log('✅ AI response received:', aiResponse);

            // Add agent message to UI
            console.log('💬 Adding AI message to UI...');
            this.addMessage('agent', aiResponse);
            console.log('✅ AI message added');

            // Step 3: Play AI speech in detected language
            this.updateStatus('speaking', 'AI Speaking...');
            console.log('🔊 Playing AI speech...');
            await this.playAIResponse(aiResponse);
            console.log('✅ AI speech completed');

            // Ready for next input - KEEP CALL ACTIVE
            console.log('✅ Ready for next turn');
            this.updateStatus('active', 'Ready - Click mic to speak');

        } catch (error) {
            console.error('❌ Error processing recording:', error);
            console.error('Error stack:', error.stack);
            console.log('Call state after error - callActive:', this.callActive, 'isRecording:', this.isRecording);
            
            // Show error but keep call active
            this.showError(`Error: ${error.message}. Please try again.`);
            this.updateStatus('active', 'Ready - Click mic to speak');
            
            // Make sure call stays active and button is ready
            if (this.callActive) {
                console.log('✅ Call still active, ready for next recording');
            } else {
                console.error('⚠️ WARNING: Call became inactive during error!');
            }
        }
    }

    updateRecordingButton(isRecording) {
        const micBtnText = document.getElementById('micBtnText');
        const micBtn = this.micBtn;
        
        if (isRecording) {
            micBtnText.textContent = 'Stop Recording';
            micBtn.classList.remove('btn-secondary');
            micBtn.classList.add('btn-danger');
            micBtn.style.animation = 'pulse 1.5s infinite';
        } else {
            micBtnText.textContent = 'Press to Speak';
            micBtn.classList.remove('btn-danger');
            micBtn.classList.add('btn-secondary');
            micBtn.style.animation = '';
        }
    }

    async transcribeAudio(audioBlob) {
        try {
            const formData = new FormData();
            
            // Determine file extension based on MIME type
            let filename = 'recording.webm';
            if (audioBlob.type.includes('ogg')) {
                filename = 'recording.ogg';
            } else if (audioBlob.type.includes('mp4')) {
                filename = 'recording.mp4';
            }
            
            formData.append('audio', audioBlob, filename);

            console.log(`📤 Sending ${audioBlob.size} bytes to ${API_URL}/api/voice/transcribe`);
            
            const response = await fetch(`${API_URL}/api/voice/transcribe`, {
                method: 'POST',
                body: formData
            });

            console.log('📥 Transcription response status:', response.status);
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ detail: 'Transcription failed' }));
                console.error('❌ Transcription error:', errorData);
                throw new Error(errorData.detail || 'Transcription failed');
            }

            const result = await response.json();
            console.log('✅ Transcription result:', result);
            return result;
        } catch (error) {
            console.error('❌ transcribeAudio error:', error);
            throw error; // Re-throw to be caught by processRecording
        }
    }

    async getAIResponse(userMessage) {
        try {
            // Use auto-detected language (default to English if not detected yet)
            const language = this.detectedLang || 'en';
            
            console.log(`📤 Requesting AI response for: "${userMessage}" in ${language}`);
            
            const response = await fetch(`${API_URL}/api/voice/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    message: userMessage,
                    language: language,
                    session_id: this.sessionId,
                    history: this.conversationHistory.slice(-10)
                })
            });

            console.log('📥 AI response status:', response.status);
            
            if (!response.ok) {
                const errorText = await response.text();
                console.error('❌ AI response error:', errorText);
                throw new Error(`AI response failed: ${response.status}`);
            }

            const data = await response.json();
            console.log('✅ AI response data:', data);
            
            // Save to history
            this.conversationHistory.push({
                role: 'customer',
                content: userMessage,
                timestamp: new Date().toISOString()
            });
            this.conversationHistory.push({
                role: 'agent',
                content: data.response,
                timestamp: new Date().toISOString(),
                sentiment: data.sentiment || 'neutral'
            });

            return data.response;
        } catch (error) {
            console.error('❌ getAIResponse error:', error);
            throw error; // Re-throw to be caught by processRecording
        }
    }

    async playAIResponse(text) {
        try {
            // Use auto-detected language (default to English if not detected yet)
            const language = this.detectedLang || 'en';
            
            console.log(`📤 Requesting TTS for: "${text.substring(0, 50)}..." in ${language}`);
            
            const response = await fetch(`${API_URL}/api/voice/tts`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    text: text,
                    language: language
                })
            });

            console.log('📥 TTS response status:', response.status);
            
            if (!response.ok) {
                const errorText = await response.text();
                console.error('⚠️ TTS failed:', errorText);
                console.error('⚠️ Continuing without audio...');
                return; // Don't throw error, just skip TTS
            }

            const audioBlob = await response.blob();
            console.log(`✅ Audio blob received: ${audioBlob.size} bytes, type: ${audioBlob.type}`);
            const audioUrl = URL.createObjectURL(audioBlob);
            console.log('🔊 Created audio URL:', audioUrl);
            console.log('🔊 Playing TTS audio...');

            return new Promise((resolve, reject) => {
                this.audioPlayer.src = audioUrl;
                this.audioPlayer.volume = 1.0; // Ensure volume is at max
                
                this.audioPlayer.onloadeddata = () => {
                    console.log('✅ Audio loaded, duration:', this.audioPlayer.duration, 'seconds');
                };
                
                this.audioPlayer.onended = () => {
                    console.log('✅ TTS playback completed');
                    URL.revokeObjectURL(audioUrl); // Clean up
                    resolve();
                };
                
                this.audioPlayer.onerror = (err) => {
                    console.error('⚠️ TTS playback error:', err);
                    console.error('Audio player error details:', this.audioPlayer.error);
                    URL.revokeObjectURL(audioUrl);
                    resolve(); // Resolve anyway, don't block conversation
                };
                
                // Attempt to play
                const playPromise = this.audioPlayer.play();
                
                if (playPromise !== undefined) {
                    playPromise
                        .then(() => {
                            console.log('✅ Audio playback started successfully');
                        })
                        .catch(err => {
                            console.error('⚠️ Audio play error:', err.name, '-', err.message);
                            if (err.name === 'NotAllowedError') {
                                console.error('🔴 Browser blocked autoplay - user interaction required');
                                alert('Please click anywhere on the page to enable audio playback');
                            }
                            URL.revokeObjectURL(audioUrl);
                            resolve(); // Resolve anyway
                        });
                }
            });
        } catch (error) {
            console.error('⚠️ playAIResponse error (non-critical):', error);
            // Don't throw - TTS failure shouldn't stop the conversation
        }
    }

    async endCall() {
        console.log('🔚 END CALL button pressed');
        if (!this.callActive) {
            console.log('⚠️ Call not active, ignoring');
            return;
        }
        
        this.updateStatus('processing', 'Ending call...');
        console.log('💾 Saving call to database...');
        
        try {
            // Save call to database
            await this.saveCallToDatabase();
            
            this.callActive = false;
            this.conversationHistory = [];
            this.detectedLang = null;
            this.audioFiles = [];  // Reset audio files list
            
            // Reset language display
            const languageText = document.getElementById('languageText');
            if (languageText) {
                languageText.textContent = 'Will be detected automatically';
                languageText.style.color = '';
                languageText.style.fontWeight = '';
            }
            
            // Update UI
            this.startCallBtn.classList.remove('hidden');
            this.micBtn.classList.add('hidden');
            this.endCallBtn.classList.add('hidden');
            this.updateStatus('', 'Call ended');
            
            this.addSystemMessage('Call ended. Summary sent to admin dashboard.');
            
            setTimeout(() => {
                this.updateStatus('', 'Ready to start');
            }, 2000);
            
        } catch (error) {
            console.error('Error ending call:', error);
            this.showError('Error saving call summary.');
        }
    }

    async saveCallToDatabase() {
        // Calculate call duration
        const callDuration = Math.floor((new Date() - this.callStartTime) / 1000);
        
        // Build full transcript
        const fullTranscript = this.conversationHistory
            .map(msg => `${msg.role === 'customer' ? 'Customer' : 'Agent'}: ${msg.content}`)
            .join('\n\n');
        
        // Detect overall sentiment and urgency
        const customerMessages = this.conversationHistory.filter(m => m.role === 'customer');
        const agentMessages = this.conversationHistory.filter(m => m.role === 'agent');
        
        const response = await fetch(`${API_URL}/api/voice/save-call`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                session_id: this.sessionId,
                transcript: fullTranscript,
                customer_queries: customerMessages.map(m => m.content),
                agent_responses: agentMessages.map(m => m.content),
                conversation_history: this.conversationHistory,
                audio_files: this.audioFiles,  // Include saved audio file paths
                language: this.detectedLang || this.languageSelect.value,
                duration: callDuration,
                timestamp: this.callStartTime.toISOString()
            })
        });

        if (!response.ok) {
            throw new Error('Failed to save call');
        }

        return await response.json();
    }

    addMessage(role, text) {
        try {
            console.log(`📝 addMessage called - role: ${role}, text: "${text}"`);
            
            // Ensure transcript container exists
            if (!this.transcriptContainer) {
                console.error('❌ Transcript container not found!');
                return;
            }
            
            console.log('✅ Transcript container exists:', this.transcriptContainer.id);
            
            // Remove empty state if exists
            const emptyState = this.transcriptContainer.querySelector('.transcript-empty');
            if (emptyState) {
                console.log('🗑️ Removing empty state');
                emptyState.remove();
            }

            const messageDiv = document.createElement('div');
            messageDiv.className = `transcript-message ${role}`;
            console.log('✅ Created message div with class:', messageDiv.className);

            const now = new Date();
            const timeString = now.toLocaleTimeString('en-IN', { 
                hour: '2-digit', 
                minute: '2-digit',
                second: '2-digit'
            });
            console.log('✅ Timestamp created:', timeString);

            const escapedText = this.escapeHtml(text);
            console.log('✅ Text escaped successfully, length:', escapedText.length);

            messageDiv.innerHTML = `
                <div class="message-header">
                    <span>${role === 'customer' ? 'You' : 'AI Agent'}</span>
                    <span class="message-time">${timeString}</span>
                </div>
                <div class="message-text">${escapedText}</div>
            `;
            console.log('✅ Set innerHTML');

            this.transcriptContainer.appendChild(messageDiv);
            console.log('✅ Appended to container');
            
            this.transcriptContainer.scrollTop = this.transcriptContainer.scrollHeight;
            console.log('✅ Scrolled to bottom');
            
            console.log('✅ Message added to DOM, total messages:', this.transcriptContainer.children.length);
        } catch (error) {
            console.error('❌ Error in addMessage:', error);
            console.error('Error stack:', error.stack);
        }
    }

    addSystemMessage(text) {
        const emptyState = this.transcriptContainer.querySelector('.transcript-empty');
        if (emptyState) {
            emptyState.remove();
        }

        const messageDiv = document.createElement('div');
        messageDiv.className = 'transcript-message';
        messageDiv.style.background = 'linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%)';
        messageDiv.style.borderLeft = '4px solid #64748b';

        const now = new Date();
        const timeString = now.toLocaleTimeString('en-IN', { 
            hour: '2-digit', 
            minute: '2-digit',
            second: '2-digit'
        });

        messageDiv.innerHTML = `
            <div class="message-header">
                <span>System</span>
                <span class="message-time">${timeString}</span>
            </div>
            <div class="message-text">${this.escapeHtml(text)}</div>
        `;

        this.transcriptContainer.appendChild(messageDiv);
        this.transcriptContainer.scrollTop = this.transcriptContainer.scrollHeight;
    }

    updateStatus(state, text) {
        this.statusDisplay.className = 'status-display ' + state;
        this.statusText.textContent = text;
    }

    showError(message) {
        this.updateStatus('', 'Error');
        this.addSystemMessage('Error: ' + message);
    }

    getLanguageName(code) {
        const names = {
            'en': 'English',
            'ta': 'Tamil',
            'hi': 'Hindi',
            'ml': 'Malayalam',
            'te': 'Telugu',
            'auto': 'Auto Detect'
        };
        return names[code] || code;
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    console.log('📄 DOM Content Loaded - Initializing VoiceChat...');
    try {
        new VoiceChat();
        console.log('✅ VoiceChat initialized successfully');
    } catch (error) {
        console.error('❌ Failed to initialize VoiceChat:', error);
        console.error('Stack:', error.stack);
    }
});
