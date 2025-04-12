/**
 * Emotion Detection System for VidyAI
 * Detects user's facial expressions and emotions during video playback
 */

class EmotionDetection {
    constructor(options = {}) {
        // Default options
        this.options = {
            confusionThreshold: 0.6,
            checkInterval: 1000,
            webcamElement: null,
            canvasElement: null,
            videoElement: null, // YouTube iframe for playback control
            statusCallback: null,
            onConfusion: null,
            confusionCallback: null,
            emotionCallback: null // New callback for emotion updates
        };
        
        // Override defaults with provided options
        Object.assign(this.options, options);
        
        // Initialize state
        this.isActive = false;
        this.isPaused = false;
        this.faceApiLoaded = false;
        this.checkTimer = null;
        this.confusionCounter = 0;
        
        // Initialize emotion data
        this.currentDominantEmotion = 'neutral';
        
        // Bind methods to this instance
        this.start = this.start.bind(this);
        this.stop = this.stop.bind(this);
        this.detectEmotion = this.detectEmotion.bind(this);
        this.processEmotions = this.processEmotions.bind(this);
        this.handleConfusion = this.handleConfusion.bind(this);
        this.reportEmotion = this.reportEmotion.bind(this);
    }
    
    async init() {
        try {
            // Log initialization start
            console.log('Starting emotion detection initialization...');
            
            // Load Face-API.js library from CDN dynamically
            await this.loadScripts([
                'https://cdn.jsdelivr.net/npm/face-api.js@0.22.2/dist/face-api.min.js'
            ]);
            
            console.log('Face-API loaded successfully');
            
            // Force the browser to show the webcam permission dialog immediately
            console.log('Triggering webcam permission dialog...');
            try {
                // This explicit call forces the permission dialog to appear
                const stream = await navigator.mediaDevices.getUserMedia({ 
                    audio: false, 
                    video: { 
                        width: { ideal: 320 },
                        height: { ideal: 240 }
                    } 
                });
                
                // If we reach here, permission was granted - close this temporary stream
                const tracks = stream.getTracks();
                tracks.forEach(track => track.stop());
                console.log('Webcam permission granted successfully');
            } catch (permErr) {
                console.error('Initial webcam permission check failed:', permErr);
                // Continue anyway - we'll try again in startWebcam
            }
            
            // Use GitHub Pages for reliable model hosting
            try {
                console.log('Loading face detection models from reliable source...');
                const modelUrl = 'https://justadudewhohacks.github.io/face-api.js/models';
                console.log('Using model URL:', modelUrl);
                
                console.log('Loading tiny face detector model...');
                await faceapi.nets.tinyFaceDetector.loadFromUri(modelUrl);
                console.log('Tiny face detector model loaded.');
                
                console.log('Loading face landmark model...');
                await faceapi.nets.faceLandmark68Net.loadFromUri(modelUrl);
                console.log('Face landmark model loaded.');
                
                console.log('Loading face expression model...');
                await faceapi.nets.faceExpressionNet.loadFromUri(modelUrl);
                console.log('Face expression model loaded.');
                
                console.log('All face detection models loaded successfully');
            } catch (modelErr) {
                console.error('Error loading face-api.js models:', modelErr);
                this.updateStatus('Error loading face models');
                throw new Error('Could not load face detection models. Please check your internet connection and try again.');
            }
            
            // Initialize webcam
            this.updateStatus('Initializing webcam...');
            await this.startWebcam();
            
            // Initialize detection
            this.updateStatus('Ready');
            this.faceApiLoaded = true;
            return true;
        } catch (error) {
            console.error('Emotion detection initialization error:', error);
            this.updateStatus('Initialization failed: ' + error.message);
            throw error;
        }
    }
    
    async loadScripts(urls) {
        const promises = urls.map(url => {
            return new Promise((resolve, reject) => {
                const script = document.createElement('script');
                script.src = url;
                script.onload = resolve;
                script.onerror = reject;
                document.head.appendChild(script);
            });
        });
        
        return Promise.all(promises);
    }
    
    updateStatus(message) {
        if (this.options.statusCallback) {
            this.options.statusCallback(message);
        }
        console.log('Emotion detection status:', message);
    }
    
