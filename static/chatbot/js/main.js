// =================================
// فایل اصلی اجرا و رویداد‌ها (Main Execution & Event Handlers)
// =================================

// Global variables to store selected options for new session
let selectedModelForNewSession = null;
let isWebSearchEnabledForNewSession = false;
// Store model data for cost multiplier checking
let availableModelsData = [];
// Store current selected model for the floating selection
let currentSelectedModel = null;

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
        
        // Check if there's a default model selected and pre-select it
        const defaultModelId = localStorage.getItem('defaultModelId');
        if (defaultModelId) {
            // Set a small delay to ensure the modal is fully loaded
            setTimeout(() => {
                const chatbotSelect = document.getElementById('modal-chatbot-select');
                const modelSelect = document.getElementById('modal-model-select');
                
                if (chatbotSelect && modelSelect) {
                    // If chatbot is not selected, select the first available chatbot
                    if (!chatbotSelect.value && chatbotSelect.options.length > 1) {
                        chatbotSelect.value = chatbotSelect.options[1].value;
                        // Trigger the change event to load models
                        chatbotSelect.dispatchEvent(new Event('change'));
                        
                        // After models are loaded, select the default model
                        setTimeout(() => {
                            // Check if the default model is available in the options
                            for (let i = 0; i < modelSelect.options.length; i++) {
                                if (modelSelect.options[i].value === defaultModelId) {
                                    modelSelect.value = defaultModelId;
                                    checkModalSelections();
                                    break;
                                }
                            }
                        }, 200);
                    } else if (chatbotSelect.value) {
                        // If chatbot is already selected, just select the default model
                        // Check if the default model is available in the options
                        for (let i = 0; i < modelSelect.options.length; i++) {
                            if (modelSelect.options[i].value === defaultModelId) {
                                modelSelect.value = defaultModelId;
                                checkModalSelections();
                                break;
                            }
                        }
                    }
                }
            }, 100);
        }
        
        const modal = new bootstrap.Modal(document.getElementById('newChatModal'));
        modal.show();
    });

    // Event listener for model selection toggle to show floating model selection
    const modelToggle = document.getElementById('model-selection-toggle');
    if (modelToggle) {
        modelToggle.addEventListener('click', function() {
            const floatingSelection = document.getElementById('floating-model-selection');
            if (floatingSelection) {
                floatingSelection.classList.toggle('show');
            }
            // Close any open modals or other dropdowns if needed
            const newChatModal = bootstrap.Modal.getInstance(document.getElementById('newChatModal'));
            if (newChatModal) {
                newChatModal.hide();
            }
        });
    }

    // Floating Action Button for mobile - new chat
    const fabNewChat = document.getElementById('fab-new-chat');
    if (fabNewChat) {
        fabNewChat.addEventListener('click', function() {
            document.getElementById('modal-chatbot-select').value = '';
            document.getElementById('modal-model-select').value = '';
            document.getElementById('create-chat-btn').disabled = true;
            
            // Check if there's a default model selected and pre-select it
            const defaultModelId = localStorage.getItem('defaultModelId');
            if (defaultModelId) {
                // Set a small delay to ensure the modal is fully loaded
                setTimeout(() => {
                    const chatbotSelect = document.getElementById('modal-chatbot-select');
                    const modelSelect = document.getElementById('modal-model-select');
                    
                    if (chatbotSelect && modelSelect) {
                        // If chatbot is not selected, select the first available chatbot
                        if (!chatbotSelect.value && chatbotSelect.options.length > 1) {
                            chatbotSelect.value = chatbotSelect.options[1].value;
                            // Trigger the change event to load models
                            chatbotSelect.dispatchEvent(new Event('change'));
                            
                            // After models are loaded, select the default model
                            setTimeout(() => {
                                // Check if the default model is available in the options
                                for (let i = 0; i < modelSelect.options.length; i++) {
                                    if (modelSelect.options[i].value === defaultModelId) {
                                        modelSelect.value = defaultModelId;
                                        checkModalSelections();
                                        break;
                                    }
                                }
                            }, 200);
                        } else if (chatbotSelect.value) {
                            // If chatbot is already selected, just select the default model
                            // Check if the default model is available in the options
                            for (let i = 0; i < modelSelect.options.length; i++) {
                                if (modelSelect.options[i].value === defaultModelId) {
                                    modelSelect.value = defaultModelId;
                                    checkModalSelections();
                                    break;
                                }
                            }
                        }
                    }
                }, 100);
            }
            
            const modalElement = document.getElementById('newChatModal');
            const modal = bootstrap.Modal.getInstance(modalElement) || new bootstrap.Modal(modalElement);
            modal.show();
        });
    }
    
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

    document.getElementById('modal-model-select').addEventListener('change', function() {
        checkModalSelections();
        
        // Check if the selected model has a cost multiplier > 1 and show warning
        const selectedOption = this.options[this.selectedIndex];
        const costMultiplier = parseFloat(selectedOption.dataset.tokenCostMultiplier);
        
        if (costMultiplier > 1) {
            // Show warning message in modal
            showModalCostWarning(costMultiplier);
        } else {
            // Hide any existing warning
            hideModalCostWarning();
        }
    });

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
            
            // Reset model selection button text
            const currentModelName = document.getElementById('current-model-name');
            if (currentModelName) {
                currentModelName.textContent = 'انتخاب مدل';
            }
            currentSelectedModel = null;
            
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
    
    // Initialize floating model selection functionality
    initializeFloatingModelSelection();
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
            
            // Store model data for later use
            availableModelsData = data.models;
            
            const webSearchContainer = document.getElementById('welcome-web-search-container');
            
            // Populate floating model selection grid
            populateFloatingModelGrid(data.models);
            
            // If we have a current session, make sure the model name is displayed correctly
            if (currentSessionId) {
                const sessionData = JSON.parse(localStorage.getItem(`session_${currentSessionId}`) || '{}');
                if (sessionData.ai_model_name) {
                    const currentModelName = document.getElementById('current-model-name');
                    if (currentModelName) {
                        currentModelName.textContent = sessionData.ai_model_name;
                    }
                }
            } else {
                // If no session is selected, check if there's a default model and display it
                const defaultModelName = localStorage.getItem('defaultModelName');
                if (defaultModelName) {
                    const currentModelName = document.getElementById('current-model-name');
                    if (currentModelName) {
                        currentModelName.textContent = defaultModelName;
                    }
                }
            }
        })
        .catch(error => console.error('Error loading models:', error));
}

