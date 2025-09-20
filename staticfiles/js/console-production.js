// =================================
// Production-Safe Console Utility
// =================================

(function() {
    'use strict';
    
    // Check if we're in production (you can customize this logic)
    const isProduction = window.location.hostname !== 'localhost' && 
                         window.location.hostname !== '127.0.0.1' && 
                         !window.location.hostname.includes('dev');
    
    if (isProduction) {
        // Override console methods in production
        const noop = function() {};
        
        // Keep error logging but remove the rest
        console.log = noop;
        console.warn = noop;
        console.info = noop;
        console.debug = noop;
        
        // Keep console.error for critical issues (you might want to send these to a logging service)
        const originalError = console.error;
        console.error = function(...args) {
            // In a real production setup, you might send this to a logging service
            // For now, we'll keep it but could enhance it later
            originalError.apply(console, args);
        };
    }
    
    // Export a safe logger that respects production settings
    window.safeLog = {
        log: function(...args) {
            if (!isProduction) {
                console.log(...args);
            }
        },
        error: function(...args) {
            console.error(...args);
        },
        warn: function(...args) {
            if (!isProduction) {
                console.warn(...args);
            }
        },
        info: function(...args) {
            if (!isProduction) {
                console.info(...args);
            }
        }
    };
})();