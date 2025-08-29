/**
 * VocalCart Accessibility Tutorial 
 * Interactive voice-guided tutorial for screen reader and blind users
 */

class VoiceAccessibilityTutorial {
    constructor() {
        // Core properties
        this.synthesis = window.speechSynthesis;
        this.tutorialActive = false;
        this.currentStep = 0;
        this.tutorialSteps = [];
        this.isListening = false;
        this.recognition = null;
        this.pauseTime = 1500; // Time between instructions in ms
        
        // Initialize components
        this.initTutorialSteps();
        this.initSpeechRecognition();
    }
    
    /**
     * Initialize speech recognition for tutorial commands
     */
    initSpeechRecognition() {
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            // Use the standard SpeechRecognition interface if available, otherwise use the webkit prefix
            this.recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
            
            // Configure recognition
            this.recognition.continuous = false;
            this.recognition.interimResults = false;
            this.recognition.lang = 'en-US';
            
            // Event handlers
            this.recognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript.toLowerCase();
                console.log(`Tutorial heard: "${transcript}"`);
                
                if (transcript.includes('next') || transcript.includes('continue')) {
                    this.nextStep();
                } else if (transcript.includes('previous') || transcript.includes('back')) {
                    this.previousStep();
                } else if (transcript.includes('repeat')) {
                    this.repeatStep();
                } else if (transcript.includes('stop tutorial') || transcript.includes('exit tutorial')) {
                    this.endTutorial();
                }
            };
            
