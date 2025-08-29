/**
 * VocalCart Audio Tutorial System
 * This script provides a comprehensive audio guide for blind users
 * to understand how to use the VocalCart application
 */

class AudioTutorial {
    constructor() {
        this.audioContext = null;
        this.tutorialActive = false;
        this.currentStep = 0;
        this.audioQueue = [];
        this.isSpeaking = false;
        this.synthesis = window.speechSynthesis;
        this.voicePreference = null;
        
        // Define tutorial script with pauses and emphasis
        this.tutorialScript = this.buildTutorialScript();
        
        // Initialize
        this.initAudioContext();
        this.setupVoicePreference();
        this.createTutorialControls();
    }
    
    /**
     * Build the complete tutorial script with all steps
     */
    buildTutorialScript() {
        return [
            // Welcome message
            {
                text: "Welcome to the VocalCart audio tutorial for blind and visually impaired users. I'm going to guide you through using this voice-powered shopping assistant specifically designed for screen reader users.",
                pause: 1000
            },
            // Introduction to the interface
            {
                text: "VocalCart is a shopping assistant that lets you search for products, navigate results, and manage your shopping cart completely by voice. The interface has been optimized for screen readers and keyboard navigation.",
                pause: 1500
            },
            // Starting voice input
            {
                text: "To activate voice commands at any time, press Control plus Space on your keyboard. You will hear a sound indicating that the system is listening. To stop listening mode, press the Escape key.",
                pause: 1500
            },
            // Navigation commands
            {
                text: "The most important commands for navigation are: Next, Previous, and Repeat. Say 'next' to move to the next product. Say 'previous' to move to the previous product. Say 'repeat' to hear the current product again. You can also press the Spacebar key to go to the next product.",
                pause: 1500
            },
            // Search commands
            {
                text: "To search for products, say 'search for' followed by what you're looking for. For example, 'search for shoes under 2000' or 'find smartphones'. The system will search and announce the number of products found.",
                pause: 1500
            },
            // Getting product details 
            {
                text: "To hear detailed information about a product, say 'tell me about item' followed by the number. For example, 'tell me about item 2'. This will provide comprehensive details about that product.",
                pause: 1500
            },
            // Cart management
            {
                text: "To add an item to your shopping cart, say 'add item' followed by the number. For example, 'add item 3 to cart'. The system will confirm when the item has been added. To check what's in your cart, say 'show my cart' or 'view cart'. To remove items, say 'remove item' followed by the number.",
                pause: 1500
            },
            // Checkout process
            {
                text: "When you're ready to complete your purchase, simply say 'checkout'. The system will guide you through the checkout process and confirm your order.",
                pause: 1500
            },
            // Keyboard shortcuts
            {
                text: "VocalCart also offers keyboard shortcuts for accessibility. Press Control+Space to start voice input. Press Escape to cancel. Press the Spacebar alone to move to the next product. Press Shift+Tab to navigate backwards through page elements.",
                pause: 1500
            },
            // Getting help
            {
                text: "If you need assistance at any time, say 'help' or 'what can I say' for a list of available commands. You can also access this tutorial again by saying 'start tutorial'.",
                pause: 1500
            },
            // Common issues
            {
                text: "If the system doesn't hear you clearly, try moving closer to your microphone or speaking more slowly and distinctly. If you're in a noisy environment, you can also type commands in the text input box and press Enter.",
                pause: 1500
            },
            // Practice exercise
            {
                text: "Let's practice with a simple exercise. Try these steps: First, search for a product by saying 'search for shirts'. Then, navigate using 'next' and 'previous'. Finally, add an item to your cart by saying 'add item 1 to cart'.",
                pause: 2000
            },
            // Tutorial closing
            {
                text: "This concludes the VocalCart audio tutorial. To restart this tutorial at any time, press the Audio Tutorial button in the bottom left corner of the page, or say 'restart tutorial'. Happy shopping!",
                pause: 1000
            }
        ];
    }
    
    /**
     * Initialize audio context for sound effects
     */
    initAudioContext() {
        try {
            // Fix for browsers that require user interaction
            const resumeAudio = () => {
                if (this.audioContext && this.audioContext.state === 'suspended') {
                    this.audioContext.resume();
                }
                document.removeEventListener('click', resumeAudio);
            };
            
            // Create audio context
            window.AudioContext = window.AudioContext || window.webkitAudioContext;
            this.audioContext = new AudioContext();
            
            // Add listener to resume audio context after user interaction
            document.addEventListener('click', resumeAudio);
            
        } catch (e) {
            console.warn('Web Audio API not supported:', e);
        }
    }
    
