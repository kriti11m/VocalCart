/**
 * VocalCart - Voice-Powered Shopping Assistant
 * Advanced voice recognition and real-time data handling
 */

class VoiceShoppingApp {
    constructor() {
        // Core properties
        this.recognition = null;
        this.synthesis = window.speechSynthesis;
        this.isListening = false;
        this.cart = [];
        this.currentProducts = [];
        this.searchInProgress = false;
        this.lastCommand = '';
        this.apiBaseUrl = '';  // Will be set based on current URL
        this.sessionId = 'default';
        this.pollingInterval = null;
        this.isPolling = false;
        
        // Voice properties
        this.voicePreferences = {
            voice: null,
            rate: 1.0,
            pitch: 1.0,
            volume: 1.0
        };

        // Initialize components
        this.setApiBaseUrl();
        this.initSpeechRecognition();
        this.initEventListeners();
        this.loadPreferredVoice();
        this.setupAccessibility();
    }
    
    /**
     * Set API base URL based on current window location
     */
    setApiBaseUrl() {
        const protocol = window.location.protocol;
        const hostname = window.location.hostname;
        const port = window.location.port ? `:${window.location.port}` : '';
        this.apiBaseUrl = `${protocol}//${hostname}${port}`;
        console.log(`API base URL set to: ${this.apiBaseUrl}`);
    }
    