            this.recognition.onend = () => {
                this.isListening = false;
                // Auto restart listening if tutorial is active
                if (this.tutorialActive) {
                    setTimeout(() => {
                        this.startListening();
                    }, 500);
                }
            };
        }
    }
    
    /**
     * Define all tutorial steps with voice instructions
     */
    initTutorialSteps() {
        this.tutorialSteps = [
            {
                title: "Welcome to VocalCart",
                instruction: "Welcome to VocalCart, your voice-powered shopping assistant designed with accessibility in mind. This tutorial will guide you through using VocalCart with voice commands and screen readers. Say 'next' or 'continue' to move to the next step, 'previous' or 'back' to go to the previous step, 'repeat' to hear instructions again, or 'stop tutorial' to exit anytime."
            },
            {
                title: "Activating Voice Commands",
                instruction: "To activate voice commands, press Control plus Space on your keyboard. You'll hear a sound indicating that VocalCart is listening. You can then speak your commands clearly. To stop listening mode, press the Escape key."
            },
            {
                title: "Basic Navigation",
                instruction: "The most important commands for navigation are: Next, Previous, and Repeat. Say 'next' to move to the next product. Say 'previous' to move to the previous product. Say 'repeat' to hear the current product again. You can also press the Spacebar key to go to the next product."
            },
            {
                title: "Searching for Products",
                instruction: "To search for products, say 'search for' followed by what you're looking for. For example, 'search for shoes under 2000' or 'find smartphones'. The system will search and announce the number of products found."
            },
            {
                title: "Getting Product Details",
                instruction: "To hear detailed information about a product, say 'tell me about item' followed by the number. For example, 'tell me about item 2'. This will provide comprehensive details about that product."
            },
            {
                title: "Adding Items to Cart",
                instruction: "To add an item to your shopping cart, say 'add item' followed by the number. For example, 'add item 3 to cart'. The system will confirm when the item has been added."
            },
            {
                title: "Managing Your Cart",
                instruction: "To check what's in your cart, say 'show my cart' or 'view cart'. To remove items, say 'remove item' followed by the number. To clear your entire cart, say 'clear cart'."
            },
            {
                title: "Checking Out",
                instruction: "When you're ready to complete your purchase, simply say 'checkout'. The system will guide you through the checkout process and confirm your order."
            },
            {
                title: "Getting Help",
                instruction: "If you need assistance at any time, say 'help' or 'what can I say' for a list of available commands. You can also access this tutorial again by saying 'start tutorial'."
            },
            {
                title: "Practice Exercise",
                instruction: "Let's practice with a simple exercise. Try these steps: First, search for a product by saying 'search for shirts'. Then, navigate using 'next' and 'previous'. Finally, add an item to your cart by saying 'add item 1 to cart'. Remember, you can say 'repeat' at any time to hear instructions again."
            },
            {
                title: "Tutorial Complete",
                instruction: "Congratulations! You've completed the VocalCart tutorial. You're now ready to shop using voice commands. Remember to use Control plus Space to start voice input, and use commands like 'search for', 'next', 'previous', 'add to cart', and 'checkout'. Happy shopping!"
            }
        ];
    }
    
    /**
     * Start the accessibility tutorial
     */
    startTutorial() {
        this.tutorialActive = true;
        this.currentStep = 0;
        
        // Create tutorial overlay
        this.createTutorialOverlay();
        
        // Announce beginning of tutorial
        this.speak("Starting VocalCart accessibility tutorial. This will guide you through using the app with voice commands.");
        
        setTimeout(() => {
            // Present the first step after a short pause
            this.presentCurrentStep();
            this.startListening();
        }, this.pauseTime);
    }
    
    /**
     * Create visual overlay for the tutorial
     */
    createTutorialOverlay() {
        // Remove existing overlay if there is one
        const existingOverlay = document.getElementById('tutorial-overlay');
        if (existingOverlay) existingOverlay.remove();
        
        // Create new overlay
        const overlay = document.createElement('div');
        overlay.id = 'tutorial-overlay';
        overlay.setAttribute('role', 'dialog');
        overlay.setAttribute('aria-modal', 'true');
        overlay.setAttribute('aria-labelledby', 'tutorial-title');
        
        overlay.innerHTML = `
            <div class="tutorial-container">
                <div class="tutorial-header">
                    <h2 id="tutorial-title">VocalCart Accessibility Tutorial</h2>
                    <button id="close-tutorial" aria-label="Close tutorial">×</button>
                </div>
                <div class="tutorial-content">
                    <div id="tutorial-step-content">
                        <!-- Step content will be inserted here -->
                    </div>
                    <div class="tutorial-progress">
                        <span id="tutorial-step-indicator">Step 1 of ${this.tutorialSteps.length}</span>
                    </div>
                    <div class="tutorial-controls">
                        <button id="tutorial-prev" aria-label="Previous step">◀ Previous</button>
                        <button id="tutorial-repeat" aria-label="Repeat current step">🔁 Repeat</button>
                        <button id="tutorial-next" aria-label="Next step">Next ▶</button>
                    </div>
                    <div class="tutorial-voice-hint">
                        <p>You can also navigate using voice commands:</p>
                        <ul>
                            <li>"next" or "continue" - Move to next step</li>
                            <li>"previous" or "back" - Move to previous step</li>
                            <li>"repeat" - Repeat current step</li>
                            <li>"stop tutorial" - Exit tutorial</li>
                        </ul>
                    </div>
                </div>
            </div>
        `;
        
        // Apply styles
        const style = document.createElement('style');
        style.textContent = `
            #tutorial-overlay {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background-color: rgba(0,0,0,0.8);
                display: flex;
                justify-content: center;
                align-items: center;
                z-index: 9999;
            }
            .tutorial-container {
                background-color: white;
                width: 80%;
                max-width: 600px;
                border-radius: 8px;
                overflow: hidden;
                box-shadow: 0 0 20px rgba(0,0,0,0.5);
            }
            .tutorial-header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 15px;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            .tutorial-header h2 {
                margin: 0;
                font-size: 1.5rem;
            }
            #close-tutorial {
                background: none;
                border: none;
                color: white;
                font-size: 24px;
                cursor: pointer;
            }
            .tutorial-content {
                padding: 20px;
            }
            #tutorial-step-content {
                min-height: 150px;
                margin-bottom: 20px;
            }
            .tutorial-progress {
                text-align: center;
                margin-bottom: 20px;
                color: #666;
            }
            .tutorial-controls {
                display: flex;
                justify-content: space-between;
                gap: 10px;
                margin-bottom: 20px;
            }
            .tutorial-controls button {
                background: #667eea;
                color: white;
                border: none;
                padding: 10px 15px;
                border-radius: 4px;
                cursor: pointer;
                flex-grow: 1;
            }
            .tutorial-controls button:hover {
                background: #5a70d8;
            }
            .tutorial-voice-hint {
                background-color: #f5f5f5;
                border-radius: 4px;
                padding: 10px;
                margin-top: 10px;
            }
            .tutorial-voice-hint p {
                margin-top: 0;
            }
            .tutorial-voice-hint ul {
                margin-bottom: 0;
            }
            .step-title {
                font-size: 1.3rem;
                color: #333;
                margin-top: 0;
            }
            .step-instruction {
                line-height: 1.5;
            }
        `;
        
        // Append overlay and styles
        document.head.appendChild(style);
        document.body.appendChild(overlay);
        
        // Add event listeners
        document.getElementById('close-tutorial').addEventListener('click', () => this.endTutorial());
        document.getElementById('tutorial-prev').addEventListener('click', () => this.previousStep());
        document.getElementById('tutorial-next').addEventListener('click', () => this.nextStep());
        document.getElementById('tutorial-repeat').addEventListener('click', () => this.repeatStep());
        
        // Add keyboard shortcuts
        document.addEventListener('keydown', this.handleTutorialKeyboard.bind(this));
    }
    
    /**
     * Handle keyboard events for tutorial navigation
     */
    handleTutorialKeyboard(e) {
        if (!this.tutorialActive) return;
        
        // Right arrow for next step
        if (e.code === 'ArrowRight') {
            e.preventDefault();
            this.nextStep();
        }
        // Left arrow for previous step
        else if (e.code === 'ArrowLeft') {
            e.preventDefault();
            this.previousStep();
        }
        // R key for repeat
        else if (e.code === 'KeyR') {
            e.preventDefault();
            this.repeatStep();
        }
        // Escape to exit
        else if (e.code === 'Escape') {
            e.preventDefault();
            this.endTutorial();
        }
    }
    
    /**
     * Present the current tutorial step
     */
    presentCurrentStep() {
        if (this.currentStep < 0 || this.currentStep >= this.tutorialSteps.length) {
            console.error('Invalid tutorial step');
            return;
        }
        
        const step = this.tutorialSteps[this.currentStep];
        const stepContent = document.getElementById('tutorial-step-content');
        const stepIndicator = document.getElementById('tutorial-step-indicator');
        
        if (stepContent && stepIndicator) {
            // Update content
            stepContent.innerHTML = `
                <h3 class="step-title">${step.title}</h3>
                <p class="step-instruction">${step.instruction}</p>
            `;
            
            // Update progress indicator
            stepIndicator.textContent = `Step ${this.currentStep + 1} of ${this.tutorialSteps.length}`;
            
            // Speak the instruction
            this.speak(step.instruction);
        }
    }
    
    /**
     * Move to the next tutorial step
     */
    nextStep() {
        if (this.currentStep < this.tutorialSteps.length - 1) {
            this.currentStep++;
            this.presentCurrentStep();
        } else {
            // End of tutorial
            this.speak("You've reached the end of the tutorial. You can exit now by saying 'stop tutorial' or clicking the close button.");
        }
    }
    
    /**
     * Move to the previous tutorial step
     */
    previousStep() {
        if (this.currentStep > 0) {
            this.currentStep--;
            this.presentCurrentStep();
        } else {
            this.speak("You're already at the first step of the tutorial.");
        }
    }
    
    /**
     * Repeat the current tutorial step
     */
    repeatStep() {
        this.presentCurrentStep();
    }
    
    /**
     * End the tutorial and clean up
     */
    endTutorial() {
        this.tutorialActive = false;
        
        // Stop listening
        if (this.isListening && this.recognition) {
            this.recognition.stop();
        }
        
        // Remove overlay
        const overlay = document.getElementById('tutorial-overlay');
        if (overlay) overlay.remove();
        
        // Remove keyboard event listener
        document.removeEventListener('keydown', this.handleTutorialKeyboard);
        
        // Final announcement
        this.speak("Tutorial closed. You can restart it anytime by saying 'start tutorial' or using the accessibility menu.");
    }
    
    /**
     * Start listening for voice commands
     */
    startListening() {
        if (this.recognition && !this.isListening) {
            try {
                this.recognition.start();
                this.isListening = true;
                console.log('Tutorial listening for commands...');
            } catch (err) {
                console.error('Tutorial recognition error:', err);
            }
        }
    }
    
    /**
     * Speak text using speech synthesis
     */
    speak(text) {
        if (!this.synthesis) return;
        
        // Cancel any ongoing speech
        this.synthesis.cancel();
        
        // Create utterance
        const utterance = new SpeechSynthesisUtterance(text);
        
        // Set voice preferences (optional)
        const voices = this.synthesis.getVoices();
        const preferredVoice = voices.find(voice => voice.lang === 'en-US');
        if (preferredVoice) {
            utterance.voice = preferredVoice;
        }
        
        // Speak the text
        this.synthesis.speak(utterance);
        
        // Also update the aria live region for screen readers
        const liveRegion = document.getElementById('tutorial-announcer') || this.createLiveRegion();
        liveRegion.textContent = text;
    }
    
    /**
     * Create live region for screen reader announcements
     */
    createLiveRegion() {
        const region = document.createElement('div');
        region.id = 'tutorial-announcer';
        region.setAttribute('aria-live', 'assertive');
        region.setAttribute('aria-atomic', 'true');
        region.style.position = 'absolute';
        region.style.width = '1px';
        region.style.height = '1px';
        region.style.overflow = 'hidden';
        region.style.clip = 'rect(0 0 0 0)';
        document.body.appendChild(region);
        return region;
    }
}

