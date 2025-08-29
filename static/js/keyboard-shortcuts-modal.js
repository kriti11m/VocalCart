/**
 * Keyboard Shortcuts Help Modal for VocalCart
 * This script creates and manages a modal dialog showing keyboard shortcuts
 */

class KeyboardShortcutsModal {
    constructor() {
        this.modalId = 'keyboard-shortcuts-modal';
        this.isOpen = false;
        this.createModal();
        this.registerEvents();
    }

    /**
     * Create the modal HTML structure
     */
    createModal() {
        // Create the modal elements
        const modal = document.createElement('div');
        modal.id = this.modalId;
        modal.className = 'keyboard-modal';
        modal.setAttribute('role', 'dialog');
        modal.setAttribute('aria-labelledby', 'keyboard-shortcuts-title');
        modal.setAttribute('aria-modal', 'true');
        modal.setAttribute('tabindex', '-1');
        modal.style.display = 'none';

        // Create the modal overlay
        const overlay = document.createElement('div');
        overlay.className = 'keyboard-modal-overlay';
        overlay.id = `${this.modalId}-overlay`;
        overlay.style.display = 'none';

        // Create the modal content
        modal.innerHTML = `
            <div class="keyboard-modal-header">
                <h2 id="keyboard-shortcuts-title" class="keyboard-modal-title">Keyboard Shortcuts</h2>
                <button type="button" class="keyboard-modal-close" aria-label="Close keyboard shortcuts" id="${this.modalId}-close">×</button>
            </div>
            <div class="keyboard-modal-body">
                <table style="width: 100%; border-collapse: collapse;">
                    <thead>
                        <tr>
                            <th style="text-align: left; padding: 8px; border-bottom: 1px solid #ddd;">Shortcut</th>
                            <th style="text-align: left; padding: 8px; border-bottom: 1px solid #ddd;">Action</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td style="padding: 8px; border-bottom: 1px solid #eee;"><kbd>Ctrl</kbd> + <kbd>Space</kbd></td>
                            <td style="padding: 8px; border-bottom: 1px solid #eee;">Start/stop tutorial</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px; border-bottom: 1px solid #eee;"><kbd>Alt</kbd> + <kbd>T</kbd></td>
                            <td style="padding: 8px; border-bottom: 1px solid #eee;">Toggle tutorial</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px; border-bottom: 1px solid #eee;"><kbd>Space</kbd></td>
                            <td style="padding: 8px; border-bottom: 1px solid #eee;">Pause/resume tutorial</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px; border-bottom: 1px solid #eee;"><kbd>Esc</kbd></td>
                            <td style="padding: 8px; border-bottom: 1px solid #eee;">Close dialogs or modals</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px; border-bottom: 1px solid #eee;"><kbd>Alt</kbd> + <kbd>S</kbd></td>
                            <td style="padding: 8px; border-bottom: 1px solid #eee;">Skip to main content</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px; border-bottom: 1px solid #eee;"><kbd>Alt</kbd> + <kbd>N</kbd></td>
                            <td style="padding: 8px; border-bottom: 1px solid #eee;">Skip to navigation</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px; border-bottom: 1px solid #eee;"><kbd>Alt</kbd> + <kbd>F</kbd></td>
                            <td style="padding: 8px; border-bottom: 1px solid #eee;">Focus search input</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px; border-bottom: 1px solid #eee;"><kbd>Alt</kbd> + <kbd>R</kbd></td>
                            <td style="padding: 8px; border-bottom: 1px solid #eee;">Read current item</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px; border-bottom: 1px solid #eee;"><kbd>Alt</kbd> + <kbd>Right Arrow</kbd></td>
                            <td style="padding: 8px; border-bottom: 1px solid #eee;">Next item</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px; border-bottom: 1px solid #eee;"><kbd>Alt</kbd> + <kbd>Left Arrow</kbd></td>
                            <td style="padding: 8px; border-bottom: 1px solid #eee;">Previous item</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px; border-bottom: 1px solid #eee;"><kbd>Alt</kbd> + <kbd>H</kbd></td>
                            <td style="padding: 8px; border-bottom: 1px solid #eee;">Show keyboard shortcuts (this dialog)</td>
                        </tr>
                    </tbody>
                </table>
            </div>
            <div class="keyboard-modal-footer">
                <button type="button" class="primary-button" id="${this.modalId}-close-btn">Close</button>
            </div>
        `;

        // Append the modal and overlay to the body
        document.body.appendChild(overlay);
        document.body.appendChild(modal);
    }

