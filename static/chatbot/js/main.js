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
    console.log('Chat page DOM content loaded');
    
    // Log important elements
    const sidebar = document.getElementById('sidebar');
    const sidebarOverlay = document.getElementById('sidebar-overlay');
    const mobileMenuToggle = document.getElementById('mobile-menu-toggle');
    
    console.log('Chat page - Sidebar element:', sidebar);
    console.log('Chat page - Sidebar overlay element:', sidebarOverlay);
    console.log('Chat page - Mobile menu toggle element:', mobileMenuToggle);
    
    // Hide model selection button by default until we know the session type
    const modelSelButton = document.getElementById('model-selection-button');
    if (modelSelButton) {
        modelSelButton.style.display = 'none';
    }
    
    // Add event listener for the image editing button
    const imageEditingBtn = document.getElementById('image-editing-btn');
    if (imageEditingBtn) {
        imageEditingBtn.addEventListener('click', function() {
            // Reset modal to step 1
            showStep(1);
            
            // Reset selections
            const chatbotContainer = document.getElementById('modal-chatbot-select');
            if (chatbotContainer) {
                const current = chatbotContainer.querySelector('.select-current');
                if (current) {
                    current.innerHTML = '<div class="placeholder">چت‌بات را انتخاب کنید</div>';
                }
                const options = chatbotContainer.querySelector('.select-options');
                if (options) {
                    options.innerHTML = '';
                    options.style.display = 'none';
                }
                delete chatbotContainer.dataset.selected;
                chatbotContainer.classList.remove('open');
            }
            
            const modelContainer = document.getElementById('modal-model-select');
            if (modelContainer) {
                const current = modelContainer.querySelector('.select-current');
                if (current) {
                    current.innerHTML = '<div class="placeholder">مدل را انتخاب کنید</div>';
                }
                const options = modelContainer.querySelector('.select-options');
                if (options) {
                    options.innerHTML = '';
                    options.style.display = 'none';
                }
                delete modelContainer.dataset.selected;
                modelContainer.classList.remove('open');
            }
            
            // Reset interaction type buttons
            document.querySelectorAll('.interaction-type-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            
            // Open the new chat modal
            const modalElement = document.getElementById('newChatModal');
            if (modalElement) {
                const modal = new bootstrap.Modal(modalElement);
                modal.show();
                
                // Automatically select the image interaction type after a short delay
                setTimeout(() => {
                    // Find and click the image interaction type button
                    const imageInteractionBtn = document.querySelector('.interaction-type-btn[data-interaction-type="image"]');
                    if (imageInteractionBtn) {
                        imageInteractionBtn.click();
                    }
                }, 300);
            }
        });
    }
    
    // Ensure sidebar and overlay are hidden on mobile devices on page load
    if (window.innerWidth < 768) {
        if (sidebar) {
            sidebar.classList.remove('show');
        }
        if (sidebarOverlay) {
            sidebarOverlay.classList.remove('show');
        }
    }
    
    loadSessions();
    checkInitialSession(); // Check if we should load a specific session
    
    // Initialize multiple file upload functionality
    initializeMultiFileUpload();

    // Load available models for user
    loadAvailableModelsForUser();

    // Load sidebar menu items for both desktop and mobile
    loadDesktopSidebarMenuItems();
    loadSidebarMenuItems();

    // Input event listener is now handled by MultiFileUploadManager
    // This prevents conflicts between multiple event listeners

    // Add event listener for web search toggle in welcome area
    const welcomeWebSearchBtn = document.getElementById('welcome-web-search-btn');
    if (welcomeWebSearchBtn) {
        welcomeWebSearchBtn.addEventListener('click', function() {
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
    }
    
    // Check web search access for welcome screen (when no session is active)
    if (!currentSessionId) {
        checkWebSearchAccessForWelcome();
    }

    // Add event listeners for automatic session creation
    // Message input box
    const messageInput = document.getElementById('message-input');
    if (messageInput) {
        messageInput.addEventListener('focus', function() {
            // Only create a session if there's no current session
            if (!currentSessionId) {
                // Show a loading state to the user
                showSessionCreationLoading();

                // Call the function from sessions.js to create a new default session
                createDefaultSession()
                    .then(sessionData => {
                        if (sessionData && sessionData.session_id) {
                            // Session created successfully, page will automatically refresh
                            // due to changes in createDefaultSession function
                            console.log('Session created, page will refresh automatically');
                        } else {
                            // Handle cases where the server returns an error in the JSON response
                            console.error('Failed to create session:', sessionData.error || 'No session ID returned');
                            alert('خطا در ایجاد چت جدید: ' + (sessionData.error || 'پاسخ نامعتبر از سرور'));
                            hideSessionCreationLoading(false); // Hide loading and restore welcome message
                        }
                    })
                    .catch(error => {
                        // Handle network or other unexpected errors
                        console.error('Error creating default session:', error);
                        alert('یک خطای غیرمنتظره در هنگام ایجاد چت جدید رخ داد. لطفا اتصال اینترنت خود را بررسی کرده و صفحه را دوباره بارگیری کنید.');
                        hideSessionCreationLoading(false); // Hide loading and restore welcome message
                    });
            }
        });
    }

    // File upload button
    const uploadBtn = document.getElementById('upload-btn');
    if (uploadBtn) {
        uploadBtn.addEventListener('click', function() {
            // Only create a session if there's no current session
            if (!currentSessionId) {
                // Show a loading state to the user
                showSessionCreationLoading();

                // Call the function from sessions.js to create a new default session
                createDefaultSession()
                    .then(sessionData => {
                        if (sessionData && sessionData.session_id) {
                            // Session created successfully, page will automatically refresh
                            // due to changes in createDefaultSession function
                            console.log('Session created, page will refresh automatically');
                            
                            // After session is created, trigger the file input
                            setTimeout(() => {
                                document.getElementById('file-input').click();
                            }, 100);

                        } else {
                            // Handle cases where the server returns an error in the JSON response
                            console.error('Failed to create session:', sessionData.error || 'No session ID returned');
                            alert('خطا در ایجاد چت جدید: ' + (sessionData.error || 'پاسخ نامعتبر از سرور'));
                            hideSessionCreationLoading(false); // Hide loading and restore welcome message
                        }
                    })
                    .catch(error => {
                        // Handle network or other unexpected errors
                        console.error('Error creating default session:', error);
                        alert('یک خطای غیرمنتظره در هنگام ایجاد چت جدید رخ داد. لطفا اتصال اینترنت خود را بررسی کرده و صفحه را دوباره بارگیری کنید.');
                        hideSessionCreationLoading(false); // Hide loading and restore welcome message
                    });
            }
        });
    }

    // Model selection button
    const modelSelectionButton = document.getElementById('model-selection-button');
    if (modelSelectionButton) {
        modelSelectionButton.addEventListener('click', function(e) {
            e.stopPropagation();
            
            // Check if this is an image editing chatbot session
            if (currentSessionId) {
                const sessionData = JSON.parse(localStorage.getItem(`session_${currentSessionId}`) || '{}');
                if (sessionData.chatbot_type === 'image_editing') {
                    // Don't show model selection for image editing chatbots
                    return;
                }
            }
            
            // Only create a session if there's no current session
            if (!currentSessionId) {
                // Show a loading state to the user
                showSessionCreationLoading();

                // Call the function from sessions.js to create a new default session
                createDefaultSession()
                    .then(sessionData => {
                        if (sessionData && sessionData.session_id) {
                            // Session created successfully, page will automatically refresh
                            // due to changes in createDefaultSession function
                            console.log('Session created, page will refresh automatically');
                            
                            // After session is created, show the model selection
                            setTimeout(() => {
                                showFloatingModelSelection();
                            }, 100);

                        } else {
                            // Handle cases where the server returns an error in the JSON response
                            console.error('Failed to create session:', sessionData.error || 'No session ID returned');
                            alert('خطا در ایجاد چت جدید: ' + (sessionData.error || 'پاسخ نامعتبر از سرور'));
                            hideSessionCreationLoading(false); // Hide loading and restore welcome message
                        }
                    })
                    .catch(error => {
                        // Handle network or other unexpected errors
                        console.error('Error creating default session:', error);
                        alert('یک خطای غیرمنتظره در هنگام ایجاد چت جدید رخ داد. لطفا اتصال اینترنت خود را بررسی کرده و صفحه را دوباره بارگیری کنید.');
                        hideSessionCreationLoading(false); // Hide loading and restore welcome message
                    });
            } else {
                // If there's already a session, just show the model selection
                showFloatingModelSelection();
            }
        });
    }
    
    // New chat button opens modal
    const newChatBtn = document.getElementById('new-chat-btn');
    if (newChatBtn) {
        newChatBtn.addEventListener('click', function() {
            // Reset modal to step 1
            showStep(1);
            
            // Reset selections
            const chatbotContainer = document.getElementById('modal-chatbot-select');
            if (chatbotContainer) {
                const current = chatbotContainer.querySelector('.select-current');
                if (current) {
                    current.innerHTML = '<div class="placeholder">چت‌بات را انتخاب کنید</div>';
                }
                const options = chatbotContainer.querySelector('.select-options');
                if (options) {
                    options.innerHTML = '';
                    options.style.display = 'none';
                }
                delete chatbotContainer.dataset.selected;
                chatbotContainer.classList.remove('open');
            }
            
            const modelContainer = document.getElementById('modal-model-select');
            if (modelContainer) {
                const current = modelContainer.querySelector('.select-current');
                if (current) {
                    current.innerHTML = '<div class="placeholder">مدل را انتخاب کنید</div>';
                }
                const options = modelContainer.querySelector('.select-options');
                if (options) {
                    options.innerHTML = '';
                    options.style.display = 'none';
                }
                delete modelContainer.dataset.selected;
                modelContainer.classList.remove('open');
            }
            
            // Reset interaction type buttons
            document.querySelectorAll('.interaction-type-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            
            const modalElement = document.getElementById('newChatModal');
            if (modalElement) {
                const modal = new bootstrap.Modal(modalElement);
                modal.show();
            }
        });
    }

    // Floating Action Button for mobile - new chat
    const fabNewChat = document.getElementById('fab-new-chat');
    if (fabNewChat) {
        fabNewChat.addEventListener('click', function() {
            // Reset modal to step 1
            showStep(1);
            
            // Reset selections
            const chatbotContainer = document.getElementById('modal-chatbot-select');
            if (chatbotContainer) {
                const current = chatbotContainer.querySelector('.select-current');
                if (current) {
                    current.innerHTML = '<div class="placeholder">چت‌بات را انتخاب کنید</div>';
                }
                const options = chatbotContainer.querySelector('.select-options');
                if (options) {
                    options.innerHTML = '';
                    options.style.display = 'none';
                }
                delete chatbotContainer.dataset.selected;
                chatbotContainer.classList.remove('open');
            }
            
            const modelContainer = document.getElementById('modal-model-select');
            if (modelContainer) {
                const current = modelContainer.querySelector('.select-current');
                if (current) {
                    current.innerHTML = '<div class="placeholder">مدل را انتخاب کنید</div>';
                }
                const options = modelContainer.querySelector('.select-options');
                if (options) {
                    options.innerHTML = '';
                    options.style.display = 'none';
                }
                delete modelContainer.dataset.selected;
                modelContainer.classList.remove('open');
            }
            
            // Reset interaction type buttons
            document.querySelectorAll('.interaction-type-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            
            
            const modalElement = document.getElementById('newChatModal');
            if (modalElement) {
                const modal = bootstrap.Modal.getInstance(modalElement) || new bootstrap.Modal(modalElement);
                modal.show();
            }
        });
    }
    
    // Next step button
    const nextBtn = document.getElementById('next-step-btn');
    if (nextBtn) {
        nextBtn.addEventListener('click', function() {
            const currentStep = document.querySelector('.modal-step.active');
            if (!currentStep) return;
            
            const stepNumber = parseInt(currentStep.id.split('-')[1]);
            
            if (stepNumber === 1) {
                // Validate interaction type selection
                const activeBtn = document.querySelector('.interaction-type-btn.active');
                if (!activeBtn) {
                    showConfirmationMessage('لطفاً نوع تعامل را انتخاب کنید.', 'warning');
                    return;
                }
                
                const interactionType = activeBtn.dataset.interactionType;
                loadChatbotsByType(interactionType);
                showStep(2);
            } else if (stepNumber === 2) {
                // Validate chatbot selection
                const chatbotContainer = document.getElementById('modal-chatbot-select');
                if (!chatbotContainer || !chatbotContainer.dataset.selected) {
                    showConfirmationMessage('لطفاً چت‌بات را انتخاب کنید.', 'warning');
                    return;
                }
                
                showStep(3);
            }
        });
    }
    
    // Previous step button
    const prevBtn = document.getElementById('prev-step-btn');
    if (prevBtn) {
        prevBtn.addEventListener('click', function() {
            const currentStep = document.querySelector('.modal-step.active');
            if (!currentStep) return;
            
            const stepNumber = parseInt(currentStep.id.split('-')[1]);
            showStep(stepNumber - 1);
        });
    }
    
    // Initialize enhanced select behavior when DOM is loaded
    document.addEventListener('DOMContentLoaded', function() {
        initializeEnhancedSelect();
        initializeInteractionTypeSelection();
    });
    
    // Function to load chatbots by type with images
    window.loadChatbotsByType = function(type) {
        console.log('Loading chatbots for type:', type);
        const chatbotContainer = document.getElementById('modal-chatbot-select');
        if (!chatbotContainer) return;
        
        // Map frontend interaction types to backend chatbot types
        let backendType = type;
        if (type === 'image') {
            backendType = 'image_editing';  // Map image interaction type to image_editing chatbot type
        }
        
        // Show loading state
        const loadingEl = chatbotContainer.querySelector('.select-loading');
        const emptyEl = chatbotContainer.querySelector('.select-empty');
        const optionsList = chatbotContainer.querySelector('.select-options-list');
        
        if (loadingEl) loadingEl.classList.remove('d-none');
        if (emptyEl) emptyEl.classList.add('d-none');
        if (optionsList) optionsList.innerHTML = '';
        
        fetch(`/chat/chatbots/${backendType}/`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log('Chatbots data received:', data);
                const chatbots = data.chatbots || [];
                
                // Hide loading state
                if (loadingEl) loadingEl.classList.add('d-none');
                
                if (chatbots.length === 0) {
                    if (emptyEl) emptyEl.classList.remove('d-none');
                    return;
                }
                
                let html = '';
                chatbots.forEach(chatbot => {
                    const hasAccess = chatbot.has_access;
                    const badgeClass = hasAccess ? 'free' : 'premium';
                    const badgeText = hasAccess ? 'رایگان' : 'نیاز به اشتراک';
                    
                    // Add a class to indicate access status
                    const accessClass = hasAccess ? '' : 'restricted-option';
                    
                    html += `
                        <div class="enhanced-option chatbot-option ${accessClass}" 
                             data-chatbot-id="${chatbot.id}" 
                             data-image="${chatbot.image || ''}"
                             data-name="${chatbot.name}"
                             data-description="${chatbot.description || ''}"
                             data-has-access="${hasAccess}">
                            <img src="${chatbot.image ? chatbot.image : '/static/images/default-chatbot.png'}" 
                                 alt="${chatbot.name}" 
                                 class="enhanced-option-img" 
                                 onerror="this.src='/static/images/default-chatbot.png'">
                            <div class="enhanced-option-content">
                                <span class="enhanced-option-text">${chatbot.name}</span>
                                <small class="enhanced-option-desc">${chatbot.description || ''}</small>
                            </div>
                            <span class="enhanced-option-badge ${badgeClass}">${badgeText}</span>
                        </div>
                    `;
                });
                
                if (optionsList) optionsList.innerHTML = html;
                
                // Add click listeners for options
                document.querySelectorAll('.chatbot-option').forEach(option => {
                    option.addEventListener('click', function() {
                        // Get data attributes
                        const hasAccess = this.dataset.hasAccess === 'true';
                        
                        // Check if user has access to this chatbot
                        if (!hasAccess) {
                            // Show error message and prevent proceeding
                            showConfirmationMessage('شما دسترسی لازم برای استفاده از این چت‌بات را ندارید. لطفاً اشتراک مناسب را تهیه کنید.', 'warning');
                            return;
                        }
                        
                        // Remove selected class from all options
                        document.querySelectorAll('.chatbot-option').forEach(opt => {
                            opt.classList.remove('selected');
                        });
                        
                        // Add selected class to clicked option
                        this.classList.add('selected');
                        
                        // Get data attributes
                        const chatbotId = this.dataset.chatbotId;
                        const imgSrc = this.dataset.image ? this.dataset.image : '/static/images/default-chatbot.png';
                        const name = this.dataset.name;
                        const description = this.dataset.description;
                        
                        // Update select display
                        const display = chatbotContainer.querySelector('.select-display');
                        const placeholder = chatbotContainer.querySelector('.select-placeholder');
                        const value = chatbotContainer.querySelector('.select-value');
                        
                        if (display && placeholder && value) {
                            placeholder.classList.add('d-none');
                            value.classList.remove('d-none');
                            value.innerHTML = `
                                <img src="${imgSrc}" alt="${name}" class="select-value-img" onerror="this.src='/static/images/default-chatbot.png'">
                                <span>${name}</span>
                            `;
                        }
                        
                        // Hide dropdown
                        const dropdown = chatbotContainer.querySelector('.select-dropdown');
                        if (dropdown) {
                            dropdown.style.display = 'none';
                        }
                        chatbotContainer.classList.remove('open');
                        chatbotContainer.setAttribute('aria-expanded', 'false');
                        
                        // Update chatbot details card
                        const detailsCard = document.querySelector('.chatbot-details-card');
                        const detailImg = detailsCard?.querySelector('.chatbot-detail-img');
                        const detailName = detailsCard?.querySelector('.chatbot-detail-name');
                        const detailDesc = detailsCard?.querySelector('.chatbot-detail-desc');
                        const detailBadge = detailsCard?.querySelector('.chatbot-access-badge');
                        
                        if (detailsCard) {
                            detailsCard.classList.remove('d-none');
                            
                            if (detailImg) {
                                detailImg.src = imgSrc;
                                detailImg.alt = name;
                                detailImg.onerror = function() {
                                    this.src = '/static/images/default-chatbot.png';
                                };
                            }
                            
                            if (detailName) detailName.textContent = name;
                            if (detailDesc) detailDesc.textContent = description || 'بدون توضیح';
                            
                            if (detailBadge) {
                                detailBadge.textContent = hasAccess ? 'رایگان' : 'نیاز به اشتراک';
                                detailBadge.className = 'chatbot-access-badge badge ' + (hasAccess ? 'free' : 'premium');
                            }
                        }
                        
                        // Store selected chatbot ID
                        chatbotContainer.dataset.selected = chatbotId;
                        
                        // Load models for this chatbot
                        loadModelsForChatbot(chatbotId);
                        
                        // If there's only one chatbot, automatically proceed to step 3
                        if (chatbots.length === 1) {
                            setTimeout(() => showStep(3), 300);
                        } else {
                            // Automatically proceed to step 3
                            setTimeout(() => showStep(3), 300);
                        }
                    });
                });
                
                // Add keyboard navigation
                addKeyboardNavigation(chatbotContainer);
                
                // Automatically open the chatbot selection dropdown
                setTimeout(() => {
                    chatbotContainer.classList.add('open');
                    chatbotContainer.setAttribute('aria-expanded', 'true');
                    const dropdown = chatbotContainer.querySelector('.select-dropdown');
                    if (dropdown) {
                        dropdown.style.display = 'block';
                    }
                }, 100);
                
                // If there's only one chatbot, automatically select it
                if (chatbots.length === 1) {
                    setTimeout(() => {
                        const firstOption = document.querySelector('.chatbot-option');
                        if (firstOption) {
                            firstOption.click();
                        }
                    }, 300);
                }
            })
            .catch(error => {
                console.error('Error loading chatbots:', error);
                
                // Hide loading state and show error
                if (loadingEl) loadingEl.classList.add('d-none');
                if (emptyEl) {
                    emptyEl.innerHTML = '<i class="fas fa-exclamation-circle me-2"></i><span>خطا در بارگذاری چت‌بات‌ها</span>';
                    emptyEl.classList.remove('d-none');
                }
            });
    };
    
    // Function to add keyboard navigation to select
    function addKeyboardNavigation(selectElement) {
        const options = selectElement.querySelectorAll('.enhanced-option');
        if (options.length === 0) return;
        
        let currentIndex = -1;
        
        selectElement.addEventListener('keydown', function(e) {
            if (!selectElement.classList.contains('open')) return;
            
            switch (e.key) {
                case 'ArrowDown':
                    e.preventDefault();
                    currentIndex = (currentIndex + 1) % options.length;
                    highlightOption(options, currentIndex);
                    break;
                case 'ArrowUp':
                    e.preventDefault();
                    currentIndex = currentIndex <= 0 ? options.length - 1 : currentIndex - 1;
                    highlightOption(options, currentIndex);
                    break;
                case 'Enter':
                    e.preventDefault();
                    if (currentIndex >= 0 && currentIndex < options.length) {
                        options[currentIndex].click();
                    }
                    break;
                case 'Escape':
                    selectElement.classList.remove('open');
                    selectElement.setAttribute('aria-expanded', 'false');
                    const dropdown = selectElement.querySelector('.select-dropdown');
                    if (dropdown) dropdown.style.display = 'none';
                    break;
            }
        });
        
        // Reset index when dropdown is closed
        selectElement.addEventListener('blur', function() {
            setTimeout(() => {
                if (!selectElement.matches(':focus')) {
                    currentIndex = -1;
                }
            }, 100);
        });
    }
    
    function highlightOption(options, index) {
        options.forEach((option, i) => {
            if (i === index) {
                option.classList.add('selected');
                option.scrollIntoView({ block: 'nearest' });
            } else {
                option.classList.remove('selected');
            }
        });
    }
    
    // Modified loadModelsForChatbot to use enhanced select with images
    window.loadModelsForChatbot = function(chatbotId) {
        console.log('Loading models for chatbot:', chatbotId);
        const modelContainer = document.getElementById('modal-model-select');
        if (!modelContainer) return;
        
        // Show loading state
        const loadingEl = modelContainer.querySelector('.select-loading');
        const emptyEl = modelContainer.querySelector('.select-empty');
        const optionsList = modelContainer.querySelector('.select-options-list');
        
        if (loadingEl) loadingEl.classList.remove('d-none');
        if (emptyEl) emptyEl.classList.add('d-none');
        if (optionsList) optionsList.innerHTML = '';
        
        fetch(`/chat/chatbot/${chatbotId}/models/`)
            .then(response => response.json())
            .then(data => {
                console.log('Models data received:', data);
                const models = data.models || [];
                
                // Hide loading state
                if (loadingEl) loadingEl.classList.add('d-none');
                
                if (models.length === 0) {
                    if (emptyEl) emptyEl.classList.remove('d-none');
                    return;
                }
                
                let html = '';
                models.forEach(model => {
                    const isFree = model.is_free;
                    const hasAccess = model.user_has_access;
                    const badgeClass = isFree ? 'free' : 'premium';
                    const badgeText = isFree ? 'رایگان' : 'ویژه';
                    const costMultiplier = parseFloat(model.token_cost_multiplier || 1);
                    
                    // Add a class to indicate access status
                    const accessClass = hasAccess ? '' : 'restricted-option';
                    
                    html += `
                        <div class="enhanced-option model-option ${accessClass}" 
                             data-model-id="${model.model_id}" 
                             data-token-cost-multiplier="${costMultiplier}"
                             data-image="${model.image_url || ''}"
                             data-name="${model.name}"
                             data-description="${model.description || ''}"
                             data-is-free="${isFree}"
                             data-has-access="${hasAccess}">
                            <img src="${model.image_url ? model.image_url : '/static/images/default-model.png'}" 
                                 alt="${model.name}" 
                                 class="enhanced-option-img" 
                                 onerror="this.src='/static/images/default-model.png'">
                            <div class="enhanced-option-content">
                                <span class="enhanced-option-text">${model.name}</span>
                                <small class="enhanced-option-desc">${model.description || ''}</small>
                            </div>
                            <span class="enhanced-option-badge ${badgeClass}">${badgeText}</span>
                        </div>
                    `;
                });
                
                if (optionsList) optionsList.innerHTML = html;
                
                // Add click listeners for options
                const modelOptions = document.querySelectorAll('.model-option');
                modelOptions.forEach(option => {
                    option.addEventListener('click', function() {
                        // Get data attributes
                        const hasAccess = this.dataset.hasAccess === 'true';
                        
                        // Check if user has access to this model
                        if (!hasAccess) {
                            // Show error message and prevent proceeding
                            showConfirmationMessage('شما دسترسی لازم برای استفاده از این مدل را ندارید. لطفاً اشتراک مناسب را تهیه کنید.', 'warning');
                            return;
                        }
                        
                        // Remove selected class from all options
                        modelOptions.forEach(opt => {
                            opt.classList.remove('selected');
                        });
                        
                        // Add selected class to clicked option
                        this.classList.add('selected');
                        
                        // Get data attributes
                        const modelId = this.dataset.modelId;
                        const imgSrc = this.dataset.image ? this.dataset.image : '/static/images/default-model.png';
                        const name = this.dataset.name;
                        const description = this.dataset.description;
                        const isFree = this.dataset.isFree === 'true';
                        const costMultiplier = parseFloat(this.dataset.tokenCostMultiplier || 1);
                        
                        // Update select display
                        const display = modelContainer.querySelector('.select-display');
                        const placeholder = modelContainer.querySelector('.select-placeholder');
                        const value = modelContainer.querySelector('.select-value');
                        
                        if (display && placeholder && value) {
                            placeholder.classList.add('d-none');
                            value.classList.remove('d-none');
                            value.innerHTML = `
                                <img src="${imgSrc}" alt="${name}" class="select-value-img" onerror="this.src='/static/images/default-model.png'">
                                <span>${name}</span>
                            `;
                        }
                        
                        // Hide dropdown
                        const dropdown = modelContainer.querySelector('.select-dropdown');
                        if (dropdown) {
                            dropdown.style.display = 'none';
                        }
                        modelContainer.classList.remove('open');
                        modelContainer.setAttribute('aria-expanded', 'false');
                        
                        // Update model details card
                        const detailsCard = document.querySelector('.model-details-card');
                        const detailImg = detailsCard?.querySelector('.model-detail-img');
                        const detailName = detailsCard?.querySelector('.model-detail-name');
                        const detailDesc = detailsCard?.querySelector('.model-detail-desc');
                        const detailBadge = detailsCard?.querySelector('.model-access-badge');
                        const costWarning = detailsCard?.querySelector('.model-cost-warning');
                        const warningText = detailsCard?.querySelector('.warning-text');
                        
                        if (detailsCard) {
                            detailsCard.classList.remove('d-none');
                            
                            if (detailImg) {
                                detailImg.src = imgSrc;
                                detailImg.alt = name;
                                detailImg.onerror = function() {
                                    this.src = '/static/images/default-model.png';
                                };
                            }
                            
                            if (detailName) detailName.textContent = name;
                            if (detailDesc) detailDesc.textContent = description || 'بدون توضیح';
                            
                            if (detailBadge) {
                                detailBadge.textContent = isFree ? 'رایگان' : 'ویژه';
                                detailBadge.className = 'model-access-badge badge ' + (isFree ? 'free' : 'premium');
                            }
                            
                            // Show cost warning if applicable
                            if (costWarning && warningText) {
                                if (costMultiplier > 1) {
                                    costWarning.classList.remove('d-none');
                                    warningText.textContent = `این مدل دارای ضریب هزینه ${costMultiplier} است`;
                                } else {
                                    costWarning.classList.add('d-none');
                                }
                            }
                        }
                        
                        // Store selected model ID
                        modelContainer.dataset.selected = modelId;
                        
                        // Enable the create chat button
                        const createBtn = document.getElementById('create-chat-btn');
                        if (createBtn) {
                            createBtn.disabled = false;
                        }
                        
                        // Automatically show the create chat button
                        const nextBtn = document.getElementById('next-step-btn');
                        const prevBtn = document.getElementById('prev-step-btn');
                        if (nextBtn) nextBtn.style.display = 'none';
                        if (prevBtn) prevBtn.style.display = 'block';
                        if (createBtn) createBtn.style.display = 'block';
                        
                        // If there's only one model, automatically create the chat
                        if (models.length === 1) {
                            setTimeout(() => {
                                if (createBtn) {
                                    createBtn.click();
                                }
                            }, 300);
                        }
                    });
                });
                
                // Add keyboard navigation
                addKeyboardNavigation(modelContainer);
                
                // Automatically open the model selection dropdown
                setTimeout(() => {
                    modelContainer.classList.add('open');
                    modelContainer.setAttribute('aria-expanded', 'true');
                    const dropdown = modelContainer.querySelector('.select-dropdown');
                    if (dropdown) {
                        dropdown.style.display = 'block';
                    }
                }, 100);
                
                // If there's only one model, automatically select it
                if (models.length === 1) {
                    setTimeout(() => {
                        const firstOption = document.querySelector('.model-option');
                        if (firstOption) {
                            firstOption.click();
                        }
                    }, 300);
                }
            })
            .catch(error => {
                console.error('Error loading models:', error);
                
                // Hide loading state and show error
                if (loadingEl) loadingEl.classList.add('d-none');
                if (emptyEl) {
                    emptyEl.innerHTML = '<i class="fas fa-exclamation-circle me-2"></i><span>خطا در بارگذاری مدل‌ها</span>';
                    emptyEl.classList.remove('d-none');
                }
            });
    }
    
    // Send message form submission
    const chatForm = document.getElementById('chat-form');
    if (chatForm) {
        chatForm.addEventListener('submit', function(event) {
            event.preventDefault();
            sendMessage();
        });
    }
    
    // Send message button (for direct click as well)
    const sendButton = document.getElementById('send-button');
    if (sendButton && chatForm) {
        sendButton.addEventListener('click', function(event) {
            event.preventDefault();
            chatForm.dispatchEvent(new Event('submit'));
        });
    }
    
    // Enter key in message input
    const msgInput = document.getElementById('message-input');
    if (msgInput && chatForm) {
        msgInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                chatForm.dispatchEvent(new Event('submit'));
            }
        });
    }
    
    // Delete session button
    const deleteSessionBtn = document.getElementById('delete-session-btn');
    if (deleteSessionBtn) {
        deleteSessionBtn.addEventListener('click', deleteSession);
    }
    
    // Web search button
    const webSearchBtn = document.getElementById('web-search-btn');
    if (webSearchBtn) {
        webSearchBtn.addEventListener('click', toggleWebSearch);
    }
    
    // Image generation button
    const imageGenerationBtn = document.getElementById('image-generation-btn');
    if (imageGenerationBtn) {
        imageGenerationBtn.addEventListener('click', toggleImageGeneration);
    }
    
    // Mobile sidebar toggle - moved from base.html to here where sidebar exists
    if (mobileMenuToggle) {
        mobileMenuToggle.addEventListener('click', function(e) {
            e.stopPropagation(); // Prevent event bubbling
            
            // Check if we're on mobile view
            if (window.innerWidth < 768) {
                // On chat page, open the mobile menu container instead of sidebar
                const mobileMenuContainer = document.getElementById('mobile-menu-container');
                const mobileOverlay = document.getElementById('mobile-overlay');
                
                if (mobileMenuContainer) {
                    mobileMenuContainer.classList.toggle('open');
                    document.body.classList.toggle('mobile-menu-open');
                    if (mobileOverlay) {
                        mobileOverlay.classList.toggle('show');
                    }
                }
            } else {
                // On desktop, toggle the sidebar
                toggleSidebar();
            }
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
            
            const currentSessionTitle = document.getElementById('current-session-title');
            if (currentSessionTitle) {
                currentSessionTitle.innerHTML = `
                    <i class="fas fa-comments"></i> چت را انتخاب کنید یا جدیدی ایجاد کنید
                `;
            }
            
            const chatContainer = document.getElementById('chat-container');
            if (chatContainer) {
                chatContainer.innerHTML = `
                    <div class="text-center text-muted welcome-message" id="welcome-message">
                        <i class="fas fa-robot fa-3x mb-3"></i>
                        <h4>به چت‌بات MobixAI خوش آمدید</h4>
                        <p class="mb-0">چتی را انتخاب کنید یا چت جدیدی شروع کنید</p>
                    </div>
                `;
            }
            
            const messageInput = document.getElementById('message-input');
            if (messageInput) {
                messageInput.disabled = true;
            }
            
            const sendButton = document.getElementById('send-button');
            if (sendButton) {
                sendButton.disabled = true;
            }
            
            const deleteSessionBtn = document.getElementById('delete-session-btn');
            if (deleteSessionBtn) {
                deleteSessionBtn.style.display = 'none';
            }
            
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
            loadDesktopSidebarMenuItems();
            loadSidebarMenuItems();
            
            // Check web search access for welcome screen
            checkWebSearchAccessForWelcome();
        }
    });
    
    // Reload sidebar menu items on window resize
    window.addEventListener('resize', function() {
        if (window.innerWidth >= 768) {
            // On desktop, reload desktop menu items
            loadDesktopSidebarMenuItems();
        } else {
            // On mobile, ensure sidebar and overlay are hidden and reload menu items
            const sidebar = document.getElementById('sidebar');
            const sidebarOverlay = document.getElementById('sidebar-overlay');
            if (sidebar) {
                sidebar.classList.remove('show');
            }
            if (sidebarOverlay) {
                sidebarOverlay.classList.remove('show');
            }
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
        const modelImage = model.image_url || '/static/images/default-model.PNG';
        
        modelCard.innerHTML = `
            <img src="${modelImage}" alt="${model.name}" onerror="this.src='/static/images/default-model.PNG'">
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
        confirmation.className = 'alert alert-info alert-dismissible fade show';
        confirmation.style.cssText = 'position: fixed; top: 20px; right: 20px; z-index: 9999; max-width: 300px;';
        confirmation.innerHTML = `
            <strong>توجه!</strong> مدل پیشفرض برای چت‌های بعدی به ${modelName} تغییر یافت.
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

// Interaction Type Selection (Step 1)
function initializeInteractionTypeSelection() {
    console.log('Initializing interaction type selection');
    
    // Use event delegation to handle clicks on interaction type options
    const step1 = document.getElementById('step-1');
    if (step1) {
        console.log('Step 1 element found, adding event listener');
        step1.addEventListener('click', function(e) {
            console.log('Click event triggered on step 1');
            // Check if clicked element or its parent has the interaction-type-option class
            let target = e.target;
            while (target && target !== step1) {
                if (target.classList.contains('interaction-type-option')) {
                    console.log('Interaction type option clicked:', target);
                    const interactionType = target.dataset.interactionType;
                    console.log('Interaction type:', interactionType);
                    
                    // Remove active class from all options
                    document.querySelectorAll('.interaction-type-option').forEach(opt => {
                        opt.querySelector('.interaction-type-btn').classList.remove('active');
                    });
                    
                    // Add active class to clicked option
                    target.querySelector('.interaction-type-btn').classList.add('active');
                    
                    // Automatically proceed to step 2
                    console.log('Loading chatbots and showing step 2');
                    setTimeout(() => {
                        loadChatbotsByType(interactionType);
                        showStep(2);
                    }, 300);
                    break;
                }
                target = target.parentElement;
            }
        });
    } else {
        console.log('Step 1 element not found');
    }
}

// Reset modal when it's opened
const newChatModal = document.getElementById('newChatModal');
if (newChatModal) {
    newChatModal.addEventListener('show.bs.modal', function () {
        // Reset to step 1
        showStep(1);
        
        // Reset all selects
        document.querySelectorAll('.enhanced-select').forEach(select => {
            // Reset display
            const placeholder = select.querySelector('.select-placeholder');
            const value = select.querySelector('.select-value');
            if (placeholder && value) {
                placeholder.classList.remove('d-none');
                value.classList.add('d-none');
                value.innerHTML = '';
            }
            
            // Close dropdown
            const dropdown = select.querySelector('.select-dropdown');
            if (dropdown) {
                dropdown.style.display = 'none';
            }
            select.classList.remove('open');
            select.setAttribute('aria-expanded', 'false');
            
            // Clear selections
            delete select.dataset.selected;
            
            // Clear options
            const optionsList = select.querySelector('.select-options-list');
            if (optionsList) optionsList.innerHTML = '';
            
            // Show placeholder elements
            const emptyEl = select.querySelector('.select-empty');
            if (emptyEl) emptyEl.classList.add('d-none');
        });
        
        // Hide detail cards
        document.querySelectorAll('.chatbot-details-card, .model-details-card').forEach(card => {
            card.classList.add('d-none');
        });
        
        // Reset interaction type buttons
        document.querySelectorAll('.interaction-type-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        
        // Hide create chat button
        const createBtn = document.getElementById('create-chat-btn');
        const nextBtn = document.getElementById('next-step-btn');
        if (createBtn) {
            createBtn.style.display = 'none';
            createBtn.disabled = true;
        }
        if (nextBtn) nextBtn.style.display = 'block';
    });
}

// Initialize enhanced select behavior when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeEnhancedSelect();
    initializeInteractionTypeSelection();
});

// Function to show confirmation messages
function showConfirmationMessage(message, type = 'info') {
    // Remove any existing confirmation messages
    const existingMessage = document.querySelector('.confirmation-message');
    if (existingMessage) {
        existingMessage.remove();
    }
    
    // Create confirmation message element
    const messageElement = document.createElement('div');
    messageElement.className = `confirmation-message alert alert-${type} alert-dismissible fade show position-fixed`;
    messageElement.style.cssText = `
        top: 20px;
        left: 50%;
        transform: translateX(-50%);
        z-index: 9999;
        min-width: 300px;
        max-width: 500px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    `;
    messageElement.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    // Add to document
    document.body.appendChild(messageElement);
    
    // Auto remove after 3 seconds
    setTimeout(() => {
        if (messageElement.parentNode) {
            messageElement.parentNode.removeChild(messageElement);
        }
    }, 3000);
}

// Modal step navigation
function showStep(step) {
    // Hide all steps
    document.querySelectorAll('.modal-step').forEach(stepElement => {
        stepElement.classList.remove('active');
    });
    
    // Show current step
    const currentStep = document.getElementById(`step-${step}`);
    if (currentStep) {
        currentStep.classList.add('active');
    }
    
    // Update button visibility
    const prevBtn = document.getElementById('prev-step-btn');
    const nextBtn = document.getElementById('next-step-btn');
    const createBtn = document.getElementById('create-chat-btn');
    
    if (step === 1) {
        if (prevBtn) prevBtn.style.display = 'none';
        if (nextBtn) nextBtn.style.display = 'block';
        if (createBtn) createBtn.style.display = 'none';
    } else if (step === 3) {
        if (prevBtn) prevBtn.style.display = 'block';
        if (nextBtn) nextBtn.style.display = 'none';
        if (createBtn) createBtn.style.display = 'block';
    } else {
        if (prevBtn) prevBtn.style.display = 'block';
        if (nextBtn) nextBtn.style.display = 'block';
        if (createBtn) createBtn.style.display = 'none';
    }
}

// Handle clicks outside of select elements
function handleOutsideClick(e) {
    if (!e.target.closest('.enhanced-select')) {
        document.querySelectorAll('.enhanced-select.open').forEach(select => {
            select.classList.remove('open');
            select.setAttribute('aria-expanded', 'false');
            const dropdown = select.querySelector('.select-dropdown');
            if (dropdown) dropdown.style.display = 'none';
        });
    }
}

// Initialize enhanced select behavior
function initializeEnhancedSelect() {
    const selectElements = document.querySelectorAll('.enhanced-select');
    
    selectElements.forEach(select => {
        const trigger = select.querySelector('.select-trigger');
        const dropdown = select.querySelector('.select-dropdown');
        const searchInput = select.querySelector('.search-input');
        
        if (trigger) {
            // Remove any existing event listeners to prevent duplicates
            const newTrigger = trigger.cloneNode(true);
            trigger.parentNode.replaceChild(newTrigger, trigger);
            
            // Add click event listener
            newTrigger.addEventListener('click', function(e) {
                // Prevent closing when clicking on search input
                if (e.target.closest('.search-input')) return;
                
                // Toggle open state
                select.classList.toggle('open');
                const isOpen = select.classList.contains('open');
                select.setAttribute('aria-expanded', isOpen.toString());
                
                // Show/hide dropdown
                if (dropdown) {
                    dropdown.style.display = isOpen ? 'block' : 'none';
                }
                
                // Focus search input when opening
                if (isOpen && searchInput) {
                    setTimeout(() => searchInput.focus(), 100);
                }
                
                console.log('Select clicked, isOpen:', isOpen);
            });
        }
        
        if (searchInput) {
            // Remove any existing event listeners to prevent duplicates
            const newSearchInput = searchInput.cloneNode(true);
            searchInput.parentNode.replaceChild(newSearchInput, searchInput);
            
            // Add input event listener
            newSearchInput.addEventListener('input', function() {
                const searchTerm = this.value.toLowerCase();
                const options = select.querySelectorAll('.enhanced-option');
                
                options.forEach(option => {
                    const text = option.textContent.toLowerCase();
                    option.style.display = text.includes(searchTerm) ? 'flex' : 'none';
                });
            });
        }
    });
    
    // Close dropdown when clicking outside
    document.removeEventListener('click', handleOutsideClick); // Remove previous listener
    document.addEventListener('click', handleOutsideClick);
}

// Load advertising banner
function loadAdvertisingBanner() {
    fetch('/random-advertising-banner/')
        .then(response => response.json())
        .then(data => {
            if (data.banner) {
                const bannerContainer = document.getElementById('advertising-banner-container');
                const bannerLink = document.getElementById('advertising-banner-link');
                const bannerImage = document.getElementById('advertising-banner-image');
                
                if (bannerContainer && bannerLink && bannerImage) {
                    // Set banner data
                    bannerLink.href = data.banner.link || '#';
                    if (data.banner.image_url) {
                        bannerImage.src = data.banner.image_url;
                        bannerImage.alt = data.banner.title || 'Advertisement';
                        // Show banner
                        bannerContainer.style.display = 'block';
                    } else {
                        // Hide banner if no image
                        bannerContainer.style.display = 'none';
                    }
                }
            }
            // If no banner data, keep the container hidden (default)
        })
        .catch(error => {
            console.error('Error loading advertising banner:', error);
            // Hide banner container on error
            const bannerContainer = document.getElementById('advertising-banner-container');
            if (bannerContainer) {
                bannerContainer.style.display = 'none';
            }
        });
}

// Load advertising banner when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    loadAdvertisingBanner();
});