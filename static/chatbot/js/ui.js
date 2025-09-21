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

// Load sidebar menu items dynamically
function loadSidebarMenuItems() {
    const sidebarMenuItems = document.getElementById('sidebar-menu-items');
    if (!sidebarMenuItems) {
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
            sidebarMenuItems.innerHTML = '';
            
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
                    sidebarMenuItems.appendChild(navItem);
                });
            }
        })
        .catch(error => {
            console.error('Error loading menu items:', error);
        });
}

// Show floating model selection
function showFloatingModelSelection() {
    const floatingModelSelection = document.getElementById('floating-model-selection');
    const overlay = document.getElementById('sidebar-overlay');
    
    if (floatingModelSelection) {
        floatingModelSelection.style.display = 'block';
    }
    if (overlay) {
        overlay.classList.add('show');
    }
    
    // Load available models
    loadAvailableModelsForFloatingSelection();
}

// Hide floating model selection
function hideFloatingModelSelection() {
    const floatingModelSelection = document.getElementById('floating-model-selection');
    const overlay = document.getElementById('sidebar-overlay');
    
    if (floatingModelSelection) {
        floatingModelSelection.style.display = 'none';
    }
    if (overlay) {
        overlay.classList.remove('show');
    }
}

// Load available models for floating selection
function loadAvailableModelsForFloatingSelection() {
    const modelList = document.getElementById('model-list');
    if (!modelList) {
        return;
    }
    
    // Show loading state
    modelList.innerHTML = `
        <div class="text-center p-3">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">در حال بارگذاری...</span>
            </div>
            <p class="mt-2">در حال بارگذاری مدل‌ها...</p>
        </div>
    `;
    
    // Fetch available models from the server
    fetch('/chat/models/')
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error('Error loading models:', data.error);
                modelList.innerHTML = `
                    <div class="alert alert-danger">
                        خطا در بارگذاری مدل‌ها
                    </div>
                `;
                return;
            }
            
            // Clear current content
            modelList.innerHTML = '';
            
            // Populate model list
            if (data.models && data.models.length > 0) {
                data.models.forEach(model => {
                    // Only show models that user has access to
                    if (model.user_has_access) {
                        const modelItem = document.createElement('div');
                        modelItem.className = 'model-item';
                        modelItem.dataset.modelId = model.model_id;
                        
                        // Determine badge class and text
                        let badgeClass = model.is_free ? 'free' : 'premium';
                        let badgeText = model.is_free ? 'رایگان' : 'ویژه';
                        
                        modelItem.innerHTML = `
                            <div class="model-item-info">
                                <div class="model-item-name">${model.name}</div>
                                <p class="model-item-description">${model.description || 'بدون توضیح'}</p>
                            </div>
                            <div class="model-item-badge ${badgeClass}">${badgeText}</div>
                        `;
                        
                        // Add click event to select model
                        modelItem.addEventListener('click', function() {
                            selectModelForNewSession(model.model_id);
                        });
                        
                        modelList.appendChild(modelItem);
                    }
                });
            } else {
                modelList.innerHTML = `
                    <div class="alert alert-info">
                        هیچ مدلی در دسترس نیست
                    </div>
                `;
            }
        })
        .catch(error => {
            console.error('Error loading models:', error);
            modelList.innerHTML = `
                <div class="alert alert-danger">
                    خطا در بارگذاری مدل‌ها
                </div>
            `;
        });
}

// Select model for new session
function selectModelForNewSession(modelId) {
    // Store selected model
    selectedModelForNewSession = modelId;
    
    // Hide floating model selection
    hideFloatingModelSelection();
    
    // Create new session with selected model
    createDefaultSessionWithModel(modelId);
}