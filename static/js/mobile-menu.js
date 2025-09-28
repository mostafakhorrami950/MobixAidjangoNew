// Mobile Menu System - Complete Rewrite
console.log('Mobile Menu System Loaded');

// Mobile Menu Class
class MobileMenu {
    constructor() {
        this.isOpen = false;
        this.init();
    }

    init() {
        console.log('Initializing Mobile Menu');
        this.createMenu();
        this.bindEvents();
    }

    // Create the mobile menu structure
    createMenu() {
        console.log('Creating Mobile Menu Structure');
        
        // Create the mobile menu container
        this.menu = document.createElement('div');
        this.menu.id = 'mobile-menu-container';
        this.menu.className = 'mobile-menu-container';
        
        // Create the menu content
        this.menu.innerHTML = `
            <div class="mobile-menu-header">
                <div class="mobile-menu-brand">
                    <i class="fas fa-robot"></i>
                    <span>MobixAI</span>
                </div>
                <button class="mobile-menu-close" id="mobile-menu-close">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div class="mobile-menu-content">
                <div class="mobile-menu-loading">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">در حال بارگذاری...</span>
                    </div>
                    <p>در حال بارگذاری منو...</p>
                </div>
                <div class="mobile-menu-items" id="mobile-menu-items">
                    <!-- Menu items will be loaded here -->
                </div>
            </div>
        `;
        
        // Add menu to body
        document.body.appendChild(this.menu);
        
        console.log('Mobile Menu Created');
    }

