// =================================
// مدیریت رابط کاربری و تعامل (UI & Interaction Management)
// =================================

// Toggle sidebar on mobile
function toggleSidebar() {
    console.log('toggleSidebar function called');
    
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebar-overlay');
    
    console.log('Sidebar element:', sidebar);
    console.log('Overlay element:', overlay);
    
    // Only toggle sidebar on mobile devices
    if (window.innerWidth >= 768) {
        console.log('Not toggling sidebar on desktop');
        return;
    }
    
    // On mobile devices, prevent sidebar from showing
    if (sidebar) {
        // Remove show class to ensure sidebar stays hidden on mobile
        sidebar.classList.remove('show');
        console.log('Sidebar show class removed on mobile. Current classes:', sidebar.className);
    } else {
        console.error('Sidebar element not found');
    }
    
    if (overlay) {
        // Remove show class to ensure overlay stays hidden on mobile
        overlay.classList.remove('show');
        console.log('Overlay show class removed on mobile. Current classes:', overlay.className);
    } else {
        console.error('Overlay element not found');
    }
    
    console.log('toggleSidebar function completed - sidebar and overlay remain hidden on mobile');
}

// Toggle sessions list visibility
function toggleSessionsList() {
    const sessionsContainer = document.getElementById('sessions-container');
    const toggleBtn = document.getElementById('toggle-sessions');
    const icon = toggleBtn.querySelector('i');
    
    if (sessionsContainer.classList.contains('collapsed')) {
        // Show sessions
        sessionsContainer.classList.remove('collapsed');
        sessionsContainer.style.display = 'block';
        icon.className = 'fas fa-chevron-up';
        toggleBtn.title = 'جمع کردن چت‌ها';
    } else {
        // Hide sessions
        sessionsContainer.classList.add('collapsed');
        sessionsContainer.style.display = 'none';
        icon.className = 'fas fa-chevron-down';
        toggleBtn.title = 'باز کردن چت‌ها';
    }
}

// Check if both chatbot and model are selected in modal
function checkModalSelections() {
    const chatbotSelect = document.getElementById('modal-chatbot-select');
    const modelSelect = document.getElementById('modal-model-select');
    const createBtn = document.getElementById('create-chat-btn');
    
    // Enable button only if both a chatbot and a model are selected
    if (chatbotSelect.value && modelSelect.value) {
        createBtn.disabled = false;
    } else {
        createBtn.disabled = true;
    }
}

// Load sidebar menu items for desktop view
function loadDesktopSidebarMenuItems() {
    const desktopNavMenu = document.getElementById('desktop-nav-menu');
    if (!desktopNavMenu) return;

    fetch(CHAT_URLS.getSidebarMenuItems)
        .then(response => response.json())
        .then(data => {
            desktopNavMenu.innerHTML = ''; // Clear previous items
            if (data.menu_items && data.menu_items.length > 0) {
                data.menu_items.forEach(item => {
                    const navItem = document.createElement('div');
                    navItem.className = 'nav-item';
                    navItem.innerHTML = `
                        <a class="nav-link" href="${item.url}">
                          <i class="${item.icon_class}"></i> ${item.name}
                        </a>
                    `;
                    desktopNavMenu.appendChild(navItem);
                });
            } else {
                // Show default menu items if none are configured
                desktopNavMenu.innerHTML = `
                    <div class="nav-item">
                        <a class="nav-link" href="/chat/">
                            <i class="fas fa-comments"></i> چت
                        </a>
                    </div>
                    <div class="nav-item">
                        <a class="nav-link" href="/accounts/profile/">
                            <i class="fas fa-user"></i> پروفایل
                        </a>
                    </div>
                `;
            }
        })
        .catch(error => {
            console.error('Error loading desktop menu items:', error);
            // Show default menu items if there's an error
            desktopNavMenu.innerHTML = `
                <div class="nav-item">
                    <a class="nav-link" href="/chat/">
                        <i class="fas fa-comments"></i> چت
                    </a>
                </div>
                <div class="nav-item">
                    <a class="nav-link" href="/accounts/profile/">
                        <i class="fas fa-user"></i> پروفایل
                    </a>
                </div>
            `;
        });
}

// Load sidebar menu items for mobile view
function loadSidebarMenuItems() {
    const mobileNavMenu = document.getElementById('mobile-nav-menu');
    if (!mobileNavMenu) return;

    fetch(CHAT_URLS.getSidebarMenuItems)
        .then(response => response.json())
        .then(data => {
            mobileNavMenu.innerHTML = ''; // Clear previous items
            if (data.menu_items && data.menu_items.length > 0) {
                data.menu_items.forEach(item => {
                    const navItem = document.createElement('div');
                    navItem.className = 'nav-item';
                    navItem.innerHTML = `
                        <a class="nav-link" href="${item.url}">
                          <i class="${item.icon_class}"></i> ${item.name}
                        </a>
                    `;
                    mobileNavMenu.appendChild(navItem);
                });
            } else {
                // Show default menu items if none are configured
                mobileNavMenu.innerHTML = `
                    <div class="nav-item">
                        <a class="nav-link" href="/chat/">
                            <i class="fas fa-comments"></i> چت
                        </a>
                    </div>
                    <div class="nav-item">
                        <a class="nav-link" href="/accounts/profile/">
                            <i class="fas fa-user"></i> پروفایل
                        </a>
                    </div>
                `;
            }
        })
        .catch(error => {
            console.error('Error loading menu items:', error);
            // Show default menu items if there's an error
            mobileNavMenu.innerHTML = `
                <div class="nav-item">
                    <a class="nav-link" href="/chat/">
                        <i class="fas fa-comments"></i> چت
                    </a>
                </div>
                <div class="nav-item">
                    <a class="nav-link" href="/accounts/profile/">
                        <i class="fas fa-user"></i> پروفایل
                    </a>
                </div>
            `;
        });
}

// Show loading indicator when creating a new session by clicking the input
function showSessionCreationLoading() {
    const welcomeMessage = document.getElementById('welcome-message');
    if (welcomeMessage) {
        welcomeMessage.innerHTML = `
            <div class="text-center text-muted p-5">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <p class="mt-3 mb-0">در حال ایجاد چت جدید...</p>
            </div>
        `;
    }
    document.getElementById('message-input').placeholder = 'لطفا صبر کنید...';
    document.getElementById('message-input').disabled = true;
    document.getElementById('send-button').disabled = true;
}

// Hide loading indicator after session creation attempt
function hideSessionCreationLoading(success = true) {
    const messageInput = document.getElementById('message-input');
    if(messageInput) {
        messageInput.disabled = false;
        messageInput.placeholder = 'پیام خود را تایپ کنید...';
    }

    // If creation failed, restore the original welcome message
    if (!success) {
        const welcomeMessage = document.getElementById('welcome-message');
        if (welcomeMessage) {
            welcomeMessage.innerHTML = `
                <i class="fas fa-robot fa-3x mb-3"></i>
                <h4>به چت‌بات MobixAI خوش آمدید</h4>
                <p class="mb-0">برای شروع، روی این کادر کلیک کنید تا چت جدیدی ایجاد شود.</p>
            `;
        }
    }
    // If successful, loadSession will handle replacing the welcome message
}

// Export functions to global scope for cross-file access
console.log('Exporting toggleSidebar to global scope');
window.toggleSidebar = toggleSidebar;
console.log('toggleSidebar exported. Type:', typeof window.toggleSidebar);
