/**
 * Auto-starting tutorial for blind users
 * This script ensures the audio tutorial starts automatically when the page loads
 * BUT ONLY IF it hasn't been started by another script
 */

document.addEventListener('DOMContentLoaded', function() {
    // Wait a short time to ensure screen readers have announced the page
    setTimeout(function() {
        // Create and add an announcement element
        const announcement = document.createElement('div');
        announcement.setAttribute('role', 'alert');
        announcement.setAttribute('aria-live', 'assertive');
        announcement.style.position = 'absolute';
        announcement.style.width = '1px';
        announcement.style.height = '1px';
        announcement.style.overflow = 'hidden';
        announcement.textContent = 'Welcome to VocalCart. Press Alt+T to start the audio tutorial.';
        document.body.appendChild(announcement);
        
        // Check if tutorial should auto-start (screen reader detection)
        const shouldAutoStart = checkIfScreenReaderIsActive();
        
        // Only start if we should auto-start AND tutorial hasn't been started yet
        if (shouldAutoStart && window.audioTutorial && !window.tutorialHasStarted) {
            // Show announcement first
            announcement.textContent = 'Welcome to VocalCart. Audio tutorial for blind users is starting automatically.';
            
            // Create and show welcome modal
            if (typeof createWelcomeModal === 'function') {
                createWelcomeModal();
            }
            
            // Wait 2 seconds before actually starting tutorial
            setTimeout(function() {
                // Double-check that tutorial hasn't been started by another script
                if (!window.tutorialHasStarted && window.audioTutorial) {
                    window.audioTutorial.startTutorial();
                    window.tutorialHasStarted = true;
                }
            }, 2000);
        }
        
        // Helper function to detect screen readers
        function checkIfScreenReaderIsActive() {
            // Try to detect screen readers
            const usingScreenReader = 
                navigator.userAgent.includes("JAWS") || 
                navigator.userAgent.includes("NVDA") || 
                navigator.userAgent.includes("VoiceOver") || 
                navigator.userAgent.includes("Narrator") || 
                window.location.href.includes('screenreader=true');
                
            // For demo purposes, return false to prevent auto-start 
            // In production, you would return usingScreenReader
            return false;
        }
        
        // Add keyboard shortcut instructions
        setTimeout(function() {
            announcement.textContent = 'Press Alt+T to restart tutorial anytime. Press Control+Space to activate voice commands.';
        }, 5000);
        
        // Setup quick help mode
        document.addEventListener('keydown', function(e) {
            // ? key for quick help
            if (e.key === '?' || (e.shiftKey && e.key === '/')) {
                const helpText = `
                    VocalCart keyboard shortcuts:
                    Control+Space: Activate voice recognition
                    Alt+T: Start audio tutorial
                    Spacebar: Go to next product
                    Enter on a product: Get product details
                    Escape: Cancel current operation
                `;
                
                announcement.textContent = helpText;
            }
        });
        
    }, 1000);
    
    // Add a warning about navigating away
    window.addEventListener('beforeunload', function(e) {
        const announcement = document.createElement('div');
        announcement.setAttribute('role', 'alert');
        announcement.textContent = 'Warning: You are about to leave VocalCart.';
        document.body.appendChild(announcement);
    });
});