// Initialize floating model selection functionality
function initializeFloatingModelSelection() {
    // Add click event to model selection wrapper to show floating model selection
    const modelSelectionButton = document.getElementById('model-selection-button');
    if (modelSelectionButton) {
        modelSelectionButton.addEventListener('click', function(e) {
            e.stopPropagation();
            showFloatingModelSelection();
        });
    }
    
    // Add click event to close button
    const closeModelSelection = document.getElementById('close-model-selection');
    if (closeModelSelection) {
        closeModelSelection.addEventListener('click', function() {
            hideFloatingModelSelection();
        });
    }
    
    // Close floating model selection when clicking outside
    document.addEventListener('click', function(e) {
        const floatingModelSelection = document.getElementById('floating-model-selection');
        if (floatingModelSelection && floatingModelSelection.classList.contains('show') && 
            !floatingModelSelection.contains(e.target) && 
            !e.target.closest('#model-selection-button')) {
            hideFloatingModelSelection();
        }
    });
}

// Show floating model selection
function showFloatingModelSelection() {
    const floatingModelSelection = document.getElementById('floating-model-selection');
    if (floatingModelSelection) {
        floatingModelSelection.classList.add('show');
        // Populate the grid with available models if needed
        if (availableModelsData && availableModelsData.length > 0) {
            populateFloatingModelGrid(availableModelsData);
        }
    }
}

// Hide floating model selection
function hideFloatingModelSelection() {
    const floatingModelSelection = document.getElementById('floating-model-selection');
    if (floatingModelSelection) {
        floatingModelSelection.classList.remove('show');
    }
}

