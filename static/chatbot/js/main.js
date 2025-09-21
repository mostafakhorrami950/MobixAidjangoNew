// =================================
// فایل اصلی اجرا و رویداد‌ها (Main Execution & Event Handlers)
// =================================

// Global variables to store selected options for new session
let selectedModelForNewSession = null;
let isWebSearchEnabledForNewSession = false;
// Store model data for cost multiplier checking
let availableModelsData = [];

// Touch interaction variables
let touchStartX = 0;
let touchStartY = 0;
let touchEndX = 0;
let touchEndY = 0;

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
    
    // Add input focus management for mobile
    function manageInputFocus() {
        const messageInput = document.getElementById('message-input');
        if (!messageInput) return;
        
        // Focus input when chat container is clicked (mobile-friendly)
        const chatContainer = document.getElementById('chat-container');
        if (chatContainer) {
            chatContainer.addEventListener('click', function(e) {
                // Only focus if we're not clicking on a button or link
                if (!e.target.closest('button, a, .message-actions, .file-actions')) {
                    messageInput.focus();
                }
            });
        }
        
        // Handle viewport height changes (keyboard opening/closing on mobile)
        let initialViewportHeight = window.innerHeight;
        window.addEventListener('resize', function() {
            const currentHeight = window.innerHeight;
            const heightDifference = initialViewportHeight - currentHeight;
            
            // If keyboard is open (viewport height decreased significantly)
            if (heightDifference > 150) {
                // Scroll to bottom to keep input visible
                setTimeout(scrollToBottom, 100);
            }
        });
    }
    
    // Call input focus management
    manageInputFocus();
    
    // Add touch event listeners for swipe gestures
    setupTouchGestures();
    
    // Add long press detection for message actions
    setupLongPressDetection();
    
    // Add event listener for model selection in welcome area
    document.getElementById('welcome-model-select').addEventListener('change', function() {
        selectedModelForNewSession = this.value;
        
        // Check if the selected model has a cost multiplier > 1 and show warning
        if (selectedModelForNewSession) {
            const selectedModel = availableModelsData.find(model => model.model_id === selectedModelForNewSession);
            if (selectedModel && selectedModel.token_cost_multiplier > 1) {
                // Show warning message
                showCostMultiplierWarning(selectedModel);
            } else {
                // Hide any existing warning
                hideCostMultiplierWarning();
            }
        } else {
            // Hide warning when no model is selected
            hideCostMultiplierWarning();
        }
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
    
    // Add keyboard handling for mobile navigation
    document.addEventListener('keydown', function(e) {
        // ESC key to close sidebar on mobile
        if (e.key === 'Escape' && window.innerWidth <= 768) {
            const sidebar = document.getElementById('sidebar');
            if (sidebar && sidebar.classList.contains('show')) {
                toggleSidebar();
            }
        }
    });
    
    // Add edit button to user messages after a short delay
    setTimeout(addEditButtonToUserMessages, 1000);
    
    // Add touch event listeners for mobile optimization
    setupMobileTouchEvents();
    
    // Add mobile input optimizations
    setupMobileInputOptimizations();
    
    // Add mobile navigation enhancements
    setupMobileNavigation();
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
            
            const modelSelect = document.getElementById('welcome-model-select');
            const modelSelectionContainer = document.getElementById('welcome-model-selection');
            const webSearchContainer = document.getElementById('welcome-web-search-container');
            
            // Check if elements exist before manipulating them
            if (!modelSelect || !modelSelectionContainer) {
                console.warn('Model selection elements not found, skipping model loading');
                return;
            }
            
            // Clear current options
            modelSelect.innerHTML = '<option value="">-- مدلی را انتخاب کنید --</option>';
            
            // Populate model select
            data.models.forEach(model => {
                const option = document.createElement('option');
                option.value = model.model_id;
                
                // Add access information to the text
                if (model.is_free) {
                    option.textContent = `${model.name} (رایگان)`;
                    option.className = 'model-option-free';
                } else {
                    if (model.user_has_access) {
                        option.textContent = `${model.name} (ویژه)`;
                        option.className = 'model-option-premium';
                    } else {
                        option.textContent = `${model.name} (نیاز به اشتراک)`;
                        option.className = 'model-option-disabled';
                        option.disabled = true;
                    }
                }
                
                // Disable option if user doesn't have access
                if (!model.user_has_access) {
                    option.disabled = true;
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
        // Insert after the model selection container
        const modelSelectionContainer = document.getElementById('welcome-model-selection');
        modelSelectionContainer.parentNode.insertBefore(warningElement, modelSelectionContainer.nextSibling);
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

// Setup touch gestures for mobile interaction
function setupTouchGestures() {
    const chatContainer = document.getElementById('chat-container');
    const sidebar = document.getElementById('sidebar');
    
    if (!chatContainer || !sidebar) return;
    
    // Add touch event listeners for swipe gestures
    chatContainer.addEventListener('touchstart', handleTouchStart, false);
    chatContainer.addEventListener('touchmove', handleTouchMove, false);
    chatContainer.addEventListener('touchend', handleTouchEnd, false);
    
    // Add touch event listeners for sidebar swipe
    sidebar.addEventListener('touchstart', handleSidebarTouchStart, false);
    sidebar.addEventListener('touchmove', handleSidebarTouchMove, false);
    sidebar.addEventListener('touchend', handleSidebarTouchEnd, false);
}

// Handle touch start for main chat area
function handleTouchStart(evt) {
    touchStartX = evt.touches[0].clientX;
    touchStartY = evt.touches[0].clientY;
}

// Handle touch move for main chat area
function handleTouchMove(evt) {
    // Prevent scrolling during swipe
    if (Math.abs(touchStartX - evt.touches[0].clientX) > 10) {
        evt.preventDefault();
    }
}

// Handle touch end for main chat area
function handleTouchEnd(evt) {
    touchEndX = evt.changedTouches[0].clientX;
    touchEndY = evt.changedTouches[0].clientY;
    
    handleSwipeGesture();
}

// Handle swipe gesture
function handleSwipeGesture() {
    const deltaX = touchEndX - touchStartX;
    const deltaY = touchEndY - touchStartY;
    const absDeltaX = Math.abs(deltaX);
    const absDeltaY = Math.abs(deltaY);
    
    // Minimum swipe distance
    const minSwipeDistance = 50;
    
    // Check if it's a horizontal swipe
    if (absDeltaX > absDeltaY && absDeltaX > minSwipeDistance) {
        if (deltaX > 0) {
            // Swipe right - open sidebar on mobile
            if (window.innerWidth <= 768) {
                toggleSidebar();
            }
        } else {
            // Swipe left - close sidebar on mobile
            if (window.innerWidth <= 768) {
                const sidebar = document.getElementById('sidebar');
                if (sidebar && sidebar.classList.contains('show')) {
                    toggleSidebar();
                }
            }
        }
    }
}

// Handle touch start for sidebar
function handleSidebarTouchStart(evt) {
    touchStartX = evt.touches[0].clientX;
    touchStartY = evt.touches[0].clientY;
}

// Handle touch move for sidebar
function handleSidebarTouchMove(evt) {
    // Prevent scrolling during swipe
    if (Math.abs(touchStartX - evt.touches[0].clientX) > 10) {
        evt.preventDefault();
    }
}

// Handle touch end for sidebar
function handleSidebarTouchEnd(evt) {
    touchEndX = evt.changedTouches[0].clientX;
    touchEndY = evt.changedTouches[0].clientY;
    
    handleSidebarSwipeGesture();
}

// Handle sidebar swipe gesture
function handleSidebarSwipeGesture() {
    const deltaX = touchEndX - touchStartX;
    const deltaY = touchEndY - touchStartY;
    const absDeltaX = Math.abs(deltaX);
    const absDeltaY = Math.abs(deltaY);
    
    // Minimum swipe distance
    const minSwipeDistance = 50;
    
    // Check if it's a horizontal swipe to the left (close sidebar)
    if (absDeltaX > absDeltaY && absDeltaX > minSwipeDistance && deltaX < 0) {
        // Close sidebar on mobile
        if (window.innerWidth <= 768) {
            const sidebar = document.getElementById('sidebar');
            if (sidebar && sidebar.classList.contains('show')) {
                toggleSidebar();
            }
        }
    }
}

// Setup long press detection for message actions
function setupLongPressDetection() {
    const chatContainer = document.getElementById('chat-container');
    if (!chatContainer) return;
    
    let pressTimer;
    
    // Add event listeners to message elements
    chatContainer.addEventListener('touchstart', function(e) {
        // Check if we're touching a message element
        const messageElement = e.target.closest('.message-user, .message-assistant');
        if (messageElement) {
            pressTimer = setTimeout(function() {
                // Show message actions on long press
                showMessageActions(messageElement);
            }, 500); // 500ms for long press
        }
    });
    
    chatContainer.addEventListener('touchend', function(e) {
        clearTimeout(pressTimer);
    });
    
    chatContainer.addEventListener('touchmove', function(e) {
        clearTimeout(pressTimer);
    });
}

// Show message actions on long press
function showMessageActions(messageElement) {
    // Find or create message actions container
    let actionsContainer = messageElement.querySelector('.message-actions');
    
    if (!actionsContainer) {
        actionsContainer = document.createElement('div');
        actionsContainer.className = 'message-actions';
        
        // Add copy button
        const copyBtn = document.createElement('button');
        copyBtn.className = 'btn btn-sm';
        copyBtn.innerHTML = '<i class="fas fa-copy"></i> کپی';
        copyBtn.addEventListener('click', function() {
            copyMessageContent(messageElement);
        });
        
        // Add edit button for user messages
        if (messageElement.classList.contains('message-user')) {
            const editBtn = document.createElement('button');
            editBtn.className = 'btn btn-sm';
            editBtn.innerHTML = '<i class="fas fa-edit"></i> ویرایش';
            editBtn.addEventListener('click', function() {
                editMessage(messageElement);
            });
            actionsContainer.appendChild(editBtn);
        }
        
        actionsContainer.appendChild(copyBtn);
        messageElement.appendChild(actionsContainer);
    }
    
    // Show actions
    actionsContainer.style.display = 'flex';
    
    // Auto-hide after 3 seconds
    setTimeout(function() {
        if (actionsContainer.style.display === 'flex') {
            actionsContainer.style.display = 'none';
        }
    }, 3000);
}

// Copy message content to clipboard
function copyMessageContent(messageElement) {
    const content = messageElement.querySelector('.message-content').innerText;
    navigator.clipboard.writeText(content).then(function() {
        // Show success notification
        showNotification('محتوای پیام کپی شد', 'success');
    }).catch(function(err) {
        console.error('Could not copy text: ', err);
        showNotification('خطا در کپی محتوا', 'error');
    });
}

// Show notification message
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `alert alert-${type === 'error' ? 'danger' : type} position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; max-width: 300px;';
    notification.innerHTML = `
        <strong>${type === 'success' ? 'موفقیت' : type === 'error' ? 'خطا' : 'اطلاعات'}!</strong> ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto remove after 3 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }, 3000);
}

// Setup mobile touch events
function setupMobileTouchEvents() {
    // Add double tap to scroll to bottom
    let lastTap = 0;
    const chatContainer = document.getElementById('chat-container');
    
    if (chatContainer) {
        chatContainer.addEventListener('touchend', function(e) {
            const currentTime = new Date().getTime();
            const tapLength = currentTime - lastTap;
            
            if (tapLength < 500 && tapLength > 0) {
                // Double tap - scroll to bottom
                scrollToBottom();
                e.preventDefault();
            }
            
            lastTap = currentTime;
        });
    }
    
    // Add pinch to zoom for images
    setupImagePinchZoom();
}

// Setup pinch to zoom for images
function setupImagePinchZoom() {
    const images = document.querySelectorAll('.image-container img');
    
    images.forEach(function(img) {
        let scale = 1;
        let startDistance = 0;
        
        img.addEventListener('touchstart', function(e) {
            if (e.touches.length === 2) {
                // Two fingers - start pinch
                startDistance = Math.hypot(
                    e.touches[0].pageX - e.touches[1].pageX,
                    e.touches[0].pageY - e.touches[1].pageY
                );
            }
        });
        
        img.addEventListener('touchmove', function(e) {
            if (e.touches.length === 2) {
                // Two fingers - pinch in progress
                const currentDistance = Math.hypot(
                    e.touches[0].pageX - e.touches[1].pageX,
                    e.touches[0].pageY - e.touches[1].pageY
                );
                
                if (startDistance > 0) {
                    scale = currentDistance / startDistance;
                    
                    // Limit zoom between 1x and 3x
                    if (scale < 1) scale = 1;
                    if (scale > 3) scale = 3;
                    
                    img.style.transform = `scale(${scale})`;
                }
                
                e.preventDefault();
            }
        });
        
        img.addEventListener('touchend', function(e) {
            startDistance = 0;
            
            // Reset scale if it's close to 1
            if (scale < 1.1) {
                scale = 1;
                img.style.transform = '';
            }
        });
    });
}

// Setup mobile input optimizations
function setupMobileInputOptimizations() {
    const messageInput = document.getElementById('message-input');
    if (!messageInput) return;
    
    // Add focus handling for mobile keyboards
    messageInput.addEventListener('focus', function() {
        // Scroll to bottom when input is focused
        setTimeout(scrollToBottom, 300);
        
        // Add visual feedback for focus
        this.style.boxShadow = '0 0 0 2px var(--primary-blue)';
    });
    
    messageInput.addEventListener('blur', function() {
        // Remove focus styling
        this.style.boxShadow = '';
        
        // Scroll to bottom when input loses focus
        setTimeout(scrollToBottom, 300);
    });
    
    // Add input event listener for dynamic height adjustment
    messageInput.addEventListener('input', function() {
        // Auto-resize textarea
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight > 200 ? 200 : this.scrollHeight) + 'px';
        
        // Update send button state
        updateSendButtonState();
    });
    
    // Add key event handling for mobile
    messageInput.addEventListener('keydown', function(e) {
        // Handle Enter key on mobile
        if (e.key === 'Enter' && !e.shiftKey) {
            // On mobile, we might want to allow line breaks with Enter
            // But still send with a special combination
            if (e.ctrlKey || e.metaKey) {
                e.preventDefault();
                document.getElementById('chat-form').dispatchEvent(new Event('submit'));
            }
        }
        
        // Handle Escape key to blur input
        if (e.key === 'Escape') {
            this.blur();
        }
    });
    
    // Add paste handling for mobile
    messageInput.addEventListener('paste', function(e) {
        // Handle paste event for better mobile experience
        setTimeout(() => {
            // Auto-resize after paste
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight > 200 ? 200 : this.scrollHeight) + 'px';
        }, 100);
    });
    
    // Add long press detection for special actions
    let pressTimer;
    messageInput.addEventListener('touchstart', function(e) {
        pressTimer = setTimeout(() => {
            // Show special input options on long press
            showInputOptions(this);
        }, 1000);
    });
    
    messageInput.addEventListener('touchend', function(e) {
        clearTimeout(pressTimer);
    });
    
    messageInput.addEventListener('touchmove', function(e) {
        clearTimeout(pressTimer);
    });
}

