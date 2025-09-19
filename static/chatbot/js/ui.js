// =================================
// مدیریت رابط کاربری و تعامل (UI & Interaction Management)
// =================================

// Toggle sidebar on mobile
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebar-overlay');
    
    if (sidebar) {
        sidebar.classList.toggle('show');
    }
    if (overlay) {
        overlay.classList.toggle('show');
    }
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
    
    const chatbotSelected = chatbotSelect.value;
    const modelSelected = modelSelect.value;
    
    // Check if selected chatbot is disabled (no access)
    const selectedChatbotOption = chatbotSelect.options[chatbotSelect.selectedIndex];
    const chatbotDisabled = selectedChatbotOption && selectedChatbotOption.disabled;
    
    // Check if selected model is disabled (no access) 
    const selectedModelOption = modelSelect.options[modelSelect.selectedIndex];
    const modelDisabled = selectedModelOption && selectedModelOption.disabled;
    
    // Both chatbot and model must be selected and not disabled
    if (chatbotSelected && modelSelected && !chatbotDisabled && !modelDisabled) {
        createBtn.disabled = false;
    } else {
        createBtn.disabled = true;
    }
}

// Check if both chatbot and model are selected in sidebar
function checkSidebarSelections() {
    const chatbotSelect = document.getElementById('chatbot-select');
    const startBtn = document.getElementById('start-chat-btn');
    
    const chatbotSelected = chatbotSelect.value;
    
    // Chatbot must be selected
    if (chatbotSelected) {
        startBtn.disabled = false;
    } else {
        startBtn.disabled = true;
    }
}

// Load sidebar menu items dynamically
function loadSidebarMenuItems() {
    // Only load for mobile view
    if (window.innerWidth >= 768) {
        return;
    }
    
    const mobileNavMenu = document.getElementById('mobile-nav-menu');
    if (!mobileNavMenu) {
        return;
    }
    
    // Fetch menu items from the server
    fetch(CHAT_URLS.getSidebarMenuItems)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error('Error loading menu items:', data.error);
                return;
            }
            
            // Clear existing menu items
            mobileNavMenu.innerHTML = '';
            
            // Add menu items
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