// Create the global tutorial instance
document.addEventListener('DOMContentLoaded', () => {
    window.accessibilityTutorial = new VoiceAccessibilityTutorial();
    
    // Add tutorial button to the page
    const tutorialBtn = document.createElement('button');
    tutorialBtn.id = 'accessibility-tutorial-btn';
    tutorialBtn.innerHTML = '🔊 Voice Tutorial';
    tutorialBtn.setAttribute('aria-label', 'Start accessibility voice tutorial');
    tutorialBtn.style.position = 'fixed';
    tutorialBtn.style.bottom = '20px';
    tutorialBtn.style.left = '20px';
    tutorialBtn.style.padding = '10px 15px';
    tutorialBtn.style.backgroundColor = '#4CAF50';
    tutorialBtn.style.color = 'white';
    tutorialBtn.style.border = 'none';
    tutorialBtn.style.borderRadius = '5px';
    tutorialBtn.style.cursor = 'pointer';
    tutorialBtn.style.zIndex = '1000';
    tutorialBtn.style.boxShadow = '0 2px 5px rgba(0,0,0,0.2)';
    
    tutorialBtn.addEventListener('click', () => {
        window.accessibilityTutorial.startTutorial();
    });
    
    document.body.appendChild(tutorialBtn);
    
    // Listen for global "start tutorial" command
    if (window.app && window.app.recognition) {
        const originalHandler = window.app.recognition.onresult;
        window.app.recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript.toLowerCase();
            if (transcript.includes('start tutorial') || 
                transcript.includes('accessibility tutorial') || 
                transcript.includes('help me use') ||
                transcript.includes('how to use this app')) {
                window.accessibilityTutorial.startTutorial();
            } else if (originalHandler) {
                originalHandler(event);
            }
        };
    }
});
