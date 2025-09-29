// Mobile menu functionality
document.addEventListener('DOMContentLoaded', function() {
    console.log('Mobile menu JavaScript loaded');
    
    // Mobile menu elements
    const mobileMenuToggle = document.getElementById('mobile-menu-toggle');
    const mobileMenuContainer = document.getElementById('mobile-menu-container');
    const mobileMenuClose = document.getElementById('mobile-menu-close');
    const mobileOverlay = document.getElementById('mobile-overlay');
    
    // Function to toggle mobile menu
    function toggleMobileMenu() {
        if (mobileMenuContainer) {
            mobileMenuContainer.classList.toggle('open');
            document.body.classList.toggle('mobile-menu-open');
            if (mobileOverlay) {
                mobileOverlay.classList.toggle('show');
            }
        }
    }
    
    // Function to close mobile menu
    function closeMobileMenu() {
        if (mobileMenuContainer) {
            mobileMenuContainer.classList.remove('open');
            document.body.classList.remove('mobile-menu-open');
            if (mobileOverlay) {
                mobileOverlay.classList.remove('show');
            }
        }
    }
    
    // Event listeners for mobile menu
    if (mobileMenuToggle) {
        mobileMenuToggle.addEventListener('click', function(e) {
            // Check if we're on the chat page
            const isChatPage = window.location.pathname.startsWith('/chat');
            
            if (isChatPage) {
                // On chat page, prevent default behavior - let the chat page handle it
                e.preventDefault();
                e.stopPropagation();
                return;
            }
            
            // Toggle mobile menu on non-chat pages
            toggleMobileMenu();
        });
    }
    
    if (mobileMenuClose) {
        mobileMenuClose.addEventListener('click', closeMobileMenu);
    }
    
    if (mobileOverlay) {
        mobileOverlay.addEventListener('click', closeMobileMenu);
    }
    
    // Close mobile menu when pressing Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && mobileMenuContainer && mobileMenuContainer.classList.contains('open')) {
            closeMobileMenu();
        }
    });
    
    // Close mobile menu when clicking on links inside it
    if (mobileMenuContainer) {
        mobileMenuContainer.addEventListener('click', function(e) {
            // Check if the clicked element is a link
            if (e.target.tagName === 'A' || e.target.closest('a')) {
                // Small delay to allow the click to register before closing
                setTimeout(closeMobileMenu, 100);
            }
        });
    }
});