// Populate floating model grid with available models
function populateFloatingModelGrid(models) {
    const modelGrid = document.getElementById('model-grid');
    if (!modelGrid) return;
    
    // Only populate if the grid is empty or models have changed
    const existingCards = modelGrid.querySelectorAll('.model-card');
    if (existingCards.length > 0 && existingCards.length === models.length) {
        // Check if models are the same
        let modelsMatch = true;
        for (let i = 0; i < existingCards.length; i++) {
            if (existingCards[i].dataset.modelId !== models[i].model_id) {
                modelsMatch = false;
                break;
            }
        }
        
        if (modelsMatch) {
            // Models are the same, just update selection state
            updateModelSelectionState(models);
            return;
        }
    }
    
    // Clear current grid
    modelGrid.innerHTML = '';
    
    // Populate grid with model cards
    models.forEach(model => {
        const modelCard = document.createElement('div');
        modelCard.className = 'model-card';
        modelCard.dataset.modelId = model.model_id;
        
        // Add selected class if this is the current model
        if (currentSessionId) {
            const sessionData = JSON.parse(localStorage.getItem(`session_${currentSessionId}`) || '{}');
            if (sessionData.ai_model_name === model.name) {
                modelCard.classList.add('selected');
                currentSelectedModel = model.model_id;
                // Update the current model name in the button
                const currentModelName = document.getElementById('current-model-name');
                if (currentModelName) {
                    currentModelName.textContent = model.name;
                }
            }
        } else {
            // If no session is selected, check if this is the model stored in the global variable
            if (currentSelectedModel === model.model_id) {
                modelCard.classList.add('selected');
                // Update the current model name in the button
                const currentModelName = document.getElementById('current-model-name');
                if (currentModelName) {
                    currentModelName.textContent = model.name;
                }
            }
        }
        
        // Set access class
        let accessClass = 'free';
        let accessText = 'رایگان';
        if (!model.is_free) {
            if (model.user_has_access) {
                accessClass = 'premium';
                accessText = 'ویژه';
            } else {
                accessClass = 'restricted';
                accessText = 'محدود';
                modelCard.classList.add('restricted');
            }
        }
        
        // Set default image if none provided
        const modelImage = model.image_url || '/static/images/default-model.png';
        
        modelCard.innerHTML = `
            <img src="${modelImage}" alt="${model.name}" onerror="this.src='/static/images/default-model.png'">
            <div class="model-name">${model.name}</div>
            <span class="model-access ${accessClass}">${accessText}</span>
        `;
        
        // Add click event if user has access
        if (model.user_has_access || model.is_free) {
            console.log('Adding click event for model:', model.model_id, model.name);
            // Store model data directly on the element for use in the event handler
            modelCard.modelId = model.model_id;
            modelCard.modelName = model.name;
            modelCard.addEventListener('click', function() {
                console.log('Model card clicked:', this.modelId, this.modelName);
                selectModel(this.modelId, this.modelName);
            });
        } else {
            console.log('Model not accessible:', model.model_id, model.name);
            // Add a visual indicator that the model is not accessible
            modelCard.style.opacity = '0.5';
            modelCard.style.cursor = 'not-allowed';
        }
        
        modelGrid.appendChild(modelCard);
    });
}

// Update selection state without recreating cards
function updateModelSelectionState(models) {
    const modelCards = document.querySelectorAll('.model-card');
    modelCards.forEach(card => {
        // Remove selected class from all cards
        card.classList.remove('selected');
        
        // Add selected class if this is the current model
        if (currentSessionId) {
            const sessionData = JSON.parse(localStorage.getItem(`session_${currentSessionId}`) || '{}');
            const model = models.find(m => m.model_id === card.dataset.modelId);
            if (model && sessionData.ai_model_name === model.name) {
                card.classList.add('selected');
                currentSelectedModel = model.model_id;
                // Update the current model name in the button
                const currentModelName = document.getElementById('current-model-name');
                if (currentModelName) {
                    currentModelName.textContent = model.name;
                }
            }
        } else {
            // If no session is selected, check if this is the model stored in the global variable
            if (currentSelectedModel === card.dataset.modelId) {
                card.classList.add('selected');
                // Update the current model name in the button
                const currentModelName = document.getElementById('current-model-name');
                if (currentModelName) {
                    const model = models.find(m => m.model_id === card.dataset.modelId);
                    currentModelName.textContent = model ? model.name : 'انتخاب مدل';
                }
            }
        }
    });
}

