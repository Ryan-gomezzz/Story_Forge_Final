/**
 * Audio Recording functionality for StoryForge AI
 * Supports live recording, file upload, and real-time transcription
 */

class AudioRecorder {
    constructor() {
        this.mediaRecorder = null;
        this.audioStream = null;
        this.audioChunks = [];
        this.isRecording = false;
        this.recordingStartTime = null;
        this.audioContext = null;
        this.analyser = null;
        this.animationId = null;

        this.initializeElements();
        this.setupEventListeners();
    }

    initializeElements() {
        this.recordBtn = document.getElementById('recordBtn');
        this.stopBtn = document.getElementById('stopBtn');
        this.playBtn = document.getElementById('playBtn');
        this.recordingTime = document.getElementById('recordingTime');
        this.recordingStatus = document.getElementById('recordingStatus');
        this.recordedAudio = document.getElementById('recordedAudio');
        this.audioCanvas = document.getElementById('audioCanvas');
        this.audioFile = document.getElementById('audioFile');
        this.transcriptionPreview = document.getElementById('transcriptionPreview');
        this.transcribedText = document.getElementById('transcribedText');

        if (this.audioCanvas) {
            this.canvasCtx = this.audioCanvas.getContext('2d');
        }
    }

    setupEventListeners() {
        if (this.recordBtn) {
            this.recordBtn.addEventListener('click', () => this.startRecording());
        }

        if (this.stopBtn) {
            this.stopBtn.addEventListener('click', () => this.stopRecording());
        }

        if (this.playBtn) {
            this.playBtn.addEventListener('click', () => this.playRecording());
        }

        if (this.audioFile) {
            this.audioFile.addEventListener('change', (e) => this.handleFileUpload(e));
        }
    }

    async startRecording() {
        try {
            // Request microphone access
            this.audioStream = await navigator.mediaDevices.getUserMedia({ 
                audio: {
                    echoCancellation: true,
                    noiseSuppression: true,
                    sampleRate: 44100
                } 
            });

            // Setup audio context for visualization
            this.setupAudioVisualization();

            // Setup MediaRecorder
            this.mediaRecorder = new MediaRecorder(this.audioStream, {
                mimeType: 'audio/webm;codecs=opus'
            });

            this.audioChunks = [];
            this.recordingStartTime = Date.now();

            this.mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    this.audioChunks.push(event.data);
                }
            };

            this.mediaRecorder.onstop = () => {
                this.createAudioBlob();
            };

            // Start recording
            this.mediaRecorder.start(100); // Collect data every 100ms
            this.isRecording = true;