    /**
     * Setup preferred voice for speech synthesis
     */
    setupVoicePreference() {
        // Wait for voices to load
        const loadVoices = () => {
            const voices = this.synthesis.getVoices();
            
            if (voices.length > 0) {
                // Prefer voice for screen reader users
                this.voicePreference = 
                    // Try to find screen reader friendly voice
                    voices.find(voice => voice.name.includes('Screen Reader') || voice.name.includes('NVDA')) || 
                    // Fallback to English
                    voices.find(voice => voice.lang === 'en-US' || voice.lang === 'en-GB') ||
                    // Default to first available voice
                    voices[0];
                    
                console.log('Selected tutorial voice:', this.voicePreference.name);
            }
        };
        
        // Check if voices already loaded
        if (this.synthesis.getVoices().length) {
            loadVoices();
        } else {
            // Wait for voices to load
            this.synthesis.onvoiceschanged = loadVoices;
        }
    }
    
    /**
     * Create and add tutorial controls to the page
     */
    createTutorialControls() {
        // Tutorial button removed - we'll access the tutorial through keyboard shortcuts only
        // The tutorial can still be started via Alt+T keyboard shortcut
        // or through the auto-start feature for screen reader users
        
        // Creating a hidden accessible element to announce tutorial availability
        const srAnnouncer = document.getElementById('sr-announcements');
        if (srAnnouncer) {
            setTimeout(() => {
                srAnnouncer.textContent = 'Audio tutorial is available. Press Alt+T to start the tutorial.';
            }, 2000);
        }
    }
    
    /**
     * Start the audio tutorial
     */
    startTutorial() {
        // Check if tutorial is already active
        if (this.tutorialActive) {
            this.stopTutorial();
            return;
        }
        
        // Check if there's an existing welcome modal or tutorial overlay
        const existingWelcomeModal = document.querySelector('.auto-tutorial-modal');
        const existingTutorialOverlay = document.getElementById('audio-tutorial-overlay');
        
        // If either exists, remove them first
        if (existingWelcomeModal) {
            existingWelcomeModal.remove();
            const backdrop = document.querySelector('.auto-tutorial-backdrop');
            if (backdrop) backdrop.remove();
        }
        
        if (existingTutorialOverlay) {
            existingTutorialOverlay.remove();
            const backdrop = document.getElementById('audio-tutorial-backdrop');
            if (backdrop) backdrop.remove();
        }
        
        // Set global flag that tutorial has started
        window.tutorialHasStarted = true;
        
        this.tutorialActive = true;
        this.currentStep = 0;
        this.playTutorialSound('start');
        
        // Create tutorial controls overlay
        this.createTutorialOverlay();
        
        // Start speaking the first part after a short delay
        setTimeout(() => {
            this.speakCurrentStep();
        }, 500);
    }
    
    /**
     * Stop the current tutorial
     */
    stopTutorial() {
        this.tutorialActive = false;
        this.synthesis.cancel(); // Stop any current speech
        this.playTutorialSound('stop');
        
        // Remove overlay
        const overlay = document.getElementById('audio-tutorial-overlay');
        if (overlay) {
            overlay.remove();
        }
        
        // Remove backdrop
        const backdrop = document.getElementById('audio-tutorial-backdrop');
        if (backdrop) {
            backdrop.remove();
        }
        
        // Announce tutorial stopped
        this.announceToScreenReader('Audio tutorial stopped.');
    }
    