// Show input options on long press
function showInputOptions(inputElement) {
    // Create a context menu for input options
    const menu = document.createElement('div');
    menu.className = 'input-options-menu position-fixed bg-white border rounded shadow';
    menu.style.cssText = 'z-index: 9999; padding: 10px;';
    
    // Get touch position
    const touch = event.touches[0] || event.changedTouches[0];
    menu.style.left = `${touch.clientX}px`;
    menu.style.top = `${touch.clientY}px`;
    
    // Add options
    menu.innerHTML = `
        <div class="d-flex flex-column gap-2">
            <button class="btn btn-sm btn-outline-primary" id="paste-btn">
                <i class="fas fa-paste"></i> جای‌گذاری
            </button>
            <button class="btn btn-sm btn-outline-secondary" id="clear-btn">
                <i class="fas fa-trash"></i> پاک کردن
            </button>
        </div>
    `;
    
    document.body.appendChild(menu);
    
    // Add event listeners
    document.getElementById('paste-btn').addEventListener('click', function() {
        navigator.clipboard.readText().then(text => {
            inputElement.value += text;
            inputElement.dispatchEvent(new Event('input'));
        }).catch(err => {
            console.error('Failed to read clipboard contents: ', err);
        });
        menu.remove();
    });
    
    document.getElementById('clear-btn').addEventListener('click', function() {
        inputElement.value = '';
        inputElement.dispatchEvent(new Event('input'));
        menu.remove();
    });
    
    // Remove menu when clicking elsewhere
    setTimeout(() => {
        document.addEventListener('click', function removeMenu() {
            menu.remove();
            document.removeEventListener('click', removeMenu);
        });
    }, 100);
}

