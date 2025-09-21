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
    
    // Both chatbot and model must be selected
    if (chatbotSelected && modelSelected) {
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

// Load sidebar menu items dynamically and display them in the sidebar
function loadSidebarMenuItems() {
    const sidebarNavMenu = document.getElementById('sidebar-nav-menu');
    if (!sidebarNavMenu) {
        return;
    }
    
    // Fetch menu items from the server
    fetch(CHAT_URLS.getSidebarMenuItems)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error('Error loading menu items:', data.error);
                // Show default menu items if there's an error
                showDefaultSidebarMenuItems();
                return;
            }
            
            // Clear existing menu items
            sidebarNavMenu.innerHTML = '';
            
            // Check if user is authenticated
            const isAuthenticated = document.body.dataset.authenticated === 'true';
            
            // Add menu items
            if (data.menu_items && data.menu_items.length > 0) {
                data.menu_items.forEach(item => {
                    // Skip items that should only be shown to authenticated users if user is not authenticated
                    if (item.show_only_for_authenticated && !isAuthenticated) {
                        return;
                    }
                    
                    // Skip items that should only be shown to non-authenticated users if user is authenticated
                    if (item.show_only_for_non_authenticated && isAuthenticated) {
                        return;
                    }
                    
                    const navItem = document.createElement('div');
                    navItem.className = 'nav-item';
                    navItem.innerHTML = `
                        <a class="nav-link" href="${item.url}">
                            <i class="${item.icon_class}"></i> ${item.name}
                        </a>
                    `;
                    sidebarNavMenu.appendChild(navItem);
                });
            } else {
                // Show default menu items if none are configured
                showDefaultSidebarMenuItems();
            }
        })
        .catch(error => {
            console.error('Error loading menu items:', error);
            // Show default menu items if there's an error
            showDefaultSidebarMenuItems();
        });
}

// Show default sidebar menu items
function showDefaultSidebarMenuItems() {
    const sidebarNavMenu = document.getElementById('sidebar-nav-menu');
    if (!sidebarNavMenu) {
        return;
    }
    
    // Check if user is authenticated
    const isAuthenticated = document.body.dataset.authenticated === 'true';
    
    // Clear existing menu items
    sidebarNavMenu.innerHTML = '';
    
    // Default menu items
    const defaultMenuItems = [
        { name: 'خانه', url: '/', icon_class: 'fas fa-home' },
        { name: 'چت', url: '/chat/', icon_class: 'fas fa-comments' }
    ];
    
    // Add user-specific menu items
    if (isAuthenticated) {
        defaultMenuItems.push(
            { name: 'داشبورد', url: '/dashboard/', icon_class: 'fas fa-tachometer-alt' },
            { name: 'تراکنش‌های مالی', url: '/financial-transactions/', icon_class: 'fas fa-credit-card' },
            { name: 'خرید اشتراک', url: '/purchase-subscription/', icon_class: 'fas fa-shopping-cart' },
            { name: 'خروج', url: '/accounts/logout/', icon_class: 'fas fa-sign-out-alt' }
        );
    } else {
        defaultMenuItems.push(
            { name: 'ورود', url: '/accounts/login/', icon_class: 'fas fa-sign-in-alt' }
        );
    }
    
    // Add menu items to sidebar
    defaultMenuItems.forEach(item => {
        const navItem = document.createElement('div');
        navItem.className = 'nav-item';
        navItem.innerHTML = `
            <a class="nav-link" href="${item.url}">
                <i class="${item.icon_class}"></i> ${item.name}
            </a>
        `;
        sidebarNavMenu.appendChild(navItem);
    });
}