    /**
     * Initialize Web Speech API for voice recognition
     */
    initSpeechRecognition() {
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            // Use the standard SpeechRecognition interface if available, otherwise use the webkit prefix
            this.recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
            
            // Configure recognition
            this.recognition.continuous = false;
            this.recognition.interimResults = false;
            this.recognition.lang = 'en-US';
            this.recognition.maxAlternatives = 3;
            
            // Event handlers
            this.recognition.onstart = this.handleRecognitionStart.bind(this);
            this.recognition.onresult = this.handleRecognitionResult.bind(this);
            this.recognition.onerror = this.handleRecognitionError.bind(this);
            this.recognition.onend = this.handleRecognitionEnd.bind(this);
            
            this.announce("Voice recognition ready");
        } else {
            console.error("Speech recognition not supported");
            this.updateUI('error', 'Speech recognition is not supported in your browser');
            this.announce("Voice recognition not available in your browser");
        }
    }
    
    /**
     * Set up event listeners for UI elements
     */
    initEventListeners() {
        // Main voice button
        document.getElementById('voiceButton')?.addEventListener('click', () => {
            if (this.isListening) {
                this.stopListening();
            } else {
                this.startListening();
            }
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            // Press Spacebar while holding Ctrl to activate voice
            if (e.ctrlKey && e.code === 'Space' && !this.isListening) {
                e.preventDefault();
                this.startListening();
            }
            
            // Escape key to stop listening
            if (e.code === 'Escape' && this.isListening) {
                this.stopListening();
            }
            
            // Handle spacebar for next item navigation
            if (e.code === 'Space' && !e.ctrlKey && !this.isListening) {
                e.preventDefault();
                this.handleNavigationCommand('next');
            }
        });

        // Handle window focus for better UX
        window.addEventListener('focus', () => {
            // Check if we need to resume polling when window regains focus
            if (this.searchInProgress && !this.isPolling) {
                this.startPollingForResults();
            }
        });

        window.addEventListener('blur', () => {
            // Reduce polling frequency when window loses focus
            if (this.isPolling) {
                this.pausePolling();
            }
        });
    }

    /**
     * Set up accessibility features
     */
    setupAccessibility() {
        // Create live region for screen readers
        const liveRegion = document.createElement('div');
        liveRegion.setAttribute('aria-live', 'polite');
        liveRegion.setAttribute('aria-atomic', 'true');
        liveRegion.classList.add('aria-live-region');
        liveRegion.id = 'voice-assistant-announcer';
        document.body.appendChild(liveRegion);
        
        // Add keyboard shortcut instructions
        const shortcutsInfo = document.createElement('div');
        shortcutsInfo.innerHTML = `
            <div class="accessibility-info" style="margin-top: 20px; padding: 10px; text-align: center; color: #667eea;">
                <strong>Keyboard shortcuts:</strong> Press <kbd>Ctrl+Space</kbd> to activate voice, <kbd>Esc</kbd> to cancel
            </div>
        `;
        document.querySelector('.voice-control')?.appendChild(shortcutsInfo);
    }
    
    /**
     * Start listening for voice commands
     */
    startListening() {
        if (this.recognition) {
            try {
                this.recognition.start();
                console.log("Starting voice recognition...");
            } catch (err) {
                console.error("Error starting recognition:", err);
                this.updateUI('error', 'Error starting voice recognition');
            }
        }
    }
    
    /**
     * Stop listening for voice commands
     */
    stopListening() {
        if (this.recognition && this.isListening) {
            this.recognition.stop();
            console.log("Stopping voice recognition");
        }
    }
    
    /**
     * Handle recognition start event
     */
    handleRecognitionStart() {
        this.isListening = true;
        this.updateUI('listening', 'Listening... Speak your command');
        console.log("Recognition started");
    }
    
    /**
     * Handle recognition result event
     * @param {SpeechRecognitionEvent} event - The recognition event
     */
    handleRecognitionResult(event) {
        const transcript = event.results[0][0].transcript;
        console.log(`Heard: "${transcript}" (Confidence: ${event.results[0][0].confidence.toFixed(2)})`);
        this.handleVoiceCommand(transcript);
    }
    
    /**
     * Handle recognition error event
     * @param {SpeechRecognitionError} event - The error event
     */
    handleRecognitionError(event) {
        console.error("Recognition error:", event.error);
        
        let errorMessage = "Sorry, I couldn't hear you clearly";
        switch (event.error) {
            case 'no-speech':
                errorMessage = "I couldn't detect any speech. Please try again.";
                break;
            case 'aborted':
                errorMessage = "Listening was aborted";
                break;
            case 'audio-capture':
                errorMessage = "No microphone was found or microphone is disabled";
                break;
            case 'network':
                errorMessage = "Network error occurred. Please check your connection.";
                break;
            case 'not-allowed':
            case 'service-not-allowed':
                errorMessage = "Microphone access was denied or is disabled";
                break;
        }
        
        this.updateUI('error', errorMessage);
        this.announce(errorMessage);
    }
    
    /**
     * Handle recognition end event
     */
    handleRecognitionEnd() {
        this.isListening = false;
        console.log("Recognition ended");
        
        // Only update UI if we're not already processing a command
        if (!this.searchInProgress) {
            this.updateUI('idle');
        }
    }
    
    /**
     * Process text command from input field
     */
    handleTextCommand() {
        const textInput = document.getElementById('textInput');
        const command = textInput.value.trim();
        
        if (!command) {
            this.updateUI('error', 'Please enter a command');
            return;
        }
        
        this.lastCommand = command;
        this.updateUI('processing', `Processing: "${command}"`);
        this.announce(`Processing your command: ${command}`);
        
        this.processCommand(command);
        textInput.value = '';
    }

    /**
     * Handle voice command
     * @param {string} command - The transcribed voice command
     */
    async handleVoiceCommand(command) {
        this.lastCommand = command;
        this.updateUI('processing', `Processing: "${command}"`);
        this.announce(`I heard: ${command}`);
        
        // Process the command
        await this.processCommand(command);
    }
    
    /**
     * Process a command (from voice or text input)
     * @param {string} command - The command to process
     */
    async processCommand(command) {
        // Extract any search terms and filters
        const searchInfo = this.parseSearchCommand(command);
        
        if (searchInfo.isSearch) {
            await this.handleSearchCommand(command, searchInfo);
        } else if (command.toLowerCase().includes('next') || command.toLowerCase().includes('show more')) {
            await this.handleNavigationCommand('next');
        } else if (command.toLowerCase().includes('previous') || command.toLowerCase().includes('back')) {
            await this.handleNavigationCommand('previous');
        } else if (command.toLowerCase().includes('buy this') || command.toLowerCase().includes('purchase')) {
            await this.handleBuyCommand();
        } else if (this.isAddToCartCommand(command)) {
            await this.handleAddToCartCommand(command);
        } else if (command.toLowerCase().includes('clear cart') || command.toLowerCase().includes('empty cart')) {
            this.clearCart();
            this.updateUI('idle', 'Your cart has been cleared');
            this.speak('Your cart has been cleared');
        } else if (command.toLowerCase().includes('checkout')) {
            this.checkout();
        } else {
            // If no specific command pattern is recognized, send to API for processing
            await this.sendCommandToAPI(command);
        }
    }

    /**
     * Handle search command specifically
     * @param {string} command - Full command 
     * @param {object} searchInfo - Parsed search info
     */
    async handleSearchCommand(command, searchInfo) {
        try {
            this.searchInProgress = true;
            
            // Create loading skeleton
            this.showSearchLoadingState();
            
            // Send initial search request
            const response = await fetch(`${this.apiBaseUrl}/api/voice-command`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    command: command,
                    session_id: this.sessionId
                })
            });
            
            const result = await response.json();
            
            if (result.status === 'processing') {
                // If search is being processed asynchronously, start polling for results
                this.updateUI('processing', 'Searching for real-time products...');
                this.speak('Searching for products in real time. This might take a moment.');
                this.startPollingForResults();
            } else {
                // If search results were returned immediately
                this.searchInProgress = false;
                this.handleCommandResult(result);
            }
            
        } catch (error) {
            console.error('Search error:', error);
            this.searchInProgress = false;
            this.updateUI('error', 'Sorry, something went wrong with your search');
            this.speak('Sorry, I encountered an error searching for products.');
            this.hideSearchLoadingState();
        }
    }

    /**
     * Poll for real-time search results
     */
    startPollingForResults() {
        if (this.pollingInterval) {
            clearInterval(this.pollingInterval);
        }
        
        this.isPolling = true;
        let pollCount = 0;
        const maxPolls = 15; // Stop after 15 attempts (30 seconds)
        
        this.pollingInterval = setInterval(async () => {
            pollCount++;
            
            try {
                const response = await fetch(`${this.apiBaseUrl}/api/search-status/${this.sessionId}`);
                const result = await response.json();
                
                if (result.status === 'complete') {
                    // Results are ready
                    clearInterval(this.pollingInterval);
                    this.isPolling = false;
                    this.searchInProgress = false;
                    
                    this.handleCommandResult(result);
                    this.hideSearchLoadingState();
                } else if (pollCount >= maxPolls) {
                    // Give up after max attempts
                    clearInterval(this.pollingInterval);
                    this.isPolling = false;
                    this.searchInProgress = false;
                    
                    this.updateUI('error', 'Search is taking too long. Please try again.');
                    this.speak('Sorry, the search is taking longer than expected. Please try again with different keywords.');
                    this.hideSearchLoadingState();
                }
                
            } catch (error) {
                console.error('Polling error:', error);
                clearInterval(this.pollingInterval);
                this.isPolling = false;
                this.searchInProgress = false;
                
                this.updateUI('error', 'Error checking search results');
                this.hideSearchLoadingState();
            }
        }, 2000); // Check every 2 seconds
    }
    
    /**
     * Pause polling when window loses focus
     */
    pausePolling() {
        if (this.pollingInterval) {
            clearInterval(this.pollingInterval);
            this.isPolling = false;
        }
    }
    
    /**
     * Parse a search command to extract important elements
     * @param {string} command - The command to parse
     * @returns {object} Parsed search information
     */
    parseSearchCommand(command) {
        const lowercaseCmd = command.toLowerCase();
        
        // Check if this is a search command
        const isSearch = lowercaseCmd.includes('find') || 
                        lowercaseCmd.includes('search') || 
                        lowercaseCmd.includes('show me') ||
                        lowercaseCmd.includes('get me') ||
                        lowercaseCmd.includes('look for');
        
        if (!isSearch) {
            return { isSearch: false };
        }
        
        // Extract price constraints
        let minPrice = null;
        let maxPrice = null;
        
        // "under X" pattern
        const underMatch = lowercaseCmd.match(/under\s+(\d+)/);
        if (underMatch) {
            maxPrice = parseInt(underMatch[1]);
        }
        
        // "between X and Y" pattern
        const betweenMatch = lowercaseCmd.match(/between\s+(\d+)\s+and\s+(\d+)/);
        if (betweenMatch) {
            minPrice = parseInt(betweenMatch[1]);
            maxPrice = parseInt(betweenMatch[2]);
        }
        
        // Extract main search terms by removing price constraints
        let searchTerms = lowercaseCmd
            .replace(/find|search|show me|get me|look for/g, '')
            .replace(/under\s+\d+/g, '')
            .replace(/between\s+\d+\s+and\s+\d+/g, '')
            .replace(/rupees|rs|₹/g, '')
            .trim();
        
        return {
            isSearch: true,
            searchTerms,
            minPrice,
            maxPrice
        };
    }
    
    /**
     * Check if command is asking to add something to cart
     * @param {string} command - Command to check
     * @returns {boolean} True if it's an add to cart command
     */
    isAddToCartCommand(command) {
        const lowercaseCmd = command.toLowerCase();
        return (
            lowercaseCmd.includes('add to cart') || 
            lowercaseCmd.includes('put in cart') ||
            lowercaseCmd.includes('add item') ||
            (lowercaseCmd.includes('add') && lowercaseCmd.includes('cart'))
        );
    }
    
    /**
     * Send a command to the API for processing
     * @param {string} command - The command to send
     */
    async sendCommandToAPI(command) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/api/voice-command`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    command: command,
                    session_id: this.sessionId
                })
            });
            
            const result = await response.json();
            this.handleCommandResult(result);
            
        } catch (error) {
            console.error('API error:', error);
            this.updateUI('error', 'Sorry, something went wrong processing your command');
            this.speak('Sorry, I encountered an error processing your request.');
        }
    }
    
    /**
     * Handle navigation commands like next/previous
     * @param {string} direction - Direction to navigate (next or previous)
     */
    async handleNavigationCommand(direction) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/api/navigate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    command: direction,
                    session_id: this.sessionId
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                if (result.product) {
                    this.speak(result.voice_response);
                    
                    // Highlight the new current product
                    this.highlightProduct(result.current_index);
                }
                this.updateUI('idle', result.voice_response || `Showing ${direction} product`);
            } else {
                this.speak(result.voice_response || `No ${direction} product available`);
                this.updateUI('idle', result.voice_response || `No ${direction} product available`);
            }
            
        } catch (error) {
            console.error('Navigation error:', error);
            this.updateUI('error', `Error navigating ${direction}`);
            this.speak(`Sorry, I couldn't navigate to the ${direction} product.`);
        }
    }
    
    /**
     * Handle "buy this" or purchase commands
     */
    async handleBuyCommand() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/api/navigate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    command: 'buy',
                    session_id: this.sessionId
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.speak(result.voice_response || "I'll take you to the product page to complete your purchase");
                this.updateUI('idle', result.voice_response || "Taking you to the product page");
                
                // If a URL was provided, open it
                if (result.product && result.product.url) {
                    window.open(result.product.url, '_blank');
                }
            } else {
                this.speak(result.voice_response || "Sorry, I couldn't complete the purchase");
                this.updateUI('error', result.voice_response || "Couldn't complete purchase");
            }
            
        } catch (error) {
            console.error('Buy command error:', error);
            this.updateUI('error', "Error processing purchase");
            this.speak("Sorry, I encountered an error processing your purchase.");
        }
    }
    
    /**
     * Handle adding items to cart from voice
     * @param {string} command - The add to cart command
     */
    async handleAddToCartCommand(command) {
        // Extract the item number
        const itemMatch = command.match(/item\s+(\d+)/i);
        const numberMatch = command.match(/number\s+(\d+)/i);
        const productMatch = command.match(/product\s+(\d+)/i);
        
        let itemNumber = null;
        if (itemMatch) itemNumber = parseInt(itemMatch[1]);
        else if (numberMatch) itemNumber = parseInt(numberMatch[1]);
        else if (productMatch) itemNumber = parseInt(productMatch[1]);
        
        if (itemNumber === null) {
            // Try to add currently focused item
            if (this.currentProducts.length > 0) {
                const currentIndex = document.querySelector('.product-card.highlight')?.dataset?.index || 0;
                this.addToCartByIndex(currentIndex);
                this.speak(`Added ${this.currentProducts[currentIndex]?.title} to your cart`);
                this.updateUI('idle', `Added item to your cart`);
            } else {
                this.speak("Please specify which item you want to add to your cart");
                this.updateUI('idle', "Please specify which item to add");
            }
            return;
        }
        
        // Adjust for 1-based indexing in voice commands
        const index = itemNumber - 1;
        
        if (index >= 0 && index < this.currentProducts.length) {
            this.addToCartByIndex(index);
            const product = this.currentProducts[index];
            const response = `Added ${product.title} to your cart.`;
            this.speak(response);
            this.updateUI('idle', response);
        } else {
            const response = `Sorry, I couldn't find item ${itemNumber}. Please try another item number.`;
            this.speak(response);
            this.updateUI('error', response);
        }
    }
    
    /**
     * Process API response and update UI accordingly
     * @param {object} result - API response
     */
    handleCommandResult(result) {
        // Check for search results
        if (result.products && Array.isArray(result.products)) {
            this.displayProducts(result.products);
            const message = result.voice_response || `Found ${result.products.length} products`;
            this.speak(message);
            this.updateUI('idle', message);
        } 
        // Check for navigation or other actions
        else if (result.action) {
            switch(result.action) {
                case 'next':
                case 'previous':
                    this.speak(result.voice_response);
                    this.highlightProduct(result.current_index);
                    this.updateUI('idle', result.voice_response);
                    break;
                    
                case 'buy':
                    this.speak(result.voice_response);
                    this.updateUI('idle', result.voice_response);
                    if (result.product && result.product.url) {
                        window.open(result.product.url, '_blank');
                    }
                    break;
                    
                default:
                    this.speak(result.voice_response || 'Command processed');
                    this.updateUI('idle', result.voice_response || 'Command processed');
            }
        } else {
            // Default handling
            this.speak(result.voice_response || result.message || 'Command processed');
            this.updateUI('idle', result.voice_response || result.message || 'Command processed');
        }
    }

    /**
     * Update UI based on app state
     * @param {string} state - Current state (listening, processing, idle, error)
     * @param {string} message - Optional status message
     */
    updateUI(state, message = '') {
        const button = document.getElementById('voiceButton');
        const status = document.getElementById('status');
        
        if (!button || !status) return;
        
        switch(state) {
            case 'listening':
                button.innerHTML = '🔴 <span class="loading"></span> Listening...';
                button.classList.add('listening');
                status.textContent = message || 'Listening... Speak your command';
                break;
                
            case 'processing':
                button.innerHTML = '⏳ <span class="loading"></span> Processing...';
                button.classList.remove('listening');
                status.textContent = message || 'Processing your request...';
                this.setInputsDisabled(true);
                break;
                
            case 'error':
                button.textContent = '🎤 Try Again';
                button.classList.remove('listening');
                status.innerHTML = `<span style="color: var(--error-color);">❌ ${message}</span>`;
                this.setInputsDisabled(false);
                break;
                
            default: // idle state
                button.textContent = '🎤 Start Voice Shopping';
                button.classList.remove('listening');
                
                if (message) {
                    status.innerHTML = `<span style="color: var(--success-color);">✅ ${message}</span>`;
                } else {
                    status.innerHTML = 'Choose voice or text input to start shopping';
                }
                
                this.setInputsDisabled(false);
        }
    }
    
    /**
     * Enable/disable input controls during processing
     * @param {boolean} disabled - Whether inputs should be disabled
     */
    setInputsDisabled(disabled) {
        const textInput = document.getElementById('textInput');
        const submitBtn = document.getElementById('submitBtn');
        const voiceBtn = document.getElementById('voiceButton');
        
        if (textInput) textInput.disabled = disabled;
        if (submitBtn) submitBtn.disabled = disabled;
        if (voiceBtn) voiceBtn.disabled = disabled;
    }
    
    /**
     * Show skeleton loading state while products are being fetched
     */
    showSearchLoadingState() {
        const grid = document.getElementById('productsGrid');
        if (!grid) return;
        
        // Add a real-time indicator
        const statusDiv = document.createElement('div');
        statusDiv.className = 'processing-indicator';
        statusDiv.innerHTML = `
            <span class="loading"></span>
            <span>Searching for products in real-time <span class="real-time-badge">LIVE</span></span>
        `;
        statusDiv.setAttribute('aria-live', 'polite');
        
        // Generate skeletons
        const skeletonHTML = Array(6).fill(0).map(() => `
            <div class="skeleton-product">
                <div class="skeleton skeleton-image"></div>
                <div class="skeleton skeleton-title"></div>
                <div class="skeleton skeleton-price"></div>
                <div class="skeleton skeleton-button"></div>
            </div>
        `).join('');
        
        grid.innerHTML = '';
        grid.appendChild(statusDiv);
        grid.insertAdjacentHTML('beforeend', skeletonHTML);
    }
    
    /**
     * Remove skeleton loading state
     */
    hideSearchLoadingState() {
        const grid = document.getElementById('productsGrid');
        const statusIndicator = grid?.querySelector('.processing-indicator');
        
        if (statusIndicator) {
            statusIndicator.remove();
        }
    }
    
    /**
     * Display products in the product grid
     * @param {Array} products - Products to display
     */
    displayProducts(products) {
        this.currentProducts = products;
        const grid = document.getElementById('productsGrid');
        
        if (!grid) return;
        
        if (!products || products.length === 0) {
            grid.innerHTML = `
                <div class="empty-state">
                    <p>No products found. Try a different search term!</p>
                </div>
            `;
            return;
        }
        
        grid.innerHTML = products.map((product, index) => {
            // Get source badge styling
            let sourceBadge = '';
            if (product.source || product.store) {
                let source = product.source || product.store || 'unknown';
                let badgeClass = 'source-badge';
                
                if (source.toLowerCase().includes('flipkart')) {
                    badgeClass += ' flipkart';
                } else if (source.toLowerCase().includes('myntra')) {
                    badgeClass += ' myntra';
                } else if (source.toLowerCase().includes('amazon')) {
                    badgeClass += ' amazon';
                }
                
                sourceBadge = `<span class="${badgeClass}">${source}</span>`;
            }
            
            // Format price consistently
            let price = product.price;
            if (typeof price === 'string') {
                price = price.replace(/[^0-9]/g, '');
            }
            
            let displayPrice = '₹' + (typeof price === 'number' ? 
                price.toLocaleString() : 
                price || 'N/A');
            
            // Get product image if available with better fallback handling
            const placeholderImage = '/static/placeholder.svg';
            let imageUrl = product.image_url || product.image || product.imageUrl;
            
            // Create an image element to test if the URL is valid
            if (imageUrl) {
                const img = new Image();
                img.onerror = function() {
                    // If external image fails to load, use the local fallback
                    const imgElement = document.querySelector(`.product-card[data-index="${index}"] .product-image`);
                    if (imgElement) imgElement.src = placeholderImage;
                };
                img.src = imageUrl;
            } else {
                // Use placeholder if no image URL is provided
                imageUrl = placeholderImage;
            }
            
            // Real-time badge
            const realTimeBadge = product.data_source === 'real-time' ? 
                `<span class="real-time-badge">REAL-TIME</span>` : '';
            
            return `
                <div class="product-card" role="article" aria-label="Product ${index + 1} of ${products.length}"
                     tabindex="0" data-index="${index}">
                    <div class="product-header">
                        <span class="product-number">#${index + 1}</span>
                        ${sourceBadge}
                    </div>
                    <img src="${imageUrl}" alt="${product.title}" class="product-image">
                    <div class="product-title" title="${product.title}">${product.title}</div>
                    <div class="product-price">${displayPrice} ${realTimeBadge}</div>
                    ${product.rating ? 
                        `<div class="product-rating">⭐ ${product.rating}</div>` : ''}
                    ${product.discount ? 
                        `<div class="product-discount">🏷️ ${product.discount}</div>` : ''}
                    <div class="product-actions">
                        <button onclick="app.getProductDetails(${index + 1})" class="details-btn" 
                                aria-label="Get details for product ${index + 1}: ${product.title}">
                            📋 Details
                        </button>
                        <button onclick="app.addToCartByIndex(${index})" class="add-to-cart-btn"
                                aria-label="Add product ${index + 1} to cart: ${product.title}">
                            🛒 Add to Cart
                        </button>
                    </div>
                </div>
            `;
        }).join('') + `
            <div class="accessibility-info" style="grid-column: 1/-1; margin-top: 20px; padding: 15px; background: rgba(102, 126, 234, 0.1); border-radius: 10px; font-size: 0.9em; color: #667eea;">
                <strong>Voice Shopping:</strong> ${products.length} products found from multiple stores. 
                Say <em>"tell me about item 1"</em> or <em>"add item 2 to cart"</em> for hands-free shopping.
                You can also say <em>"next"</em> or <em>"previous"</em> to navigate through products.
            </div>
        `;

        // Add keyboard navigation for products
        const productCards = grid.querySelectorAll('.product-card');
        productCards.forEach(card => {
            card.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') {
                    this.getProductDetails(parseInt(card.dataset.index) + 1);
                }
            });
        });
    }
    
    /**
     * Highlight a specific product in the UI
     * @param {number} index - Product index to highlight
     */
    highlightProduct(index) {
        const productCards = document.querySelectorAll('.product-card');
        
        // Remove existing highlights
        productCards.forEach(card => card.classList.remove('highlight'));
        
        // Add highlight to current product
        if (productCards[index]) {
            productCards[index].classList.add('highlight');
            productCards[index].scrollIntoView({ behavior: 'smooth', block: 'center' });
            
            // Add visual highlight style
            productCards[index].style.boxShadow = '0 0 0 3px var(--primary-color), 0 20px 50px rgba(0,0,0,0.15)';
            productCards[index].style.transform = 'translateY(-8px)';
            
            // Remove the highlight style after a delay
            setTimeout(() => {
                productCards[index].style.boxShadow = '';
                productCards[index].style.transform = '';
            }, 3000);
        }
    }
    
    /**
     * Get detailed information about a specific product
     * @param {number} itemNumber - Product number (1-based)
     */
    async getProductDetails(itemNumber) {
        try {
            this.updateUI('processing', `Getting details for item ${itemNumber}...`);
            
            // Adjust for 0-based indexing in our array
            const index = itemNumber - 1;
            
            if (index < 0 || index >= this.currentProducts.length) {
                this.updateUI('error', `Invalid item number: ${itemNumber}`);
                this.speak(`I couldn't find item number ${itemNumber}`);
                return;
            }
            
            const product = this.currentProducts[index];
            
            // Highlight the selected product
            this.highlightProduct(index);
            
            // Prepare a detailed description
            let description = `Product ${itemNumber}: ${product.title}. `;
            description += `Price: ${product.price} rupees. `;
            
            if (product.rating) description += `Rating: ${product.rating} stars. `;
            if (product.discount) description += `Discount: ${product.discount}. `;
            if (product.description) description += `Description: ${product.description}. `;
            if (product.source || product.store) description += `Available on ${product.source || product.store}. `;
            
            description += `You can say "add item ${itemNumber} to cart" or "buy this" to purchase.`;
            
            // Update UI and speak description
            this.updateUI('idle', `Showing details for ${product.title}`);
            this.speak(description);
            
        } catch (error) {
            console.error('Error getting product details:', error);
            this.updateUI('error', 'Sorry, I could not retrieve product details');
            this.speak('Sorry, I encountered an error getting the product details.');
        }
    }
    
    /**
     * Add a specific product to the cart by index
     * @param {number} index - Product index (0-based)
     */
    addToCartByIndex(index) {
        if (!this.currentProducts || index < 0 || index >= this.currentProducts.length) {
            console.error('Invalid product index:', index);
            return;
        }
        
        const product = this.currentProducts[index];
        
        // Send to backend API to add to cart
        this.addToCartViaAPI(product, index);
        
        // Also add to local cart for UI updates
        const existingItemIndex = this.cart.findIndex(item => 
            item.title === product.title);
            
        if (existingItemIndex >= 0) {
            // Increment quantity if already in cart
            this.cart[existingItemIndex].quantity = 
                (this.cart[existingItemIndex].quantity || 1) + 1;
        } else {
            // Add new item to cart
            this.cart.push({...product, quantity: 1});
        }
        
        this.updateCartDisplay();
        
        // Show a brief confirmation message
        const productEl = document.querySelector(`.product-card[data-index="${index}"]`);
        if (productEl) {
            const confirmMsg = document.createElement('div');
            confirmMsg.classList.add('add-confirmation');
            confirmMsg.textContent = '✅ Added to cart';
            confirmMsg.style.position = 'absolute';
            confirmMsg.style.top = '10px';
            confirmMsg.style.right = '10px';
            confirmMsg.style.background = 'var(--success-color)';
            confirmMsg.style.color = 'white';
            confirmMsg.style.padding = '5px 10px';
            confirmMsg.style.borderRadius = '5px';
            confirmMsg.style.fontSize = '0.9em';
            confirmMsg.style.animation = 'fadeInOut 2s forwards';
            
            // Add the animation style
            const style = document.createElement('style');
            style.textContent = `
                @keyframes fadeInOut {
                    0% { opacity: 0; transform: translateY(-10px); }
                    10% { opacity: 1; transform: translateY(0); }
                    70% { opacity: 1; }
                    100% { opacity: 0; }
                }
            `;
            document.head.appendChild(style);
            
            productEl.style.position = 'relative';
            productEl.appendChild(confirmMsg);
            
            // Remove after animation completes
            setTimeout(() => {
                confirmMsg.remove();
            }, 2000);
        }
    }
    
    /**
     * Add product to cart via API
     * @param {Object} product - Product to add to cart
     * @param {number} index - Product index
     */
    async addToCartViaAPI(product, index) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/api/cart/add`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    product: product,
                    session_id: this.sessionId
                })
            });
            
            const result = await response.json();
            
            if (!result.success) {
                console.error('Failed to add item to cart via API:', result.message);
            }
            
        } catch (error) {
            console.error('Error adding to cart via API:', error);
        }
    }
    
    /**
     * Update the cart display in the UI
     */
    updateCartDisplay() {
        const cartItems = document.getElementById('cartItems');
        const cartTotal = document.getElementById('cartTotal');
        
        if (!cartItems || !cartTotal) return;
        
        if (this.cart.length === 0) {
            cartItems.innerHTML = `
                <div class="empty-state">
                    <p>Your cart is empty</p>
                </div>
            `;
            cartTotal.textContent = '';
            return;
        }
        
        cartItems.innerHTML = this.cart.map((item, index) => {
            const quantity = item.quantity || 1;
            const price = typeof item.price === 'number' ? 
                item.price : 
                parseInt(String(item.price).replace(/[^\d]/g, '')) || 0;
            
            const title = item.title.length > 40 ? item.title.substring(0, 40) + '...' : item.title;
            
            return `
                <div class="cart-item">
                    <div style="font-size: 0.95em; font-weight: 600; margin-bottom: 5px;">${title}</div>
                    <div style="color: var(--primary-color); font-weight: bold;">
                        ${quantity > 1 ? `${quantity} × ` : ''}₹${price.toLocaleString()}
                    </div>
                    <button onclick="app.removeFromCart(${index})" 
                            class="remove-btn" 
                            style="background: none; border: none; color: var(--error-color); cursor: pointer; font-size: 0.8em; margin-top: 5px;"
                            aria-label="Remove ${item.title} from cart">
                        🗑️ Remove
                    </button>
                </div>
            `;
        }).join('');
        
        // Calculate total
        const total = this.cart.reduce((sum, item) => {
            const price = typeof item.price === 'number' ? 
                item.price : 
                parseInt(String(item.price).replace(/[^\d]/g, '')) || 0;
            
            const quantity = item.quantity || 1;
            return sum + (price * quantity);
        }, 0);
        
        cartTotal.textContent = `Total: ₹${total.toLocaleString()}`;
        
        // Add accessibility announcement
        this.announce(`Item added to cart. Cart now has ${this.cart.length} item${this.cart.length !== 1 ? 's' : ''} totaling ${total} rupees`);
    }
    
    /**
     * Remove an item from the cart
     * @param {number} index - Index of item to remove
     */
    async removeFromCart(index) {
        if (index >= 0 && index < this.cart.length) {
            const item = this.cart[index];
            
            try {
                // Remove via API first
                const response = await fetch(`${this.apiBaseUrl}/api/cart/remove`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ 
                        item_title: item.title,
                        session_id: this.sessionId
                    })
                });
                
                const result = await response.json();
                
                // Update local cart regardless of API result to keep UI in sync
                this.cart.splice(index, 1);
                this.updateCartDisplay();
                
                // Announce the removal
                this.announce(`Removed ${item.title} from your cart`);
                
                if (!result.success) {
                    console.warn('API cart removal had issues:', result.message);
                }
                
            } catch (error) {
                console.error('Error removing from cart via API:', error);
                
                // Still update local cart to maintain UI consistency
                this.cart.splice(index, 1);
                this.updateCartDisplay();
                
                // Announce the removal
                this.announce(`Removed ${item.title} from your cart, but there was a synchronization error`);
            }
        }
    }
    
    /**
     * Clear all items from the cart
     */
    async clearCart() {
        try {
            // Call API to clear cart
            const response = await fetch(`${this.apiBaseUrl}/api/cart/clear`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    session_id: this.sessionId
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                // Clear local cart
                this.cart = [];
                this.updateCartDisplay();
                this.speak("Your cart has been cleared");
                this.updateUI('idle', 'Cart cleared');
            } else {
                console.error('Failed to clear cart:', result.message);
            }
            
        } catch (error) {
            console.error('Error clearing cart:', error);
            this.speak("I encountered an error trying to clear your cart");
            this.updateUI('error', 'Error clearing cart');
        }
    }
    
    /**
     * Process checkout
     */
    async checkout() {
        if (this.cart.length === 0) {
            this.speak('Your cart is empty. Please add items before checkout.');
            this.updateUI('idle', 'Cart is empty');
            return;
        }
        
        try {
            this.updateUI('processing', 'Processing checkout...');
            
            // Call API to process checkout
            const response = await fetch(`${this.apiBaseUrl}/api/cart/checkout`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    session_id: this.sessionId
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                // Clear local cart
                this.cart = [];
                this.updateCartDisplay();
                
                // Use the response from API or fallback to our own message
                const message = result.message || 
                    `Thank you for your order! Your items will be processed for shipping.`;
                
                this.speak(message);
                this.updateUI('idle', 'Checkout complete!');
            } else {
                this.speak(result.message || "Sorry, I couldn't process your checkout");
                this.updateUI('error', result.message || 'Checkout failed');
            }
            
        } catch (error) {
            console.error('Error processing checkout:', error);
            this.speak("I encountered an error processing your checkout");
            this.updateUI('error', 'Checkout failed');
        }
    }
    
    /**
     * Load preferred voice for speech synthesis
     */
    loadPreferredVoice() {
        if (!this.synthesis) return;
        
        // Wait for voices to load
        const loadVoices = () => {
            const voices = this.synthesis.getVoices();
            
            if (voices.length > 0) {
                // Try to find an Indian English voice for appropriate pronunciation of rupees
                let preferredVoice = voices.find(voice => voice.lang === 'en-IN');
                
                // Fall back to any English voice
                if (!preferredVoice) {
                    preferredVoice = voices.find(voice => voice.lang.startsWith('en'));
                }
                
                if (preferredVoice) {
                    this.voicePreferences.voice = preferredVoice;
                    console.log(`Voice set to: ${preferredVoice.name} (${preferredVoice.lang})`);
                }
            }
        };
        
        // If voices already loaded, set now
        if (this.synthesis.getVoices().length) {
            loadVoices();
        }
        
        // Otherwise set on voiceschanged event
        this.synthesis.onvoiceschanged = loadVoices;
    }
    
    /**
     * Speak text using speech synthesis
     * @param {string} text - Text to speak
     */
    speak(text) {
        if (!this.synthesis) return;
        
        // Cancel any ongoing speech
        this.synthesis.cancel();
        
        // Create utterance
        const utterance = new SpeechSynthesisUtterance(text);
        
        // Set voice preferences
        if (this.voicePreferences.voice) {
            utterance.voice = this.voicePreferences.voice;
        }
        
        utterance.rate = this.voicePreferences.rate;
        utterance.pitch = this.voicePreferences.pitch;
        utterance.volume = this.voicePreferences.volume;
        
        // Speak the text
        this.synthesis.speak(utterance);
        
        // Also update the aria live region for screen readers
        this.announce(text);
    }
    
    /**
     * Announce message to screen readers
     * @param {string} text - Text to announce
     */
    announce(text) {
        const liveRegion = document.getElementById('voice-assistant-announcer');
        if (liveRegion) {
            liveRegion.textContent = text;
        }
    }
    
    /* === Test Functions === */
    
    /**
     * Test function to initiate a search
     */
    testSearch() {
        this.processCommand('search for shoes under 2000');
    }
    
    /**
     * Function to view cart
     */
    viewCart() {
        if (this.cart.length === 0) {
            this.speak('Your shopping cart is empty');
        } else {
            const count = this.cart.length;
            const message = `Your cart has ${count} item${count !== 1 ? 's' : ''}. Use the checkout button when you're ready to purchase.`;
            this.speak(message);
        }
    }
    
    /**
     * Helper function to set example text
     * @param {string} text - Example command text
     */
    setExampleText(text) {
        const textInput = document.getElementById('textInput');
        if (textInput) {
            textInput.value = text;
            textInput.focus();
        }
    }
}

/**
 * Global function for handling Enter key in text input
 * @param {KeyboardEvent} event - Key event
 */
function handleKeyPress(event) {
    if (event.key === 'Enter') {
        app.handleTextCommand();
    }
}

// Initialize the app when the document is ready
document.addEventListener('DOMContentLoaded', () => {
    // Expose the app globally
    window.app = new VoiceShoppingApp();
    
    console.log('VocalCart initialized and ready');
});