            // Update UI
            this.updateRecordingUI(true);
            this.startTimer();
            this.startVisualization();

        } catch (error) {
            console.error('Error starting recording:', error);
            this.updateStatus('Microphone access denied', 'error');
        }
    }

    stopRecording() {
        if (this.mediaRecorder && this.isRecording) {
            this.mediaRecorder.stop();
            this.isRecording = false;

            // Stop audio stream
            if (this.audioStream) {
                this.audioStream.getTracks().forEach(track => track.stop());
            }

            // Update UI
            this.updateRecordingUI(false);
            this.stopTimer();
            this.stopVisualization();
        }
    }

    setupAudioVisualization() {
        if (!this.audioStream || !this.audioCanvas) return;

        this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
        this.analyser = this.audioContext.createAnalyser();
        const source = this.audioContext.createMediaStreamSource(this.audioStream);

        source.connect(this.analyser);
        this.analyser.fftSize = 256;
    }

    startVisualization() {
        if (!this.analyser || !this.canvasCtx) return;

        const bufferLength = this.analyser.frequencyBinCount;
        const dataArray = new Uint8Array(bufferLength);

        const draw = () => {
            if (!this.isRecording) return;

            this.animationId = requestAnimationFrame(draw);

            this.analyser.getByteFrequencyData(dataArray);

            this.canvasCtx.fillStyle = 'rgba(0, 0, 0, 0.1)';
            this.canvasCtx.fillRect(0, 0, this.audioCanvas.width, this.audioCanvas.height);

            const barWidth = (this.audioCanvas.width / bufferLength) * 2.5;
            let barHeight;
            let x = 0;

            for (let i = 0; i < bufferLength; i++) {
                barHeight = (dataArray[i] / 255) * this.audioCanvas.height;

                const r = 102 + (barHeight / this.audioCanvas.height) * 100;
                const g = 126 + (barHeight / this.audioCanvas.height) * 100;
                const b = 234;

                this.canvasCtx.fillStyle = `rgb(${r},${g},${b})`;
                this.canvasCtx.fillRect(x, this.audioCanvas.height - barHeight, barWidth, barHeight);

                x += barWidth + 1;
            }
        };

        draw();
    }

    stopVisualization() {
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
        }

        if (this.canvasCtx && this.audioCanvas) {
            this.canvasCtx.clearRect(0, 0, this.audioCanvas.width, this.audioCanvas.height);
        }
    }

    createAudioBlob() {
        const blob = new Blob(this.audioChunks, { type: 'audio/webm' });
        const url = URL.createObjectURL(blob);

        // Setup audio element
        if (this.recordedAudio) {
            this.recordedAudio.src = url;
            this.recordedAudio.style.display = 'block';
            this.playBtn.disabled = false;
        }

        // Auto-transcribe if available
        this.transcribeAudio(blob);
    }

    async transcribeAudio(audioBlob) {
        try {
            this.updateStatus('Transcribing audio...', 'processing');

            const formData = new FormData();
            formData.append('audio', audioBlob, 'recording.webm');

            const response = await fetch('/api/transcribe/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': this.getCSRFToken()
                }
            });

            if (response.ok) {
                const result = await response.json();
                this.displayTranscription(result.text);
                this.updateStatus('Audio transcribed successfully', 'success');
            } else {
                const error = await response.json();
                this.updateStatus(`Transcription failed: ${error.error}`, 'error');
            }

        } catch (error) {
            console.error('Transcription error:', error);
            this.updateStatus('Transcription service unavailable', 'error');
        }
    }

    async handleFileUpload(event) {
        const file = event.target.files[0];
        if (!file) return;

        // Validate file
        if (file.size > 10 * 1024 * 1024) { // 10MB limit
            this.updateStatus('File too large (max 10MB)', 'error');
            return;
        }

        const allowedTypes = ['audio/wav', 'audio/mp3', 'audio/mp4', 'audio/mpeg', 'audio/flac', 'audio/ogg'];
        if (!allowedTypes.some(type => file.type.startsWith(type.split('/')[0]))) {
            this.updateStatus('Unsupported file format', 'error');
            return;
        }

        // Preview audio
        const url = URL.createObjectURL(file);
        if (this.recordedAudio) {
            this.recordedAudio.src = url;
            this.recordedAudio.style.display = 'block';
            this.playBtn.disabled = false;
        }

        // Auto-transcribe uploaded file
        this.transcribeAudio(file);
    }

    playRecording() {
        if (this.recordedAudio) {
            this.recordedAudio.play();
        }
    }

    displayTranscription(text) {
        if (this.transcribedText && this.transcriptionPreview) {
            this.transcribedText.textContent = text;
            this.transcriptionPreview.style.display = 'block';

            // Also populate the main prompt textarea if empty
            const promptTextarea = document.getElementById('prompt');
            if (promptTextarea && !promptTextarea.value.trim()) {
                promptTextarea.value = text;
                // Trigger input event for character counter
                promptTextarea.dispatchEvent(new Event('input'));
            }
        }
    }

    updateRecordingUI(recording) {
        if (recording) {
            this.recordBtn.disabled = true;
            this.recordBtn.innerHTML = '<i class="bi bi-mic-fill"></i> Recording...';
            this.recordBtn.classList.add('btn-danger');
            this.recordBtn.classList.remove('btn-outline-danger');

            this.stopBtn.disabled = false;
            this.playBtn.disabled = true;
        } else {
            this.recordBtn.disabled = false;
            this.recordBtn.innerHTML = '<i class="bi bi-mic"></i> Start Recording';
            this.recordBtn.classList.remove('btn-danger');
            this.recordBtn.classList.add('btn-outline-danger');

            this.stopBtn.disabled = true;
        }
    }

    startTimer() {
        const updateTimer = () => {
            if (!this.isRecording) return;

            const elapsed = Math.floor((Date.now() - this.recordingStartTime) / 1000);
            const minutes = Math.floor(elapsed / 60);
            const seconds = elapsed % 60;

            if (this.recordingTime) {
                this.recordingTime.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
            }

            setTimeout(updateTimer, 1000);
        };

        updateTimer();
    }

    stopTimer() {
        // Timer stops automatically when isRecording becomes false
    }

    updateStatus(message, type = 'info') {
        if (this.recordingStatus) {
            this.recordingStatus.textContent = message;
            this.recordingStatus.className = `small text-${this.getStatusClass(type)} mt-1`;
        }
    }

    getStatusClass(type) {
        switch (type) {
            case 'success': return 'success';
            case 'error': return 'danger';
            case 'processing': return 'warning';
            default: return 'muted';
        }
    }

    getCSRFToken() {
        const token = document.querySelector('[name=csrfmiddlewaretoken]');
        return token ? token.value : '';
    }
}

// Initialize audio recorder when DOM is loaded
function initializeAudioRecording() {
    if (typeof window !== 'undefined' && 'MediaRecorder' in window) {
        window.audioRecorder = new AudioRecorder();
    } else {
        console.warn('MediaRecorder not supported in this browser');

        // Hide audio controls if not supported
        const audioSection = document.getElementById('audioInputSection');
        if (audioSection) {
            const warning = document.createElement('div');
            warning.className = 'alert alert-warning';
            warning.innerHTML = '<i class="bi bi-exclamation-triangle me-2"></i>Audio recording not supported in this browser. Please use file upload instead.';
            audioSection.appendChild(warning);
        }
    }
}

// Export for use in templates
window.initializeAudioRecording = initializeAudioRecording;
