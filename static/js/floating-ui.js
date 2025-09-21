// Floating UI Components for Chat Page
document.addEventListener('DOMContentLoaded', function() {
    // Initialize floating components
    initFloatingComponents();
    
    // Handle mobile new chat button
    initMobileNewChatButton();
    
    // Handle floating model selection
    initFloatingModelSelection();
    
    // Load sidebar menu items for all devices
    loadSidebarMenuItems();
});

// Initialize floating components
function initFloatingComponents() {
    // Show/hide components based on page state
    const isOnChatPage = window.location.pathname.startsWith('/chat');
    
    // Only show floating components on chat page
    if (!isOnChatPage) {
        const floatingModelSelection = document.getElementById('floating-model-selection');
        const mobileNewChatBtn = document.getElementById('mobile-new-chat-btn');
        
        if (floatingModelSelection) floatingModelSelection.style.display = 'none';
        if (mobileNewChatBtn) mobileNewChatBtn.style.display = 'none';
    }
}

// Initialize mobile new chat button
function initMobileNewChatButton() {
    const mobileNewChatBtn = document.getElementById('mobile-new-chat-btn');
    const newChatBtn = document.getElementById('new-chat-btn');
    
    if (mobileNewChatBtn && newChatBtn) {
        mobileNewChatBtn.addEventListener('click', function() {
            // Trigger the original new chat button click
            newChatBtn.click();
        });
    }
}

// Initialize floating model selection
function initFloatingModelSelection() {
    const floatingModelSelect = document.getElementById('floating-model-select');
    const originalModelSelect = document.getElementById('model-select');
    
    if (floatingModelSelect && originalModelSelect) {
        // Initially hide floating model selection if no active chat
        const chatContainer = document.getElementById('chat-container');
        const welcomeMessage = document.getElementById('welcome-message');
        
        if (welcomeMessage && welcomeMessage.style.display !== 'none') {
            document.getElementById('floating-model-selection').style.display = 'none';
        }
        
        // Copy options from original model select to floating model select
        function syncModelOptions() {
            // Clear existing options
            floatingModelSelect.innerHTML = '';
            
            // Copy options from original select
            Array.from(originalModelSelect.options).forEach(option => {
                const newOption = document.createElement('option');
                newOption.value = option.value;
                newOption.text = option.text;
                newOption.selected = option.selected;
                floatingModelSelect.appendChild(newOption);
            });
            
            // Show floating model selection if original is visible
            if (originalModelSelect.style.display !== 'none') {
                document.getElementById('floating-model-selection').style.display = 'flex';
            } else {
                document.getElementById('floating-model-selection').style.display = 'none';
            }
        }
        
        // Initial sync
        if (originalModelSelect) {
            // Use MutationObserver to watch for changes in the original select
            const observer = new MutationObserver(function(mutations) {
                syncModelOptions();
            });
            
            observer.observe(originalModelSelect, { 
                attributes: true, 
                childList: true,
                subtree: true
            });
            
            // Also sync when options are loaded
            syncModelOptions();
        }
        
        // Sync selections between the two dropdowns
        floatingModelSelect.addEventListener('change', function() {
            if (originalModelSelect) {
                originalModelSelect.value = floatingModelSelect.value;
                
                // Trigger change event on original select
                const event = new Event('change', { bubbles: true });
                originalModelSelect.dispatchEvent(event);
            }
        });
    }
}

// Load sidebar menu items for all devices
function loadSidebarMenuItems() {
    const sidebarNavMenu = document.getElementById('sidebar-nav-menu');
    
    if (!sidebarNavMenu) {
        return;
    }
    
    // Fetch menu items from the server
    fetch('/chat/sidebar-menu-items/')
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error('Error loading menu items:', data.error);
                return;
            }
            
            // Clear loading state
            sidebarNavMenu.innerHTML = '';
            
            // Check if user is authenticated
            const isAuthenticated = document.body.dataset.authenticated === 'true';
            
            // Add menu items
            if (data.menu_items && data.menu_items.length > 0) {
                // Create a nav list container
                const navList = document.createElement('div');
                navList.className = 'sidebar-nav-list';
                
                data.menu_items.forEach(item => {
                    // Skip items that should only be shown to authenticated users if user is not authenticated
                    if (item.show_only_for_authenticated && !isAuthenticated) {
                        return;
                    }
                    
                    // Skip items that should only be shown to non-authenticated users if user is authenticated
                    if (item.show_only_for_non_authenticated && isAuthenticated) {
                        return;
                    }
                    
                    const navItem = document.createElement('a');
                    navItem.href = item.url;
                    navItem.className = 'sidebar-nav-item';
                    
                    // Special handling for logout to show user name
                    let itemName = item.name;
                    if (item.name === 'خروج' && document.body.dataset.userName) {
                        itemName = `خروج (${document.body.dataset.userName})`;
                    }
                    
                    navItem.innerHTML = `
                        <i class="${item.icon_class}"></i>
                        <span>${itemName}</span>
                    `;
                    
                    navList.appendChild(navItem);
                });
                
                sidebarNavMenu.appendChild(navList);
            }
        })
        .catch(error => {
            console.error('Error loading menu items:', error);
        });
}