    /**
     * Create overlay with controls for the tutorial
     */
    createTutorialOverlay() {
        // Remove existing overlay if present
        const existingOverlay = document.getElementById('audio-tutorial-overlay');
        if (existingOverlay) {
            existingOverlay.remove();
        }
        
        // Create overlay
        const overlay = document.createElement('div');
        overlay.id = 'audio-tutorial-overlay';
        overlay.setAttribute('role', 'dialog');
        overlay.setAttribute('aria-label', 'Audio Tutorial Controls');
        
        // Style the overlay - centered with improved styling
        overlay.style.position = 'fixed';
        overlay.style.top = '50%';  // Center vertically
        overlay.style.left = '50%';
        overlay.style.transform = 'translate(-50%, -50%)';  // Center both vertically and horizontally
        overlay.style.backgroundColor = 'rgba(0,0,0,0.85)';
        overlay.style.color = 'white';
        overlay.style.padding = '25px 35px';
        overlay.style.borderRadius = '15px';
        overlay.style.zIndex = '10000';
        overlay.style.boxShadow = '0 5px 35px rgba(0,0,0,0.5)';
        overlay.style.width = '80%';
        overlay.style.maxWidth = '600px';
        overlay.style.textAlign = 'center';  // Center text content
        
        // Add controls to overlay with improved layout
        overlay.innerHTML = `
            <div style="font-weight: bold; margin-bottom: 20px; font-size: 1.2em;">
                Audio Tutorial: Step ${this.currentStep + 1} of ${this.tutorialScript.length}
            </div>
            <div style="margin-bottom: 25px;">
                <p style="margin-bottom: 15px; line-height: 1.5; font-size: 1.1em;">
                    "${this.tutorialScript[this.currentStep]?.text || ''}"
                </p>
            </div>
            <div style="display: flex; justify-content: center; gap: 15px; flex-wrap: wrap;">
                <button id="tutorial-prev" aria-label="Previous tutorial step" style="min-width: 100px;">
                    ◀ Previous
                </button>
                <button id="tutorial-pause" aria-label="Pause or resume tutorial" style="min-width: 100px;">
                    ⏸️ Pause
                </button>
                <button id="tutorial-next" aria-label="Next tutorial step" style="min-width: 100px;">
                    Next ▶
                </button>
                <button id="tutorial-stop" aria-label="Stop tutorial" style="min-width: 100px;">
                    ✖️ Stop
                </button>
            </div>
            <div style="margin-top: 25px; font-size: 0.9em; opacity: 0.8;">
                Press <kbd>Alt</kbd>+<kbd>T</kbd> anytime to restart tutorial or <kbd>Esc</kbd> to close
            </div>
        `;
        
        // Create semi-transparent backdrop
        const backdrop = document.createElement('div');
        backdrop.id = 'audio-tutorial-backdrop';
        backdrop.style.position = 'fixed';
        backdrop.style.top = '0';
        backdrop.style.left = '0';
        backdrop.style.width = '100%';
        backdrop.style.height = '100%';
        backdrop.style.backgroundColor = 'rgba(0,0,0,0.6)';
        backdrop.style.zIndex = '9999';
        document.body.appendChild(backdrop);
        
        // Style buttons
        const buttons = overlay.querySelectorAll('button');
        buttons.forEach(button => {
            button.style.backgroundColor = 'rgba(255,255,255,0.2)';
            button.style.border = 'none';
            button.style.borderRadius = '8px';
            button.style.color = 'white';
            button.style.padding = '12px 18px';
            button.style.cursor = 'pointer';
            button.style.fontSize = '1em';
            button.style.fontWeight = 'bold';
            button.style.transition = 'all 0.2s ease';
            
            // Add hover effect
            button.addEventListener('mouseenter', () => {
                button.style.backgroundColor = 'rgba(255,255,255,0.35)';
                button.style.transform = 'translateY(-2px)';
            });
            
            button.addEventListener('mouseleave', () => {
                button.style.backgroundColor = 'rgba(255,255,255,0.2)';
                button.style.transform = 'translateY(0)';
            });
            
            // Add focus styles for accessibility
            button.addEventListener('focus', () => {
                button.style.outline = '3px solid white';
                button.style.outlineOffset = '2px';
            });
            
            button.addEventListener('blur', () => {
                button.style.outline = 'none';
            });
        });
        
        // Add event listeners
        overlay.querySelector('#tutorial-prev').addEventListener('click', () => this.previousStep());
        overlay.querySelector('#tutorial-next').addEventListener('click', () => this.nextStep());
        overlay.querySelector('#tutorial-pause').addEventListener('click', (e) => {
            if (this.synthesis.paused) {
                this.synthesis.resume();
                e.target.innerHTML = '⏸️ Pause';
                this.announceToScreenReader('Tutorial resumed');
            } else if (this.synthesis.speaking) {
                this.synthesis.pause();
                e.target.innerHTML = '▶️ Resume';
                this.announceToScreenReader('Tutorial paused');
            } else {
                this.speakCurrentStep();
                e.target.innerHTML = '⏸️ Pause';
            }
        });
        overlay.querySelector('#tutorial-stop').addEventListener('click', () => this.stopTutorial());
        
        // Close on ESC key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && document.getElementById('audio-tutorial-overlay')) {
                this.stopTutorial();
            }
        });
        
        // Add to page
        document.body.appendChild(overlay);
        
        // Announce to screen readers
        this.announceToScreenReader('Audio tutorial started. Use the controls to navigate between steps.');
    }
    
    /**
     * Speak the current tutorial step with enhanced screen reader support
     */
    speakCurrentStep() {
        if (!this.tutorialActive || this.currentStep >= this.tutorialScript.length) {
            return;
        }
        
        const step = this.tutorialScript[this.currentStep];
        
        // Update overlay step counter
        const overlay = document.getElementById('audio-tutorial-overlay');
        if (overlay) {
            const counter = overlay.querySelector('div');
            if (counter) {
                counter.textContent = `Audio Tutorial: Step ${this.currentStep + 1} of ${this.tutorialScript.length}`;
            }
        }
        
        // Cancel any current speech
        this.synthesis.cancel();
        
        // Create and configure utterance
        const utterance = new SpeechSynthesisUtterance(step.text);
        
        // Set preferred voice if available
        if (this.voicePreference) {
            utterance.voice = this.voicePreference;
        }
        
        // Set properties for clear speech
        utterance.rate = 0.9;  // Slightly slower for clarity
        utterance.pitch = 1.0;
        utterance.volume = 1.0;
        
        // Handle utterance events
        utterance.onend = () => {
            console.log('Finished speaking tutorial step:', this.currentStep + 1);
            
            // If this is the last step, stop the tutorial after a delay
            if (this.currentStep === this.tutorialScript.length - 1) {
                setTimeout(() => {
                    this.stopTutorial();
                }, step.pause || 2000);
            }
        };
        
        // Speak the text
        this.synthesis.speak(utterance);
        
        // Also update screen reader announcement
        this.announceToScreenReader(`Tutorial step ${this.currentStep + 1}: ${step.text}`);
    }
    
    /**
     * Go to the next tutorial step
     */
    nextStep() {
        if (this.currentStep < this.tutorialScript.length - 1) {
            this.currentStep++;
            this.playTutorialSound('next');
            this.speakCurrentStep();
        } else {
            // At the last step
            this.playTutorialSound('error');
            this.announceToScreenReader('This is the last step of the tutorial.');
        }
    }
    
    /**
     * Go to the previous tutorial step
     */
    previousStep() {
        if (this.currentStep > 0) {
            this.currentStep--;
            this.playTutorialSound('previous');
            this.speakCurrentStep();
        } else {
            // At the first step
            this.playTutorialSound('error');
            this.announceToScreenReader('This is the first step of the tutorial.');
        }
    }
    
    /**
     * Play sound effects for tutorial navigation
     * @param {string} soundType - Type of sound to play
     */
    playTutorialSound(soundType) {
        if (!this.audioContext) return;
        
        try {
            const oscillator = this.audioContext.createOscillator();
            const gain = this.audioContext.createGain();
            
            oscillator.connect(gain);
            gain.connect(this.audioContext.destination);
            
            // Configure sound based on type
            switch(soundType) {
                case 'start':
                    oscillator.type = 'sine';
                    oscillator.frequency.setValueAtTime(440, this.audioContext.currentTime); // A4
                    oscillator.frequency.setValueAtTime(523.25, this.audioContext.currentTime + 0.2); // C5
                    gain.gain.setValueAtTime(0.1, this.audioContext.currentTime);
                    gain.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + 0.5);
                    oscillator.start();
                    oscillator.stop(this.audioContext.currentTime + 0.5);
                    break;
                    
                case 'stop':
                    oscillator.type = 'sine';
                    oscillator.frequency.setValueAtTime(523.25, this.audioContext.currentTime); // C5
                    oscillator.frequency.setValueAtTime(440, this.audioContext.currentTime + 0.2); // A4
                    gain.gain.setValueAtTime(0.1, this.audioContext.currentTime);
                    gain.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + 0.5);
                    oscillator.start();
                    oscillator.stop(this.audioContext.currentTime + 0.5);
                    break;
                    
                case 'next':
                    oscillator.type = 'sine';
                    oscillator.frequency.setValueAtTime(440, this.audioContext.currentTime); // A4
                    oscillator.frequency.setValueAtTime(493.88, this.audioContext.currentTime + 0.1); // B4
                    gain.gain.setValueAtTime(0.05, this.audioContext.currentTime);
                    gain.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + 0.2);
                    oscillator.start();
                    oscillator.stop(this.audioContext.currentTime + 0.2);
                    break;
                    
                case 'previous':
                    oscillator.type = 'sine';
                    oscillator.frequency.setValueAtTime(493.88, this.audioContext.currentTime); // B4
                    oscillator.frequency.setValueAtTime(440, this.audioContext.currentTime + 0.1); // A4
                    gain.gain.setValueAtTime(0.05, this.audioContext.currentTime);
                    gain.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + 0.2);
                    oscillator.start();
                    oscillator.stop(this.audioContext.currentTime + 0.2);
                    break;
                    
                case 'error':
                    oscillator.type = 'triangle';
                    oscillator.frequency.setValueAtTime(200, this.audioContext.currentTime);
                    gain.gain.setValueAtTime(0.05, this.audioContext.currentTime);
                    gain.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + 0.3);
                    oscillator.start();
                    oscillator.stop(this.audioContext.currentTime + 0.3);
                    break;
            }
        } catch (e) {
            console.warn('Error playing tutorial sound:', e);
        }
    }
    
    /**
     * Make an announcement to screen readers
     * @param {string} text - Text to announce
     */
    announceToScreenReader(text) {
        let srAnnouncer = document.getElementById('sr-announcements');
        
        if (!srAnnouncer) {
            srAnnouncer = document.createElement('div');
            srAnnouncer.id = 'sr-announcements';
            srAnnouncer.setAttribute('aria-live', 'assertive');
            srAnnouncer.setAttribute('aria-atomic', 'true');
            srAnnouncer.classList.add('sr-only');
            document.body.appendChild(srAnnouncer);
        }
        
        // Clear previous content and set new content
        srAnnouncer.textContent = '';
        setTimeout(() => {
            srAnnouncer.textContent = text;
        }, 50);
    }
    
    /**
     * Special blind user focused instructions with extra details
     * This ensures blind users get comprehensive guidance
     */
    provideBlindUserGuidance() {
        // Create specialized region for screen reader guidance
        let blindGuidanceRegion = document.getElementById('blind-user-guidance');
        
        if (!blindGuidanceRegion) {
            blindGuidanceRegion = document.createElement('div');
            blindGuidanceRegion.id = 'blind-user-guidance';
            blindGuidanceRegion.setAttribute('aria-live', 'polite');
            blindGuidanceRegion.setAttribute('role', 'status');
            blindGuidanceRegion.classList.add('sr-only');
            document.body.appendChild(blindGuidanceRegion);
        }
        
        // Detailed guidance for blind users that only screen readers will read
        const guidance = `
            VocalCart has been designed specifically for blind users.
            To navigate through the application:
            1. Press Control plus Space to activate voice commands.
            2. Say "search for" followed by a product name to search.
            3. Use commands like "next", "previous", or "repeat" to navigate through products.
            4. Say "add to cart" to add the current product to your cart.
            5. Say "checkout" when you're ready to complete your purchase.
            6. Press Alt+T at any time to restart this tutorial.
            7. Press Tab to navigate through interactive elements on the page.
            
            VocalCart ensures all products are read aloud with their names, prices, and descriptions.
        `;
        
        // Set the guidance text
        blindGuidanceRegion.textContent = guidance;
        
        // After main guidance, provide immediate action suggestions
        setTimeout(() => {
            blindGuidanceRegion.textContent = "To begin, try saying 'search for shirts' after pressing Control plus Space.";
        }, 15000);
    }
}