// Setup mobile navigation enhancements
function setupMobileNavigation() {
    // Add click handlers for mobile navigation items
    const mobileNavMenu = document.getElementById('mobile-nav-menu');
    if (!mobileNavMenu) return;
    
    // Add delegated event listener for navigation links
    mobileNavMenu.addEventListener('click', function(e) {
        const navLink = e.target.closest('.nav-link');
        if (navLink) {
            // Close sidebar after navigation
            if (window.innerWidth <= 768) {
                const sidebar = document.getElementById('sidebar');
                if (sidebar && sidebar.classList.contains('show')) {
                    setTimeout(toggleSidebar, 150);
                }
            }
        }
    });
    
    // Add keyboard navigation support
    mobileNavMenu.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' || e.key === ' ') {
            const navLink = e.target.closest('.nav-link');
            if (navLink) {
                e.preventDefault();
                navLink.click();
            }
        }
    });
}

// Update send button state based on input content
function updateSendButtonState() {
    const messageInput = document.getElementById('message-input');
    const sendButton = document.getElementById('send-button');
    
    if (!messageInput || !sendButton) return;
    
    // Enable send button if there's content or files
    const hasContent = messageInput.value.trim().length > 0;
    const hasFiles = getSelectedFiles && getSelectedFiles().length > 0;
    
    sendButton.disabled = !(hasContent || hasFiles);
}