    async startWebcam() {
        if (!this.options.webcamElement) return;
        
        try {
            // Check if navigator.mediaDevices is supported
            if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
                throw new Error('Browser does not support webcam access. Try using Chrome, Firefox, or Edge.');
            }
            
            console.log('Requesting webcam access...');
            this.updateStatus('Requesting webcam permission...');
            
            // Define constraints for better compatibility
            const constraints = { 
                audio: false,
                video: { 
                    width: { ideal: 320 },
                    height: { ideal: 240 },
                    facingMode: 'user'
                } 
            };
            
            // Try to get webcam access with timeout for better UX
            const timeoutPromise = new Promise((_, reject) => {
                setTimeout(() => reject(new Error('Permission request timed out')), 15000);
            });
            
            // Race the media request against a timeout
            const stream = await Promise.race([
                navigator.mediaDevices.getUserMedia(constraints),
                timeoutPromise
            ]);
            
            // Set the stream to the video element
            this.options.webcamElement.srcObject = stream;
            
            // Wait for the video to be ready
            return new Promise((resolve) => {
                this.options.webcamElement.onloadedmetadata = () => {
                    this.updateStatus('Webcam active');
                    console.log('Webcam initialized successfully');
                    resolve(true);
                };
            });
        } catch (error) {
            console.error('Webcam access error:', error);
            
            let errorMessage = 'Could not access webcam';
            
            // Provide more helpful error messages based on the error
            if (error.name === 'NotAllowedError' || error.name === 'PermissionDeniedError') {
                errorMessage = 'Camera permission denied. Please allow camera access in your browser settings.';
                // Force the browser to show its permission UI again
                if (typeof error.name !== 'undefined') {
                    // This is a hack to make Chrome re-ask for permission
                    navigator.mediaDevices.getUserMedia({ audio: true })
                        .then(audioStream => audioStream.getTracks().forEach(track => track.stop()))
                        .catch(() => {});
                }
            } else if (error.name === 'NotFoundError' || error.name === 'DevicesNotFoundError') {
                errorMessage = 'No camera found. Please connect a camera and try again.';
            } else if (error.name === 'NotReadableError' || error.name === 'TrackStartError') {
                errorMessage = 'Camera is in use by another application. Please close other apps using your camera.';
            } else if (error.name === 'OverconstrainedError') {
                errorMessage = 'Camera constraints cannot be satisfied. Try a different camera.';
            } else if (error.message === 'Permission request timed out') {
                errorMessage = 'Permission request timed out. Please check your browser notifications and allow camera access.';
            }
            
            this.updateStatus(errorMessage);
            throw new Error(errorMessage);
        }
    }
    
    stopWebcam() {
        if (!this.options.webcamElement || !this.options.webcamElement.srcObject) return;
        
        const tracks = this.options.webcamElement.srcObject.getTracks();
        tracks.forEach(track => track.stop());
        this.options.webcamElement.srcObject = null;
        this.updateStatus('Webcam stopped');
    }
    
    start() {
        if (this.isActive) return;
        
        console.log('Starting emotion detection');
        this.isActive = true;
        this.isPaused = false;
        
        // Start continuous detection
        this.detectEmotion();
        
        this.updateStatus('Emotion detection active');
    }
    
    stop() {
        if (!this.isActive) return;
        
        clearInterval(this.checkTimer);
        this.isActive = false;
        this.stopWebcam();
        
        this.updateStatus('Emotion detection stopped');
    }
    
    pause() {
        if (!this.isActive) return;
        this.isPaused = true;
        this.updateStatus('Emotion detection paused');
    }
    
    resume() {
        if (!this.isActive) return;
        this.isPaused = false;
        this.updateStatus('Emotion detection resumed');
    }
    
    async detectEmotion() {
        if (!this.isActive || !this.options.webcamElement || !this.options.canvasElement || !this.faceApiLoaded) {
            return;
        }
        
        try {
            const video = this.options.webcamElement;
            const canvas = this.options.canvasElement;
            const context = canvas.getContext('2d');
            
            // Ensure canvas dimensions match video
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            
            // Detect all faces with expressions
            const detections = await faceapi.detectAllFaces(
                video, 
                new faceapi.TinyFaceDetectorOptions({
                    inputSize: 224,
                    scoreThreshold: 0.5
                })
            ).withFaceLandmarks().withFaceExpressions();
            
            // Clear previous drawings
            context.clearRect(0, 0, canvas.width, canvas.height);
            
            if (detections && detections.length > 0) {
                // Draw detections if desired (optional)
                faceapi.draw.drawDetections(canvas, detections);
                faceapi.draw.drawFaceExpressions(canvas, detections, 0.05);
                
                // Get the first detected face's expressions
                const expressions = detections[0].expressions;
                console.log('Detected expressions:', expressions);
                
                // Process the detected emotions
                this.processEmotions(expressions);
                
                // Update status to show we're actively detecting
                this.updateStatus('Detecting emotions');
            } else {
                console.log('No face detected');
                this.updateStatus('No face detected');
                
                // Report neutral when no face is detected
                this.reportEmotion('neutral');
            }
        } catch (error) {
            console.error('Error detecting emotions:', error);
            this.updateStatus('Error in emotion detection');
        }
        
        // Continue detection loop if active
        if (this.isActive) {
            setTimeout(() => this.detectEmotion(), 1000);
        }
    }
    
    processEmotions(expressions) {
        // Store the expressions for reference
        this.lastExpressions = expressions;
        
        // Find the emotion with the highest value
        let highestValue = 0;
        let dominantEmotion = null;

        for (const [emotion, value] of Object.entries(expressions)) {
            if (value > highestValue) {
                highestValue = value;
                dominantEmotion = emotion;
            }
        }

        // Only update if we have a reasonably confident detection
        // or if it's a new dominant emotion
        if (highestValue > 0.3 && (dominantEmotion !== this.currentDominantEmotion || highestValue > 0.7)) {
            // Log strong emotions for debugging
            if (highestValue > 0.7) {
                console.log(`Strong emotion detected: ${dominantEmotion} (${highestValue.toFixed(2)})`);
            }

            this.currentDominantEmotion = dominantEmotion;
            
            // Report the detected emotion through the callback
            this.reportEmotion(dominantEmotion);

            // Check for confusion based on emotions other than happy and neutral
            if (dominantEmotion && dominantEmotion !== 'happy' && dominantEmotion !== 'neutral') {
                console.log(`Non-happy/neutral emotion detected: ${dominantEmotion} (${highestValue.toFixed(2)})`);
                
                // Increment confusion counter for emotions other than happy/neutral
                this.confusionCounter += 2;
                
                // If confusion counter is higher than threshold, trigger confusion
                if (this.confusionCounter > this.options.confusionThreshold) {
                    this.handleConfusion();
                    // Reset counter after triggering
                    this.confusionCounter = 0;
                }
            } else {
                // For happy or neutral emotions, gradually decrease confusion counter
                if (this.confusionCounter > 0) {
                    this.confusionCounter--;
                }
            }
        }
    }
    
    handleConfusion() {
        console.log("Confusion detected! Triggering callback...");
        
        // Pause the video if it exists
        if (this.options.videoElement) {
            try {
                console.log("Attempting to pause video via EmotionDetection...");
                
                // If videoElement is a YouTube player object
                if (typeof this.options.videoElement.pauseVideo === 'function') {
                    console.log("Using YouTube player API to pause");
                    this.options.videoElement.pauseVideo();
                } 
                // Otherwise use the helper function if it's an iframe
                else if (this.options.videoElement.tagName === 'IFRAME') {
                    console.log("Using pauseYouTubeVideo helper for iframe");
                    pauseYouTubeVideo(this.options.videoElement);
                }
            } catch (error) {
                console.error("Error pausing video:", error);
            }
        }
        
        // Call the confusion callback
        if (typeof this.options.confusionCallback === 'function') {
            console.log("Calling confusionCallback function");
            this.options.confusionCallback();
        } else if (typeof this.options.onConfusion === 'function') {
            console.log("Calling onConfusion function");
            this.options.onConfusion();
        } else {
            console.warn("No confusion callback function provided");
        }
    }
    
    // Report the current emotion through the callback
    reportEmotion(emotion) {
        // Call the emotion callback if provided
        if (typeof this.options.emotionCallback === 'function') {
            // Find the confidence value for this emotion
            const confidence = this.lastExpressions && this.lastExpressions[emotion] 
                ? this.lastExpressions[emotion] 
                : 0.5; // Default confidence if not available
            
            this.options.emotionCallback(emotion, confidence);
        }
    }
}