// Initialize when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Create the audio tutorial instance
    window.audioTutorial = new AudioTutorial();
    
    // Set a flag to track if tutorial has been started by any script
    window.tutorialHasStarted = false;
    
    // REMOVED: Auto-start functionality has been moved to auto-start-tutorial.js
    // This prevents both scripts from starting the tutorial simultaneously
    
    // Listen for voice commands or keyboard shortcuts to start/restart the tutorial
    document.addEventListener('keydown', (e) => {
        // Alt+T to trigger audio tutorial
        if (e.altKey && e.code === 'KeyT') {
            e.preventDefault();
            window.audioTutorial.startTutorial();
        }
    });
});

// Create welcome modal for blind users
function createWelcomeModal() {
    // Create modal backdrop
    const backdrop = document.createElement('div');
    backdrop.className = 'auto-tutorial-backdrop';
    backdrop.style.position = 'fixed';
    backdrop.style.top = '0';
    backdrop.style.left = '0';
    backdrop.style.width = '100%';
    backdrop.style.height = '100%';
    backdrop.style.backgroundColor = 'rgba(0,0,0,0.7)';
    backdrop.style.zIndex = '9999';
    document.body.appendChild(backdrop);
    
    // Create modal dialog
    const modal = document.createElement('div');
    modal.className = 'auto-tutorial-modal';
    modal.setAttribute('role', 'dialog');
    modal.setAttribute('aria-modal', 'true');
    modal.setAttribute('aria-labelledby', 'welcome-title');
    
    // Style the modal - centered with improved styling
    modal.style.position = 'fixed';
    modal.style.top = '50%';
    modal.style.left = '50%';
    modal.style.transform = 'translate(-50%, -50%)';
    modal.style.backgroundColor = 'rgba(255,255,255,0.95)';
    modal.style.borderRadius = '15px';
    modal.style.padding = '30px';
    modal.style.width = '90%';
    modal.style.maxWidth = '500px';
    modal.style.boxShadow = '0 15px 50px rgba(0,0,0,0.3)';
    modal.style.zIndex = '10000';
    modal.style.textAlign = 'center';
    
    modal.innerHTML = `
        <div class="auto-tutorial-content">
            <div class="auto-tutorial-header" style="margin-bottom: 20px;">
                <h2 id="welcome-title" style="font-size: 1.8em; color: #667eea; margin-bottom: 10px;">Welcome to VocalCart</h2>
                <p style="font-size: 1.2em; color: #555;">Audio assistance for blind and visually impaired users</p>
            </div>
            <div class="auto-tutorial-body" style="margin-bottom: 30px; line-height: 1.6;">
                <p style="margin-bottom: 15px;">VocalCart is starting an audio tutorial to help you navigate this shopping experience using voice commands.</p>
                <p style="margin-bottom: 15px;">You will hear instructions on how to use voice commands to search for products, navigate results, add items to your cart, and checkout.</p>
                <p>Press Alt+T anytime to restart this tutorial.</p>
            </div>
            <div class="auto-tutorial-controls" style="display: flex; justify-content: center; gap: 20px;">
                <button class="auto-tutorial-btn secondary" id="skip-tutorial-btn" style="padding: 12px 25px; border-radius: 8px; border: 2px solid #667eea; background: transparent; color: #667eea; font-weight: bold; font-size: 1em; cursor: pointer; transition: all 0.2s ease;">Skip Tutorial</button>
                <button class="auto-tutorial-btn primary" id="start-tutorial-btn" autofocus style="padding: 12px 25px; border-radius: 8px; border: none; background: linear-gradient(135deg, #667eea, #764ba2); color: white; font-weight: bold; font-size: 1em; cursor: pointer; transition: all 0.2s ease;">Start Tutorial</button>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Set focus to the start button
    setTimeout(() => {
        document.getElementById('start-tutorial-btn').focus();
    }, 100);
    
    // Add hover effects to buttons
    const startBtn = document.getElementById('start-tutorial-btn');
    const skipBtn = document.getElementById('skip-tutorial-btn');
    
    startBtn.addEventListener('mouseenter', () => {
        startBtn.style.transform = 'translateY(-2px)';
        startBtn.style.boxShadow = '0 8px 20px rgba(102, 126, 234, 0.4)';
    });
    
    startBtn.addEventListener('mouseleave', () => {
        startBtn.style.transform = 'translateY(0)';
        startBtn.style.boxShadow = 'none';
    });
    
    skipBtn.addEventListener('mouseenter', () => {
        skipBtn.style.backgroundColor = 'rgba(102, 126, 234, 0.1)';
    });
    
    skipBtn.addEventListener('mouseleave', () => {
        skipBtn.style.backgroundColor = 'transparent';
    });
    
    // Function to close the modal
    const closeModal = (wasSkipped = false) => {
        modal.remove();
        const backdrop = document.querySelector('.auto-tutorial-backdrop');
        if (backdrop) backdrop.remove();
        
        // Announce the appropriate message
        const announcer = document.getElementById('sr-announcements');
        if (announcer) {
            if (wasSkipped) {
                announcer.textContent = 'Tutorial skipped. Press Alt+T anytime to start the tutorial.';
            } else {
                announcer.textContent = 'Tutorial dismissed. Press Alt+T anytime to start the tutorial.';
            }
        }
    };
    
    // Add event listeners
    startBtn.addEventListener('click', () => {
        closeModal();
        window.audioTutorial.startTutorial();
    });
    
    skipBtn.addEventListener('click', () => {
        closeModal(true);
    });
    
    // Close on escape key
    document.addEventListener('keydown', function escHandler(e) {
        if (e.key === 'Escape') {
            closeModal(true);
            document.removeEventListener('keydown', escHandler);
        }
    });
}