// Select a model and update the session
function selectModel(modelId, modelName) {
    console.log('Selecting model:', modelId, modelName);
    
    // Update UI to show selected model regardless of session
    const modelCards = document.querySelectorAll('.model-card');
    modelCards.forEach(card => {
        if (card.dataset.modelId === modelId) {
            card.classList.add('selected');
        } else {
            card.classList.remove('selected');
        }
    });
    
    // Update current selected model
    currentSelectedModel = modelId;
    
    // Update the current model name in the button
    const currentModelName = document.getElementById('current-model-name');
    if (currentModelName) {
        currentModelName.textContent = modelName;
    }
    
    // Store the selected model as the default model for new sessions
    localStorage.setItem('defaultModelId', modelId);
    localStorage.setItem('defaultModelName', modelName);
    
    // If we have a session, update the session model
    if (currentSessionId) {
        console.log('Updating session model');
        updateSessionModel(currentSessionId, modelId);
        
        // Also update in localStorage for consistency
        const sessionData = JSON.parse(localStorage.getItem(`session_${currentSessionId}`) || '{}');
        sessionData.ai_model_name = modelName;
        localStorage.setItem(`session_${currentSessionId}`, JSON.stringify(sessionData));
        
        // Show confirmation message
        const confirmation = document.createElement('div');
        confirmation.className = 'alert alert-success alert-dismissible fade show';
        confirmation.style.cssText = 'position: fixed; top: 20px; right: 20px; z-index: 9999; max-width: 300px;';
        confirmation.innerHTML = `
            <strong>موفقیت!</strong> مدل به ${modelName} تغییر یافت.
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        document.body.appendChild(confirmation);
        
        // Auto remove after 3 seconds
        setTimeout(() => {
            if (confirmation.parentNode) {
                confirmation.parentNode.removeChild(confirmation);
            }
        }, 3000);
    } else {
        // Show confirmation message for default model selection
        const confirmation = document.createElement('div');
        confirmation.className = 'alert alert-success alert-dismissible fade show';
        confirmation.style.cssText = 'position: fixed; top: 20px; right: 20px; z-index: 9999; max-width: 300px;';
        confirmation.innerHTML = `
            <strong>موفقیت!</strong> مدل پیشفرض به ${modelName} تغییر یافت.
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
    
    // Hide floating model selection
    hideFloatingModelSelection();
}

// Function to show cost multiplier warning
function showCostMultiplierWarning(model) {
    // Check if warning already exists
    let warningElement = document.getElementById('cost-multiplier-warning');
    if (!warningElement) {
        warningElement = document.createElement('div');
        warningElement.id = 'cost-multiplier-warning';
        warningElement.className = 'alert alert-warning alert-dismissible fade show mt-3';
        warningElement.role = 'alert';
        warningElement.innerHTML = `
            <i class="fas fa-exclamation-triangle"></i>
            <strong>هشدار هزینه!</strong>
            <span id="warning-text"></span>
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        // Append to the welcome message container
        const welcomeMessage = document.getElementById('welcome-message');
        welcomeMessage.appendChild(warningElement);
    }
    
    // Update warning text
    const multiplier = model.token_cost_multiplier;
    const warningText = document.getElementById('warning-text');
    warningText.textContent = ` این مدل هوش مصنوعی دارای ضریب هزینه ${multiplier} است و به ازای هر توکن مصرفی، ${multiplier} توکن از اعتبار شما کسر خواهد شد.`;
    
    // Make sure it's visible
    warningElement.style.display = 'block';
}

// Function to hide cost multiplier warning
function hideCostMultiplierWarning() {
    const warningElement = document.getElementById('cost-multiplier-warning');
    if (warningElement) {
        warningElement.style.display = 'none';
    }
}

// Function to show cost multiplier warning in modal
function showModalCostWarning(multiplier) {
    // Check if warning already exists
    let warningElement = document.getElementById('modal-cost-warning');
    if (!warningElement) {
        warningElement = document.createElement('div');
        warningElement.id = 'modal-cost-warning';
        warningElement.className = 'alert alert-warning mt-3';
        warningElement.role = 'alert';
        warningElement.innerHTML = `
            <i class="fas fa-exclamation-triangle"></i>
            <strong>هشدار هزینه!</strong>
            <span id="modal-warning-text"></span>
        `;
        // Insert before the create button
        const createBtn = document.getElementById('create-chat-btn');
        createBtn.parentNode.insertBefore(warningElement, createBtn);
    }
    
    // Update warning text
    const warningText = document.getElementById('modal-warning-text');
    warningText.textContent = ` این مدل هوش مصنوعی دارای ضریب هزینه ${multiplier} است و به ازای هر توکن مصرفی، ${multiplier} توکن از اعتبار شما کسر خواهد شد.`;
    
    // Make sure it's visible
    warningElement.style.display = 'block';
}

// Function to hide cost multiplier warning in modal
function hideModalCostWarning() {
    const warningElement = document.getElementById('modal-cost-warning');
    if (warningElement) {
        warningElement.style.display = 'none';
    }
}