    /**
     * Register event listeners for the modal
     */
    registerEvents() {
        // Close button event
        const closeButton = document.getElementById(`${this.modalId}-close`);
        const closeButtonFooter = document.getElementById(`${this.modalId}-close-btn`);
        const overlay = document.getElementById(`${this.modalId}-overlay`);

        if (closeButton) {
            closeButton.addEventListener('click', () => this.close());
        }

        if (closeButtonFooter) {
            closeButtonFooter.addEventListener('click', () => this.close());
        }

        if (overlay) {
            overlay.addEventListener('click', () => this.close());
        }

        // Keyboard events
        document.addEventListener('keydown', (e) => {
            // Close on escape key
            if (e.key === 'Escape' && this.isOpen) {
                this.close();
            }

            // Open on Alt+H
            if (e.altKey && e.key.toLowerCase() === 'h') {
                e.preventDefault();
                this.toggle();
            }
        });
    }

    /**
     * Open the keyboard shortcuts modal
     */
    open() {
        if (this.isOpen) return;

        const modal = document.getElementById(this.modalId);
        const overlay = document.getElementById(`${this.modalId}-overlay`);

        if (modal && overlay) {
            // Show the modal and overlay
            modal.style.display = 'block';
            overlay.style.display = 'block';

            // Focus the modal
            modal.focus();

            // Save the previously focused element
            this.previouslyFocused = document.activeElement;

            // Set up focus trapping
            this.setupFocusTrap(modal);

            // Announce to screen readers
            this.announceForScreenReaders('Keyboard shortcuts dialog opened');

            this.isOpen = true;
        }
    }

    /**
     * Close the keyboard shortcuts modal
     */
    close() {
        if (!this.isOpen) return;

        const modal = document.getElementById(this.modalId);
        const overlay = document.getElementById(`${this.modalId}-overlay`);

        if (modal && overlay) {
            // Hide the modal and overlay
            modal.style.display = 'none';
            overlay.style.display = 'none';

            // Return focus to the previously focused element
            if (this.previouslyFocused) {
                this.previouslyFocused.focus();
            }

            // Announce to screen readers
            this.announceForScreenReaders('Keyboard shortcuts dialog closed');

            this.isOpen = false;
        }
    }

    /**
     * Toggle the keyboard shortcuts modal
     */
    toggle() {
        if (this.isOpen) {
            this.close();
        } else {
            this.open();
        }
    }

    /**
     * Set up focus trapping within the modal
     * @param {HTMLElement} modal - The modal element
     */
    setupFocusTrap(modal) {
        // Get all focusable elements
        const focusableElements = modal.querySelectorAll(
            'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );

        if (focusableElements.length > 0) {
            const firstElement = focusableElements[0];
            const lastElement = focusableElements[focusableElements.length - 1];

            // Focus the first element
            firstElement.focus();

            // Handle tab key to trap focus
            modal.addEventListener('keydown', (e) => {
                if (e.key === 'Tab') {
                    if (e.shiftKey) {
                        // Shift + Tab: If on first element, go to last element
                        if (document.activeElement === firstElement) {
                            e.preventDefault();
                            lastElement.focus();
                        }
                    } else {
                        // Tab: If on last element, go to first element
                        if (document.activeElement === lastElement) {
                            e.preventDefault();
                            firstElement.focus();
                        }
                    }
                }
            });
        }
    }

    /**
     * Announce a message for screen readers
     * @param {string} message - The message to announce
     */
    announceForScreenReaders(message) {
        // Use the VocalCartAccessibility utility if available
        if (window.VocalCartAccessibility && typeof window.VocalCartAccessibility.announce === 'function') {
            window.VocalCartAccessibility.announce(message, 'assertive');
        } else {
            // Fallback to creating our own announcement
            const announcer = document.getElementById('sr-announcements');
            if (announcer) {
                announcer.textContent = message;
            }
        }
    }
}

// Initialize the keyboard shortcuts modal when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.keyboardShortcutsModal = new KeyboardShortcutsModal();
    
    // Add a help button to the header
    const header = document.querySelector('.header');
    if (header) {
        const helpButton = document.createElement('button');
        helpButton.className = 'keyboard-help-button';
        helpButton.setAttribute('aria-label', 'Show keyboard shortcuts');
        helpButton.innerHTML = '⌨️ Keyboard Shortcuts';
        helpButton.style.background = 'rgba(255, 255, 255, 0.2)';
        helpButton.style.border = 'none';
        helpButton.style.borderRadius = '4px';
        helpButton.style.padding = '8px 12px';
        helpButton.style.cursor = 'pointer';
        helpButton.style.marginTop = '10px';
        helpButton.style.fontSize = '0.9em';
        
        helpButton.addEventListener('click', () => {
            if (window.keyboardShortcutsModal) {
                window.keyboardShortcutsModal.open();
            }
        });
        
        header.appendChild(helpButton);
    }
});
