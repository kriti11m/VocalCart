/**
 * VocalCart Accessibility Configuration
 * This file contains configuration settings for all accessibility features.
 */

const VocalCartAccessibility = {
    /**
     * General accessibility settings
     */
    settings: {
        // Auto-start tutorial for screen reader users
        autoStartTutorial: true,
        
        // Time delay before auto-starting tutorial (milliseconds)
        autoStartDelay: 1500,
        
        // Default speech rate for tutorial voices (0.1 to 10)
        speechRate: 1.0,
        
        // Default speech pitch for tutorial voices (0 to 2)
        speechPitch: 1.0,
        
        // Default speech volume for tutorial voices (0 to 1)
        speechVolume: 1.0,
        
        // Enable verbose mode for more detailed audio descriptions
        verboseMode: true,
        
        // Enable high contrast mode
        highContrastMode: false,
        
        // Font size adjustment (percentage)
        fontSizeAdjustment: 100,
        
        // Focus outline width in pixels
        focusOutlineWidth: 3,
        
        // Focus outline color
        focusOutlineColor: "#2196F3",
    },
    
    /**
     * Keyboard shortcuts configuration
     */
    keyboardShortcuts: {
        startStopTutorial: "ctrl+space",
        toggleTutorial: "alt+t",
        pauseResumeTutorial: "space",
        closeTutorial: "escape",
        skipToContent: "alt+s",
        skipToNavigation: "alt+n",
        skipToSearch: "alt+f",
        readCurrentItem: "alt+r",
        nextItem: "alt+right",
        previousItem: "alt+left",
    },
    
    /**
     * ARIA live region settings
     */
    ariaSettings: {
        // Announcement politeness setting
        announcementMode: "polite", // Options: "off", "polite", "assertive"
        
        // Delay between announcements in milliseconds
        announcementDelay: 300,
        
        // Whether to announce page changes
        announcePageChanges: true,
        
        // Whether to announce cart updates
        announceCartUpdates: true,
        
        // Whether to announce search results
        announceSearchResults: true,
    },
    
    /**
     * Tutorial content configuration
     */
    tutorial: {
        // Tutorial sections
        sections: [
            {
                id: "welcome",
                title: "Welcome to VocalCart",
                content: "Welcome to VocalCart, an accessible shopping assistant. This tutorial will guide you through using the application."
            },
            {
                id: "voice-commands",
                title: "Voice Commands",
                content: "You can control VocalCart using voice commands. To search for products, say 'find' followed by what you're looking for. For example, 'find shoes under 2000'."
            },
            {
                id: "navigation",
                title: "Navigation",
                content: "To navigate through search results, say 'next' or 'previous'. You can also say 'repeat' to hear the current product again."
            },
            {
                id: "shopping-cart",
                title: "Shopping Cart",
                content: "To add the current product to your cart, say 'add to cart'. To review your cart, say 'show my cart'. To checkout, say 'checkout'."
            },
            {
                id: "keyboard",
                title: "Keyboard Navigation",
                content: "You can navigate VocalCart using keyboard shortcuts. Press Tab to move between elements, Enter to select, and Escape to close dialogs."
            },
            {
                id: "help",
                title: "Getting Help",
                content: "For help at any time, press Ctrl+Space to restart this tutorial, or say 'help' for voice assistance."
            }
        ],
        
        // Tutorial specific settings
        startOnFirstVisit: true,
        requireExplicitDismissal: true,
        showProgressIndicator: true,
        allowSkippingSteps: true,
        loopTutorial: false,
        enableTextHighlighting: true
    },
    
    /**
     * Screen reader specific settings
     */
    screenReader: {
        // Additional delay for screen readers in milliseconds
        additionalDelay: 500,
        
        // Whether to use simplified UI for screen readers
        useSimplifiedUI: true,
        
        // Whether to announce hidden content to screen readers
        announceHiddenContent: false,
        
        // Known screen readers for detection
        knownScreenReaders: ["NVDA", "JAWS", "VoiceOver", "Narrator", "Orca"],
        
        // Custom screen reader instructions
        customInstructions: {
            NVDA: "Use NVDA's browse mode to explore the page. Press H to navigate by headings.",
            JAWS: "Use JAWS's virtual cursor to explore the page. Press H to navigate by headings.",
            VoiceOver: "Use VO+Right Arrow to navigate through elements. Use VO+Space to activate buttons.",
            Narrator: "Use Caps Lock+Right Arrow to navigate through elements.",
            Orca: "Use Orca's browse mode to explore the page."
        }
    },
    
    /**
     * Initialize all accessibility features
     */
    init: function() {
        console.log("Initializing VocalCart accessibility features");
        
        // Apply focus styles
        document.documentElement.style.setProperty('--focus-outline-width', this.settings.focusOutlineWidth + 'px');
        document.documentElement.style.setProperty('--focus-outline-color', this.settings.focusOutlineColor);
        
        // Apply font size adjustment if not default
        if (this.settings.fontSizeAdjustment !== 100) {
            document.documentElement.style.setProperty('font-size', this.settings.fontSizeAdjustment + '%');
        }
        
        // Enable high contrast if needed
        if (this.settings.highContrastMode) {
            document.body.classList.add('high-contrast');
        }
        
        // Initialize ARIA live regions
        this.initAriaLiveRegions();
        
        // Attempt to detect screen readers
        this.detectScreenReader();
        
        // Register keyboard shortcuts
        this.registerKeyboardShortcuts();
        
        // Signal that accessibility is ready
        document.dispatchEvent(new CustomEvent('accessibilityReady'));
    },
    
    /**
     * Initialize ARIA live regions for announcements
     */
    initAriaLiveRegions: function() {
        // Create polite announcement region
        let politeRegion = document.getElementById('aria-live-polite');
        if (!politeRegion) {
            politeRegion = document.createElement('div');
            politeRegion.id = 'aria-live-polite';
            politeRegion.setAttribute('aria-live', 'polite');
            politeRegion.setAttribute('role', 'status');
            politeRegion.style.position = 'absolute';
            politeRegion.style.width = '1px';
            politeRegion.style.height = '1px';
            politeRegion.style.overflow = 'hidden';
            politeRegion.style.clip = 'rect(0, 0, 0, 0)';
            document.body.appendChild(politeRegion);
        }
        
        // Create assertive announcement region
        let assertiveRegion = document.getElementById('aria-live-assertive');
        if (!assertiveRegion) {
            assertiveRegion = document.createElement('div');
            assertiveRegion.id = 'aria-live-assertive';
            assertiveRegion.setAttribute('aria-live', 'assertive');
            assertiveRegion.setAttribute('role', 'alert');
            assertiveRegion.style.position = 'absolute';
            assertiveRegion.style.width = '1px';
            assertiveRegion.style.height = '1px';
            assertiveRegion.style.overflow = 'hidden';
            assertiveRegion.style.clip = 'rect(0, 0, 0, 0)';
            document.body.appendChild(assertiveRegion);
        }
    },
    
    /**
     * Attempt to detect screen readers
     */
    detectScreenReader: function() {
        // Detection is imperfect, but we can look for common signs
        this.usingScreenReader = false;
        
        // Check for common screen reader detection methods
        if (navigator.userAgent.includes("JAWS") || 
            navigator.userAgent.includes("NVDA") || 
            navigator.userAgent.includes("VoiceOver") || 
            navigator.userAgent.includes("Narrator") || 
            navigator.userAgent.includes("Orca")) {
            this.usingScreenReader = true;
            console.log("Screen reader detected via user agent");
        }
        
        // Add a hidden element that screen readers might access
        const hiddenProbe = document.createElement('div');
        hiddenProbe.setAttribute('id', 'screen-reader-detection');
        hiddenProbe.setAttribute('aria-hidden', 'false');
        hiddenProbe.style.position = 'absolute';
        hiddenProbe.style.width = '1px';
        hiddenProbe.style.height = '1px';
        hiddenProbe.style.overflow = 'hidden';
        hiddenProbe.style.clip = 'rect(0, 0, 0, 0)';
        document.body.appendChild(hiddenProbe);
        
        // Listen for focus on the hidden element (some screen readers might focus it)
        hiddenProbe.addEventListener('focus', () => {
            this.usingScreenReader = true;
            console.log("Screen reader detected via focus event");
        });
        
        // Use a MutationObserver as some screen readers may modify the DOM
        const observer = new MutationObserver((mutations) => {
            for (const mutation of mutations) {
                if (mutation.type === 'childList' || mutation.type === 'attributes') {
                    this.usingScreenReader = true;
                    observer.disconnect();
                    console.log("Screen reader detected via DOM mutation");
                    break;
                }
            }
        });
        
        observer.observe(hiddenProbe, {
            attributes: true,
            childList: true,
            subtree: true
        });
        
        // Set a flag for high probability of screen reader usage based on accessibility features
        if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
            this.probableScreenReaderUser = true;
        }
        
        // Final check: if 'accessibility' is in the URL params, assume screen reader
        if (window.location.href.includes('accessibility=true') || 
            window.location.href.includes('screenreader=true')) {
            this.usingScreenReader = true;
        }
        
        // Start auto tutorial if screen reader is detected
        if (this.usingScreenReader && this.settings.autoStartTutorial) {
            setTimeout(() => {
                console.log("Auto-starting tutorial for screen reader user");
                document.dispatchEvent(new CustomEvent('startAccessibilityTutorial'));
            }, this.settings.autoStartDelay);
        }
    },
    
    /**
     * Register keyboard shortcuts for accessibility features
     */
    registerKeyboardShortcuts: function() {
        document.addEventListener('keydown', (e) => {
            // Start/stop tutorial shortcut
            if (e.ctrlKey && e.code === 'Space') {
                e.preventDefault();
                document.dispatchEvent(new CustomEvent('toggleAccessibilityTutorial'));
            }
            
            // Toggle tutorial visibility
            if (e.altKey && e.key.toLowerCase() === 't') {
                e.preventDefault();
                document.dispatchEvent(new CustomEvent('toggleAccessibilityTutorial'));
            }
            
            // Skip to main content
            if (e.altKey && e.key.toLowerCase() === 's') {
                e.preventDefault();
                const mainContent = document.querySelector('main') || document.getElementById('main-content');
                if (mainContent) {
                    mainContent.focus();
                }
            }
            
            // Skip to navigation
            if (e.altKey && e.key.toLowerCase() === 'n') {
                e.preventDefault();
                const nav = document.querySelector('nav') || document.getElementById('main-nav');
                if (nav) {
                    nav.focus();
                }
            }
            
            // Skip to search
            if (e.altKey && e.key.toLowerCase() === 'f') {
                e.preventDefault();
                const search = document.querySelector('#search-input') || document.querySelector('input[type="search"]');
                if (search) {
                    search.focus();
                }
            }
        });
    },
    
    /**
     * Make an announcement via ARIA live region
     * @param {string} message - The message to announce
     * @param {string} priority - Either 'polite' or 'assertive'
     */
    announce: function(message, priority = 'polite') {
        if (this.ariaSettings.announcementMode === 'off') return;
        
        if (priority !== 'assertive' || this.ariaSettings.announcementMode === 'assertive') {
            const region = document.getElementById(priority === 'assertive' ? 'aria-live-assertive' : 'aria-live-polite');
            if (region) {
                // Clear the region first
                region.textContent = '';
                
                // Use timeout to ensure screen readers announce the new content
                setTimeout(() => {
                    region.textContent = message;
                }, this.ariaSettings.announcementDelay);
            }
        }
    },
    
    /**
     * Check if the user is likely using a screen reader
     * @returns {boolean}
     */
    isUsingScreenReader: function() {
        return this.usingScreenReader || this.probableScreenReaderUser;
    }
};

// Initialize accessibility features when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    VocalCartAccessibility.init();
});
