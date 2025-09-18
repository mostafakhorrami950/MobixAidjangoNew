// =================================
// فایل اصلی اجرا و رویداد‌ها (Main Execution & Event Handlers)
// =================================

// Global variables to store selected options for new session
let selectedModelForNewSession = null;
let isWebSearchEnabledForNewSession = false;

// Event listeners
document.addEventListener('DOMContentLoaded', function() {
    loadSessions();
    checkInitialSession(); // Check if we should load a specific session
    
    // Initialize multiple file upload functionality
    initializeMultiFileUpload();
    
    // Load available models for user
    loadAvailableModelsForUser();
    
    // Load sidebar menu items
    loadSidebarMenuItems();
    
    // Clicking on message input opens new chat modal if no session is selected
    document.getElementById('message-input').addEventListener('click', function() {
        if (!currentSessionId) {
            // Instead of opening modal, we'll allow users to send messages directly
            // The sendMessage function will handle creating a default session
            return;
        }
    });
    
    // Input event listener is now handled by MultiFileUploadManager
    // This prevents conflicts between multiple event listeners
    
    // Add event listener for model selection in message input area
    document.getElementById('model-select').addEventListener('change', function() {
        if (currentSessionId && this.value) {
            // Update the session model
            updateSessionModel(currentSessionId, this.value);
            
            // Show a confirmation message
            const originalText = this.options[this.selectedIndex].text;
            const confirmation = document.createElement('div');
            confirmation.className = 'alert alert-success alert-dismissible fade show';
            confirmation.style.cssText = 'position: fixed; top: 20px; right: 20px; z-index: 9999; max-width: 300px;';
            confirmation.innerHTML = `
                <strong>موفقیت!</strong> مدل به ${originalText.split(' <')[0]} تغییر یافت.
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
    
    // Add event listener for model selection in welcome area
    document.getElementById('welcome-model-select').addEventListener('change', function() {
        selectedModelForNewSession = this.value;
    });
    
    // Add event listener for web search toggle in welcome area
    document.getElementById('welcome-web-search-btn').addEventListener('click', function() {
        const isWebSearchActive = this.classList.contains('btn-success');
        
        if (isWebSearchActive) {
            // Disable web search
            this.classList.remove('btn-success');
            this.classList.add('btn-outline-secondary');
            this.innerHTML = '<i class="fas fa-search"></i> جستجو وب';
            isWebSearchEnabledForNewSession = false;
        } else {
            // Enable web search
            this.classList.remove('btn-outline-secondary');
            this.classList.add('btn-success');
            this.innerHTML = '<i class="fas fa-search"></i> جستجو وب فعال';
            isWebSearchEnabledForNewSession = true;
        }
    });
    
    // New chat button opens modal
    document.getElementById('new-chat-btn').addEventListener('click', function() {
        document.getElementById('modal-chatbot-select').value = '';
        document.getElementById('modal-model-select').value = '';
        document.getElementById('create-chat-btn').disabled = true;
        const modal = new bootstrap.Modal(document.getElementById('newChatModal'));
        modal.show();
    });
    
    // Toggle sessions list
    document.getElementById('toggle-sessions').addEventListener('click', toggleSessionsList);
    
    // Modal selection change listeners
    document.getElementById('modal-chatbot-select').addEventListener('change', function() {
        checkModalSelections();
        // Load models based on chatbot type
        const chatbotId = this.value;
        if (chatbotId) {
            loadModelsForChatbot(chatbotId);
        }
    });
    document.getElementById('modal-model-select').addEventListener('change', checkModalSelections);
    
    // Modal create button
    document.getElementById('create-chat-btn').addEventListener('click', createNewChat);
    
    // Send message form submission
    document.getElementById('chat-form').addEventListener('submit', function(event) {
        event.preventDefault();
        sendMessage();
    });
    
    // Send message button (for direct click as well)
    document.getElementById('send-button').addEventListener('click', function(event) {
        event.preventDefault();
        document.getElementById('chat-form').dispatchEvent(new Event('submit'));
    });
    
    // Enter key in message input
    document.getElementById('message-input').addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            document.getElementById('chat-form').dispatchEvent(new Event('submit'));
        }
    });
    
    // Delete session button
    document.getElementById('delete-session-btn').addEventListener('click', deleteSession);
    
    // Web search button
    document.getElementById('web-search-btn').addEventListener('click', toggleWebSearch);
    
    // Image generation button
    document.getElementById('image-generation-btn').addEventListener('click', toggleImageGeneration);
    
    // Mobile sidebar toggle - moved from base.html to here where sidebar exists
    const mobileMenuToggle = document.getElementById('mobile-menu-toggle');
    if (mobileMenuToggle) {
        mobileMenuToggle.addEventListener('click', function(e) {
            e.stopPropagation(); // Prevent event bubbling
            toggleSidebar();
        });
    }
    
    // Mobile sidebar toggle button in sidebar
    if (document.getElementById('toggle-sidebar')) {
        document.getElementById('toggle-sidebar').addEventListener('click', toggleSidebar);
    }
    
    // Overlay click to close sidebar
    if (document.getElementById('sidebar-overlay')) {
        document.getElementById('sidebar-overlay').addEventListener('click', toggleSidebar);
    }
    
    // Handle browser back/forward buttons
    window.addEventListener('popstate', function(event) {
        if (event.state && event.state.sessionId) {
            loadSession(event.state.sessionId);
        } else {
            // Reset to default state
            currentSessionId = null;
            document.getElementById('current-session-title').innerHTML = `
                <i class="fas fa-comments"></i> چت را انتخاب کنید یا جدیدی ایجاد کنید
            `;
            document.getElementById('chat-container').innerHTML = `
                <div class="text-center text-muted welcome-message" id="welcome-message">
                    <i class="fas fa-robot fa-3x mb-3"></i>
                    <h4>به چت‌بات MobixAI خوش آمدید</h4>
                    <p class="mb-0">چتی را انتخاب کنید یا چت جدیدی شروع کنید</p>
                    <div class="model-selection-container mt-4 p-3 bg-light rounded" id="welcome-model-selection" style="display: none;">
                        <h5 class="mb-3">
                            <i class="fas fa-microchip"></i> انتخاب مدل هوش مصنوعی
                        </h5>
                        <div class="mb-3">
                            <select class="form-select form-select-lg" id="welcome-model-select">
                                <option value="">-- مدلی را انتخاب کنید --</option>
                            </select>
                        </div>
                        <div class="alert alert-info">
                            <i class="fas fa-info-circle"></i>
                            مدل انتخابی برای چت جدید شما استفاده خواهد شد. بعد از ایجاد چت می‌توانید مدل را تغییر دهید.
                        </div>
                    </div>
                    <div class="web-search-toggle-container mt-3" id="welcome-web-search-container" style="display: none;">
                        <button class="btn btn-outline-secondary" id="welcome-web-search-btn" type="button">
                            <i class="fas fa-search"></i> جستجو وب
                        </button>
                        <small class="text-muted d-block mt-1">
                            فعال کردن جستجوی اینترنتی برای پاسخ‌های به‌روز
                        </small>
                    </div>
                </div>
            `;
            document.getElementById('message-input').disabled = true;
            document.getElementById('send-button').disabled = true;
            document.getElementById('delete-session-btn').style.display = 'none';
            
            // Reset global variables
            selectedModelForNewSession = null;
            isWebSearchEnabledForNewSession = false;
            
            // Reload available models for user
            loadAvailableModelsForUser();
            
            // Reload sidebar menu items
            loadSidebarMenuItems();
        }
    });
    
    // Reload sidebar menu items on window resize
    window.addEventListener('resize', function() {
        if (window.innerWidth >= 768) {
            // On desktop, clear mobile menu
            const mobileNavMenu = document.getElementById('mobile-nav-menu');
            if (mobileNavMenu) {
                mobileNavMenu.innerHTML = '';
            }
        } else {
            // On mobile, reload menu items
            loadSidebarMenuItems();
        }
    });
    
    // Add edit button to user messages after a short delay
    setTimeout(addEditButtonToUserMessages, 1000);
});

// Load available models for user
function loadAvailableModelsForUser() {
    fetch('/chat/models/')
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error('Error loading models:', data.error);
                return;
            }
            
            const modelSelect = document.getElementById('welcome-model-select');
            const modelSelectionContainer = document.getElementById('welcome-model-selection');
            const webSearchContainer = document.getElementById('welcome-web-search-container');
            
            // Clear current options
            modelSelect.innerHTML = '<option value="">-- مدلی را انتخاب کنید --</option>';
            
            // Populate model select
            data.models.forEach(model => {
                const option = document.createElement('option');
                option.value = model.model_id;
                option.textContent = model.name;
                
                // Add class based on model type
                if (model.is_free) {
                    option.className = 'model-option-free';
                } else {
                    option.className = 'model-option-premium';
                }
                
                modelSelect.appendChild(option);
            });
            
            // Show the model selection container if there are models
            if (data.models.length > 0) {
                modelSelectionContainer.style.display = 'block';
                // Check web search access for welcome area
                checkWebSearchAccessForWelcome();
            }
        })
        .catch(error => console.error('Error loading models:', error));
}