    // Bind all events
    bindEvents() {
        console.log('Binding Mobile Menu Events');
        
        // Hamburger menu toggle button
        const hamburgerBtn = document.getElementById('mobile-menu-toggle');
        if (hamburgerBtn) {
            hamburgerBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                console.log('Hamburger button clicked');
                this.toggle();
            });
        }
        
        // Close button
        const closeBtn = document.getElementById('mobile-menu-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                console.log('Close button clicked');
                this.close();
            });
        }
        
        // Overlay click
        const overlay = document.getElementById('mobile-overlay');
        if (overlay) {
            overlay.addEventListener('click', () => {
                console.log('Overlay clicked');
                this.close();
            });
        }
        
        // ESC key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isOpen) {
                console.log('ESC key pressed');
                this.close();
            }
        });
        
        console.log('Mobile Menu Events Bound');
    }

    // Toggle menu open/close
    toggle() {
        console.log('Toggling Mobile Menu');
        if (this.isOpen) {
            this.close();
        } else {
            this.open();
        }
    }

    // Open the menu
    open() {
        console.log('Opening Mobile Menu');
        if (this.isOpen) return;
        
        this.isOpen = true;
        
        // Show menu and overlay
        this.menu.classList.add('open');
        
        const overlay = document.getElementById('mobile-overlay');
        if (overlay) {
            overlay.classList.add('show');
        }
        
        // Check if we're on the chat page
        const isChatPage = window.location.pathname.startsWith('/chat');
        if (isChatPage) {
            // On chat page, load combined menu with sessions
            this.loadChatPageMenu();
        } else {
            // On other pages, load regular menu items
            this.loadMenuItems();
        }
        
        // Prevent body scroll
        document.body.classList.add('mobile-menu-open');
        
        console.log('Mobile Menu Opened');
    }

    // Close the menu
    close() {
        console.log('Closing Mobile Menu');
        if (!this.isOpen) return;
        
        this.isOpen = false;
        
        // Hide menu and overlay
        this.menu.classList.remove('open');
        
        const overlay = document.getElementById('mobile-overlay');
        if (overlay) {
            overlay.classList.remove('show');
        }
        
        // Restore body scroll
        document.body.classList.remove('mobile-menu-open');
        
        console.log('Mobile Menu Closed');
    }

    // Load menu for chat page (combines sessions and menu items)
    loadChatPageMenu() {
        console.log('Loading Chat Page Menu');
        
        const menuItemsContainer = document.getElementById('mobile-menu-items');
        if (!menuItemsContainer) {
            console.error('Menu items container not found');
            return;
        }
        
        // Show loading state
        const loadingElement = this.menu.querySelector('.mobile-menu-loading');
        if (loadingElement) {
            loadingElement.style.display = 'block';
        }
        
        // Clear existing items
        menuItemsContainer.innerHTML = '';
        
        // Create sections container
        const sectionsContainer = document.createElement('div');
        sectionsContainer.className = 'mobile-menu-sections';
        
        // Create sessions section
        const sessionsSection = document.createElement('div');
        sessionsSection.className = 'mobile-menu-section';
        sessionsSection.innerHTML = `
            <div class="mobile-menu-section-header">
                <h3>چت‌های من</h3>
                <button class="btn btn-sm btn-primary" id="mobile-new-chat-btn">
                    <i class="fas fa-plus"></i> چت جدید
                </button>
            </div>
            <div class="mobile-menu-section-content" id="mobile-sessions-list">
                <div class="text-center p-3">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">در حال بارگذاری...</span>
                    </div>
                </div>
            </div>
        `;
        
        // Create menu items section
        const menuSection = document.createElement('div');
        menuSection.className = 'mobile-menu-section';
        menuSection.innerHTML = `
            <div class="mobile-menu-section-header">
                <h3>منو</h3>
            </div>
            <div class="mobile-menu-section-content" id="mobile-menu-list">
                <div class="text-center p-3">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">در حال بارگذاری...</span>
                    </div>
                </div>
            </div>
        `;
        
        sectionsContainer.appendChild(sessionsSection);
        sectionsContainer.appendChild(menuSection);
        menuItemsContainer.appendChild(sectionsContainer);
        
        // Load sessions
        this.loadChatSessions();
        
        // Load menu items
        this.loadMenuItemsForChatPage();
    }

    // Load chat sessions for chat page menu
    loadChatSessions() {
        console.log('Loading Chat Sessions');
        
        const sessionsList = document.getElementById('mobile-sessions-list');
        if (!sessionsList) {
            console.error('Sessions list container not found');
            return;
        }
        
        // Fetch sessions from the server
        fetch('/chat/sessions/')
            .then(response => response.json())
            .then(data => {
                console.log('Sessions loaded:', data);
                
                // Clear loading state
                sessionsList.innerHTML = '';
                
                // Add sessions
                if (data.sessions && data.sessions.length > 0) {
                    data.sessions.forEach(session => {
                        const sessionItem = this.createSessionItem(session);
                        sessionsList.appendChild(sessionItem);
                    });
                } else {
                    // No sessions message
                    sessionsList.innerHTML = `
                        <div class="mobile-menu-item empty">
                            <div class="text-center p-3 text-muted">
                                <i class="fas fa-comment-slash fa-2x mb-2"></i>
                                <p class="mb-0">هیچ چتی وجود ندارد</p>
                            </div>
                        </div>
                    `;
                }
                
                // Add new chat button event
                const newChatBtn = document.getElementById('mobile-new-chat-btn');
                if (newChatBtn) {
                    newChatBtn.addEventListener('click', () => {
                        this.close();
                        // Trigger the new chat button in the main interface
                        const mainNewChatBtn = document.getElementById('new-chat-btn');
                        if (mainNewChatBtn) {
                            mainNewChatBtn.click();
                        }
                    });
                }
            })
            .catch(error => {
                console.error('Error loading sessions:', error);
                sessionsList.innerHTML = `
                    <div class="mobile-menu-item error">
                        <div class="text-center p-3 text-danger">
                            <i class="fas fa-exclamation-triangle fa-2x mb-2"></i>
                            <p class="mb-0">خطا در بارگذاری چت‌ها</p>
                        </div>
                    </div>
                `;
            });
    }

    // Load menu items for chat page
    loadMenuItemsForChatPage() {
        console.log('Loading Menu Items for Chat Page');
        
        const menuList = document.getElementById('mobile-menu-list');
        if (!menuList) {
            console.error('Menu list container not found');
            return;
        }
        
        // Fetch menu items from the server
        fetch('/chat/sidebar-menu-items/')
            .then(response => response.json())
            .then(data => {
                console.log('Menu items loaded:', data);
                
                // Hide loading state
                const loadingElement = this.menu.querySelector('.mobile-menu-loading');
                if (loadingElement) {
                    loadingElement.style.display = 'none';
                }
                
                // Check if user is authenticated
                const isAuthenticated = document.body.dataset.authenticated === 'true';
                
                // Clear existing items
                menuList.innerHTML = '';
                
                // Add menu items
                if (data.menu_items && data.menu_items.length > 0) {
                    data.menu_items.forEach(item => {
                        // Skip items based on authentication status
                        if (item.show_only_for_authenticated && !isAuthenticated) {
                            return;
                        }
                        
                        if (item.show_only_for_non_authenticated && isAuthenticated) {
                            return;
                        }
                        
                        const menuItem = this.createMenuItem(item);
                        menuList.appendChild(menuItem);
                    });
                } else {
                    // Show default menu items
                    this.showDefaultMenuItemsForChatPage(menuList);
                }
            })
            .catch(error => {
                console.error('Error loading menu items:', error);
                this.showDefaultMenuItemsForChatPage(menuList);
            });
    }

    // Create a session item element
    createSessionItem(session) {
        const sessionItem = document.createElement('div');
        sessionItem.className = 'mobile-menu-item session-item';
        sessionItem.dataset.sessionId = session.id;
        
        // Truncate title if too long
        const truncatedTitle = session.title.length > 30 ? session.title.substring(0, 30) + '...' : session.title;
        
        sessionItem.innerHTML = `
            <a href="/chat/session/${session.id}/" class="mobile-menu-link">
                <div class="session-info">
                    <div class="session-title">${truncatedTitle}</div>
                    <div class="session-meta">
                        <span class="session-date">${new Date(session.updated_at).toLocaleDateString('fa-IR')}</span>
                        <span class="session-count">${session.message_count} پیام</span>
                    </div>
                </div>
            </a>
        `;
        
        return sessionItem;
    }

    // Load menu items from server (regular pages)
    loadMenuItems() {
        console.log('Loading Menu Items');
        
        const menuItemsContainer = document.getElementById('mobile-menu-items');
        if (!menuItemsContainer) {
            console.error('Menu items container not found');
            return;
        }
        
        // Fetch menu items from the server
        fetch('/chat/sidebar-menu-items/')
            .then(response => response.json())
            .then(data => {
                console.log('Menu items loaded:', data);
                
                // Hide loading state
                const loadingElement = this.menu.querySelector('.mobile-menu-loading');
                if (loadingElement) {
                    loadingElement.style.display = 'none';
                }
                
                // Check if user is authenticated
                const isAuthenticated = document.body.dataset.authenticated === 'true';
                
                // Clear existing items
                menuItemsContainer.innerHTML = '';
                
                // Add menu items
                if (data.menu_items && data.menu_items.length > 0) {
                    data.menu_items.forEach(item => {
                        // Skip items based on authentication status
                        if (item.show_only_for_authenticated && !isAuthenticated) {
                            return;
                        }
                        
                        if (item.show_only_for_non_authenticated && isAuthenticated) {
                            return;
                        }
                        
                        const menuItem = this.createMenuItem(item);
                        menuItemsContainer.appendChild(menuItem);
                    });
                } else {
                    // Show default menu items
                    this.showDefaultMenuItems(menuItemsContainer);
                }
            })
            .catch(error => {
                console.error('Error loading menu items:', error);
                this.showDefaultMenuItems(menuItemsContainer);
            });
    }

    // Create a menu item element
    createMenuItem(item) {
        const menuItem = document.createElement('div');
        menuItem.className = 'mobile-menu-item';
        
        menuItem.innerHTML = `
            <a href="${item.url}" class="mobile-menu-link">
                <i class="${item.icon_class}"></i>
                <span>${item.name}</span>
            </a>
        `;
        
        return menuItem;
    }

    // Show default menu items when API fails (regular pages)
    showDefaultMenuItems(container) {
        console.log('Showing default menu items');
        
        // Hide loading state
        const loadingElement = this.menu.querySelector('.mobile-menu-loading');
        if (loadingElement) {
            loadingElement.style.display = 'none';
        }
        
        // Clear container
        container.innerHTML = '';
        
        // Check if user is authenticated
        const isAuthenticated = document.body.dataset.authenticated === 'true';
        
        // Default menu items
        const defaultItems = [
            { name: 'خانه', url: '/', icon_class: 'fas fa-home' },
            { name: 'چت', url: '/chat/', icon_class: 'fas fa-comments' }
        ];
        
        if (isAuthenticated) {
            defaultItems.push(
                { name: 'داشبورد', url: '/dashboard/', icon_class: 'fas fa-tachometer-alt' },
                { name: 'تراکنش‌های مالی', url: '/financial-transactions/', icon_class: 'fas fa-credit-card' },
                { name: 'خرید اشتراک', url: '/subscriptions/purchase/', icon_class: 'fas fa-shopping-cart' },
                { name: 'خروج', url: '/accounts/logout/', icon_class: 'fas fa-sign-out-alt' }
            );
        } else {
            defaultItems.push(
                { name: 'ورود', url: '/accounts/login/', icon_class: 'fas fa-sign-in-alt' }
            );
        }
        
        // Create menu items
        defaultItems.forEach(item => {
            const menuItem = this.createMenuItem(item);
            container.appendChild(menuItem);
        });
    }

    // Show default menu items when API fails (chat page)
    showDefaultMenuItemsForChatPage(container) {
        console.log('Showing default menu items for chat page');
        
        // Hide loading state
        const loadingElement = this.menu.querySelector('.mobile-menu-loading');
        if (loadingElement) {
            loadingElement.style.display = 'none';
        }
        
        // Clear container
        container.innerHTML = '';
        
        // Check if user is authenticated
        const isAuthenticated = document.body.dataset.authenticated === 'true';
        
        // Default menu items
        const defaultItems = [
            { name: 'داشبورد', url: '/dashboard/', icon_class: 'fas fa-tachometer-alt' },
            { name: 'تراکنش‌های مالی', url: '/financial-transactions/', icon_class: 'fas fa-credit-card' },
            { name: 'خرید اشتراک', url: '/subscriptions/purchase/', icon_class: 'fas fa-shopping-cart' }
        ];
        
        if (isAuthenticated) {
            defaultItems.push(
                { name: 'خروج', url: '/accounts/logout/', icon_class: 'fas fa-sign-out-alt' }
            );
        } else {
            defaultItems.push(
                { name: 'ورود', url: '/accounts/login/', icon_class: 'fas fa-sign-in-alt' }
            );
        }
        
        // Create menu items
        defaultItems.forEach(item => {
            const menuItem = this.createMenuItem(item);
            container.appendChild(menuItem);
        });
    }
}

// Initialize mobile menu when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM Loaded - Initializing Mobile Menu System');
    window.mobileMenu = new MobileMenu();
});

// Export for global access
window.MobileMenu = MobileMenu;