// Initialize UI elements when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Load sidebar menu items
    loadSidebarMenuItems();
    
    // Add event listener for floating new chat button
    const floatingNewChatBtn = document.getElementById('floating-new-chat-btn');
    if (floatingNewChatBtn) {
        floatingNewChatBtn.addEventListener('click', function() {
            // Trigger the existing new chat button
            const newChatBtn = document.getElementById('new-chat-btn');
            if (newChatBtn) {
                newChatBtn.click();
            }
        });
    }
    
    // Add event listener for model selection button (if we add one)
    // For now, we'll show the floating model selection when needed
    const modelSelect = document.getElementById('model-select');
    if (modelSelect) {
        modelSelect.addEventListener('click', function() {
            showFloatingModelSelection();
        });
    }
    
    // Add event listener for closing model selection
    const closeModelSelection = document.getElementById('close-model-selection');
    if (closeModelSelection) {
        closeModelSelection.addEventListener('click', function() {
            hideFloatingModelSelection();
        });
    }
});

// Function to show floating model selection
function showFloatingModelSelection() {
    const modelSelection = document.getElementById('floating-model-selection');
    if (modelSelection) {
        modelSelection.style.display = 'block';
        // Load models if not already loaded
        loadFloatingModelList();
    }
}

// Function to hide floating model selection
function hideFloatingModelSelection() {
    const modelSelection = document.getElementById('floating-model-selection');
    if (modelSelection) {
        modelSelection.style.display = 'none';
    }
}

// Function to load models in floating selection
function loadFloatingModelList() {
    // Fetch available models from the server
    fetch('/chat/models/')
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error('Error loading models:', data.error);
                return;
            }
            
            const modelList = document.getElementById('model-list');
            if (!modelList) return;
            
            // Clear loading state
            modelList.innerHTML = '';
            
            // Add models to the floating list
            data.models.forEach(model => {
                const modelItem = document.createElement('div');
                modelItem.className = 'model-item';
                modelItem.dataset.modelId = model.model_id;
                
                // Determine model type for styling
                let modelType = 'free';
                let modelBadge = 'رایگان';
                if (!model.is_free) {
                    if (model.user_has_access) {
                        modelType = 'premium';
                        modelBadge = 'ویژه';
                    } else {
                        modelType = 'disabled';
                        modelBadge = 'نیاز به اشتراک';
                    }
                }
                
                modelItem.innerHTML = `
                    <div class="model-icon">
                        <i class="fas fa-microchip"></i>
                    </div>
                    <div class="model-info">
                        <div class="model-name">${model.name}</div>
                        <div class="model-type">${model.description || 'مدل هوش مصنوعی'}</div>
                    </div>
                    <div class="model-badge ${modelType}">${modelBadge}</div>
                `;
                
                // Add click event if user has access
                if (model.user_has_access) {
                    modelItem.addEventListener('click', function() {
                        // Update the current session model
                        if (currentSessionId) {
                            updateSessionModel(currentSessionId, model.model_id);
                            // Hide the floating selection
                            hideFloatingModelSelection();
                            
                            // Show confirmation message
                            const confirmation = document.createElement('div');
                            confirmation.className = 'alert alert-success alert-dismissible fade show';
                            confirmation.style.cssText = 'position: fixed; top: 20px; right: 20px; z-index: 9999; max-width: 300px;';
                            confirmation.innerHTML = `
                                <strong>موفقیت!</strong> مدل به ${model.name} تغییر یافت.
                                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                            `;
                            document.body.appendChild(confirmation);
                            
                            // Auto remove after 3 seconds
                            setTimeout(() => {
                                if (confirmation.parentNode) {
                                    confirmation.parentNode.removeChild(confirmation);
                                }
                            }, 3000);
                        }
                    });
                } else {
                    // Add disabled styling
                    modelItem.classList.add('disabled');
                    modelItem.title = 'برای دسترسی به این مدل نیاز به اشتراک دارید';
                }
                
                modelList.appendChild(modelItem);
            });
        })
        .catch(error => {
            console.error('Error loading models:', error);
            const modelList = document.getElementById('model-list');
            if (modelList) {
                modelList.innerHTML = `
                    <div class="text-center text-danger p-3">
                        <i class="fas fa-exclamation-triangle"></i>
                        <p class="mt-2 mb-0">خطا در بارگذاری مدل‌ها</p>
                    </div>
                `;
            }
        });
}