// Helper function to pause YouTube video
function pauseYouTubeVideo(iframe) {
    try {
        if (!iframe) {
            console.warn("No iframe provided to pauseYouTubeVideo");
            return;
        }
        
        console.log("Attempting to pause YouTube video...");
        // Try to pause using postMessage
        iframe.contentWindow.postMessage('{"event":"command","func":"pauseVideo","args":""}', '*');
        
        // Alternative method: try to access the player directly
        if (typeof iframe.contentWindow.pauseVideo === 'function') {
            iframe.contentWindow.pauseVideo();
        }
        
        console.log("YouTube pause command sent");
    } catch (error) {
        console.error("Error pausing YouTube video:", error);
    }
}

// Helper function to resume YouTube video
function resumeYouTubeVideo(iframe) {
    try {
        if (!iframe) {
            console.warn("No iframe provided to resumeYouTubeVideo");
            return;
        }
        
        console.log("Attempting to resume YouTube video...");
        // Try to play using postMessage
        iframe.contentWindow.postMessage('{"event":"command","func":"playVideo","args":""}', '*');
        
        // Alternative method: try to access the player directly
        if (typeof iframe.contentWindow.playVideo === 'function') {
            iframe.contentWindow.playVideo();
        }
        
        console.log("YouTube play command sent");
    } catch (error) {
        console.error("Error resuming YouTube video:", error);
    }
} 