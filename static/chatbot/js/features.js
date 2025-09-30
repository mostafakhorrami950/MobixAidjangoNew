// =================================
// مدیریت ویژگی‌ها و دسترسی (Features & Access Management)
// =================================

// Web search toggle
function toggleWebSearch() {
    if (!currentSessionId) return;
    
    const webSearchBtn = document.getElementById('web-search-btn');
    const isWebSearchActive = webSearchBtn.classList.contains('btn-success');
    
    if (isWebSearchActive) {
        // Disable web search
        webSearchBtn.classList.remove('btn-success');
        webSearchBtn.classList.add('btn-outline-secondary');
        webSearchBtn.innerHTML = '<i class="fas fa-search"></i> جستجو وب';
        webSearchBtn.title = 'فعال کردن جستجو وب';
        // Store that web search is disabled for this session
        sessionStorage.setItem(`webSearch_${currentSessionId}`, 'false');
    } else {
        // Enable web search
        webSearchBtn.classList.remove('btn-outline-secondary');
        webSearchBtn.classList.add('btn-success');
        webSearchBtn.innerHTML = '<i class="fas fa-search"></i> جستجو وب فعال';
        webSearchBtn.title = 'غیرفعال کردن جستجو وب';
        // Store that web search is enabled for this session
        sessionStorage.setItem(`webSearch_${currentSessionId}`, 'true');
    }
}

// Check if user has access to web search functionality in welcome area (no session yet)
function checkWebSearchAccessForWelcome() {
    // Make a request to check if user has access to web search functionality
    fetch('/chat/web-search-access/')
        .then(response => response.json())
        .then(data => {
            const webSearchBtn = document.getElementById('welcome-web-search-btn');
            const webSearchContainer = document.getElementById('welcome-web-search-container');
            
            if (!webSearchBtn || !webSearchContainer) return;
            
            // Show the web search container
            webSearchContainer.style.display = 'block';
            
            if (data.has_access) {
                // User has access, enable the button
                webSearchBtn.disabled = false;
                webSearchBtn.classList.remove('btn-secondary');
                webSearchBtn.classList.add('btn-outline-secondary');
                webSearchBtn.innerHTML = '<i class="fas fa-search"></i> جستجو وب';
                webSearchBtn.title = 'فعال کردن جستجو وب';
            } else {
                // User doesn't have access, disable the button and show special message
                webSearchBtn.disabled = true;
                webSearchBtn.classList.remove('btn-outline-secondary');
                webSearchBtn.classList.add('btn-secondary');
                webSearchBtn.innerHTML = '<i class="fas fa-search"></i> جستجو وب (فقط برای اشتراک ویژه)';
                webSearchBtn.title = 'این ویژگی فقط برای کاربران با اشتراک ویژه در دسترس است';
            }
        })
        .catch(error => {
            console.error('Error checking web search access:', error);
            // Hide the web search container if there's an error
            const webSearchContainer = document.getElementById('welcome-web-search-container');
            if (webSearchContainer) {
                webSearchContainer.style.display = 'none';
            }
        });
}

// Check if user has access to web search functionality
function checkWebSearchAccess(sessionId) {
    fetch(`/chat/session/${sessionId}/web-search-access/`)
        .then(response => response.json())
        .then(data => {
            const webSearchBtn = document.getElementById('web-search-btn');
            if (!webSearchBtn) return;
            
            // Check if this is an image editing chatbot
            const sessionData = JSON.parse(localStorage.getItem(`session_${sessionId}`) || '{}');
            if (sessionData.chatbot_type === 'image_editing') {
                // Hide web search for image editing chatbots
                webSearchBtn.style.display = 'none';
                return;
            }
            
            if (data.has_access) {
                // User has access, show the button
                webSearchBtn.style.display = 'inline-block';
                
                // Restore web search state for this session
                const webSearchState = sessionStorage.getItem(`webSearch_${sessionId}`);
                if (webSearchState === 'true') {
                    // Enable web search
                    webSearchBtn.classList.remove('btn-outline-secondary');
                    webSearchBtn.classList.add('btn-success');
                    webSearchBtn.innerHTML = '<i class="fas fa-search"></i> جستجو وب فعال';
                    webSearchBtn.title = 'غیرفعال کردن جستجو وب';
                } else {
                    // Disable web search
                    webSearchBtn.classList.remove('btn-success');
                    webSearchBtn.classList.add('btn-outline-secondary');
                    webSearchBtn.innerHTML = '<i class="fas fa-search"></i> جستجو وب';
                    webSearchBtn.title = 'فعال کردن جستجو وب';
                }
            } else {
                // User doesn't have access, show button as disabled with appropriate message
                webSearchBtn.style.display = 'inline-block';
                webSearchBtn.classList.remove('btn-outline-secondary', 'btn-success');
                webSearchBtn.classList.add('btn-secondary');
                webSearchBtn.disabled = true;
                webSearchBtn.innerHTML = '<i class="fas fa-search"></i> جستجو وب (فقط برای اشتراک ویژه)';
                webSearchBtn.title = 'این ویژگی فقط برای کاربران با اشتراک ویژه در دسترس است';
            }
        })
        .catch(error => {
            console.error('Error checking web search access:', error);
            // Hide the button if there's an error
            const webSearchBtn = document.getElementById('web-search-btn');
            if (webSearchBtn) {
                webSearchBtn.style.display = 'none';
            }
        });
}

// Add image generation toggle
function toggleImageGeneration() {
    if (!currentSessionId) return;
    
    const imageGenBtn = document.getElementById('image-generation-btn');
    const isImageGenActive = imageGenBtn.classList.contains('btn-primary');
    
    if (isImageGenActive) {
        // Disable image generation
        imageGenBtn.classList.remove('btn-primary');
        imageGenBtn.classList.add('btn-outline-primary');
        imageGenBtn.innerHTML = '<i class="fas fa-image"></i> تولید تصویر';
        imageGenBtn.title = 'فعال کردن تولید تصویر';
        // Store that image generation is disabled for this session
        sessionStorage.setItem(`imageGen_${currentSessionId}`, 'false');
    } else {
        // Enable image generation
        imageGenBtn.classList.remove('btn-outline-primary');
        imageGenBtn.classList.add('btn-primary');
        imageGenBtn.innerHTML = '<i class="fas fa-image"></i> تولید تصویر فعال';
        imageGenBtn.title = 'غیرفعال کردن تولید تصویر';
        // Store that image generation is enabled for this session
        sessionStorage.setItem(`imageGen_${currentSessionId}`, 'true');
    }
}

// Check if user has access to image generation functionality
function checkImageGenerationAccess(sessionId) {
    fetch(`/chat/session/${sessionId}/image-generation-access/`)
        .then(response => response.json())
        .then(data => {
            const imageGenBtn = document.getElementById('image-generation-btn');
            const webSearchBtn = document.getElementById('web-search-btn');
            if (!imageGenBtn) return;
            
            if (data.has_access) {
                // Check if this is an image editing chatbot
                const sessionData = JSON.parse(localStorage.getItem(`session_${sessionId}`) || '{}');
                if (sessionData.chatbot_type === 'image_editing') {
                    // For image editing chatbots:
                    // 1. Hide the image generation button (it's automatic)
                    imageGenBtn.style.display = 'none';
                    // 2. Enable image generation by default
                    sessionStorage.setItem(`imageGen_${currentSessionId}`, 'true');
                    // 3. Hide the web search button
                    if (webSearchBtn) {
                        webSearchBtn.style.display = 'none';
                    }
                } else {
                    // For other chatbots:
                    // 1. Show the image generation button
                    imageGenBtn.style.display = 'inline-block';
                    // 2. Show the web search button
                    if (webSearchBtn) {
                        webSearchBtn.style.display = 'inline-block';
                    }
                    // 3. Restore image generation state for this session
                    const imageGenState = sessionStorage.getItem(`imageGen_${sessionId}`);
                    if (imageGenState === 'true') {
                        // Enable image generation
                        imageGenBtn.classList.remove('btn-outline-primary');
                        imageGenBtn.classList.add('btn-primary');
                        imageGenBtn.innerHTML = '<i class="fas fa-image"></i> تولید تصویر فعال';
                        imageGenBtn.title = 'غیرفعال کردن تولید تصویر';
                    } else {
                        // Disable image generation
                        imageGenBtn.classList.remove('btn-primary');
                        imageGenBtn.classList.add('btn-outline-primary');
                        imageGenBtn.innerHTML = '<i class="fas fa-image"></i> تولید تصویر';
                        imageGenBtn.title = 'فعال کردن تولید تصویر';
                    }
                }
            } else {
                // User doesn't have access, hide the button
                imageGenBtn.style.display = 'none';
            }
        })
        .catch(error => {
            console.error('Error checking image generation access:', error);
            // Hide the button if there's an error
            const imageGenBtn = document.getElementById('image-generation-btn');
            if (imageGenBtn) {
                imageGenBtn.style.display = 'none';
            }
        });
}

// Load models for a specific chatbot
function loadModelsForChatbot(chatbotId) {
    const modelSelect = document.getElementById('modal-model-select');
    const modelDropdownMenu = document.getElementById('model-dropdown-menu');
    const modelDropdownSelected = document.getElementById('model-dropdown-selected');
    
    // Clear current options
    modelDropdownMenu.innerHTML = '<div class="model-dropdown-item disabled"><span class="model-dropdown-item-name">-- مدلی را انتخاب کنید --</span></div>';
    
    // Reset selected display
    modelDropdownSelected.innerHTML = '<span class="placeholder-text">انتخاب مدل...</span><i class="fas fa-chevron-down dropdown-arrow"></i>';
    
    // Load models for this chatbot
    fetch(`/chat/chatbot/${chatbotId}/models/`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error('Error loading models:', data.error);
                // Show error in dropdown
                modelDropdownMenu.innerHTML = '<div class="model-dropdown-item disabled"><span class="model-dropdown-item-name">خطا در بارگذاری مدل‌ها</span></div>';
                return;
            }
            
            // Store model data in the select element for later use
            modelSelect.dataset.modelData = JSON.stringify(data.models);
            
            // Clear dropdown menu
            modelDropdownMenu.innerHTML = '';
            
            // Check if there are any models
            if (!data.models || data.models.length === 0) {
                modelDropdownMenu.innerHTML = '<div class="model-dropdown-item disabled"><span class="model-dropdown-item-name">مدلی یافت نشد</span></div>';
                return;
            }
            
            // Sort models: free models first, then premium models
            const sortedModels = [...data.models].sort((a, b) => {
                // Free models come first
                if (a.is_free && !b.is_free) return -1;
                if (!a.is_free && b.is_free) return 1;
                // Then sort by name
                return a.name.localeCompare(b.name);
            });
            
            // Populate model dropdown
            sortedModels.forEach(model => {
                const item = document.createElement('div');
                item.className = 'model-dropdown-item';
                item.dataset.modelId = model.model_id;
                item.dataset.tokenCostMultiplier = model.token_cost_multiplier;
                item.dataset.userHasAccess = model.user_has_access;
                
                // Add disabled class if user doesn't have access
                if (!model.user_has_access) {
                    item.classList.add('disabled');
                }
                
                // Create item content
                let imageHtml = '';
                if (model.image_url) {
                    imageHtml = `<img src="${model.image_url}" alt="${model.name}" class="model-dropdown-item-image" onerror="this.src='/static/images/default-model.PNG'; this.onerror=null;">`;
                } else {
                    // Placeholder for when no image is available
                    imageHtml = `<div class="model-dropdown-item-image" style="background-color: #f8f9fa; border: 1px solid #e9ecef; display: flex; align-items: center; justify-content: center;">
                        <i class="fas fa-microchip" style="color: #6c757d; font-size: 16px;"></i>
                    </div>`;
                }
                
                // Determine badge class
                const badgeClass = model.is_free ? 'badge-free' : 'badge-premium';
                const badgeText = model.is_free ? 'رایگان' : 'ویژه';
                
                item.innerHTML = `
                    ${imageHtml}
                    <div class="model-dropdown-item-content">
                        <span class="model-dropdown-item-name" title="${model.name}">${model.name}</span>
                        <span class="model-dropdown-item-badge ${badgeClass}">${badgeText}</span>
                    </div>
                `;
                
                // Add click event if user has access
                if (model.user_has_access) {
                    item.addEventListener('click', function() {
                        // Update hidden input value
                        modelSelect.value = model.model_id;
                        
                        // Update selected display
                        const selectedImage = this.querySelector('.model-dropdown-item-image').cloneNode(true);
                        selectedImage.className = 'model-dropdown-item-image';
                        selectedImage.style.width = '24px';
                        selectedImage.style.height = '24px';
                        
                        modelDropdownSelected.innerHTML = `
                            ${selectedImage.outerHTML}
                            <span class="model-dropdown-item-name" style="margin: 0 8px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">${model.name}</span>
                            <span class="model-dropdown-item-badge ${badgeClass}" style="font-size: 0.7rem; padding: 0.2em 0.4em;">${badgeText}</span>
                            <i class="fas fa-chevron-down dropdown-arrow"></i>
                        `;
                        
                        // Close dropdown
                        modelDropdownMenu.classList.remove('show');
                        modelDropdownSelected.classList.remove('active');
                        
                        // Rotate arrow back
                        const arrow = modelDropdownSelected.querySelector('.dropdown-arrow');
                        if (arrow) {
                            arrow.classList.remove('rotated');
                        }
                        
                        // Trigger change event for validation
                        const changeEvent = new Event('change');
                        modelSelect.dispatchEvent(changeEvent);
                        
                        // Check if the selected model has a cost multiplier > 1 and show warning
                        const costMultiplier = parseFloat(model.token_cost_multiplier);
                        if (costMultiplier > 1) {
                            showModalCostWarning(costMultiplier);
                        } else {
                            hideModalCostWarning();
                        }
                    });
                }
                
                modelDropdownMenu.appendChild(item);
            });
            
            // Check if there's a default model selected and pre-select it
            const defaultModelId = localStorage.getItem('defaultModelId');
            if (defaultModelId) {
                // Find and select the default model
                const items = modelDropdownMenu.querySelectorAll('.model-dropdown-item:not(.disabled)');
                for (let i = 0; i < items.length; i++) {
                    if (items[i].dataset.modelId === defaultModelId) {
                        items[i].click();
                        break;
                    }
                }
            }
        })
        .catch(error => {
            console.error('Error loading models:', error);
            // Show error in dropdown
            modelDropdownMenu.innerHTML = '<div class="model-dropdown-item disabled"><span class="model-dropdown-item-name">خطا در بارگذاری مدل‌ها</span></div>';
        });
}

// Initialize custom dropdown behavior
document.addEventListener('DOMContentLoaded', function() {
    const modelDropdownSelected = document.getElementById('model-dropdown-selected');
    const modelDropdownMenu = document.getElementById('model-dropdown-menu');
    const modelSelect = document.getElementById('modal-model-select');
    
    if (modelDropdownSelected && modelDropdownMenu) {
        // Toggle dropdown on click
        modelDropdownSelected.addEventListener('click', function(e) {
            e.stopPropagation();
            this.classList.toggle('active');
            modelDropdownMenu.classList.toggle('show');
            
            // Rotate arrow
            const arrow = this.querySelector('.dropdown-arrow');
            if (arrow) {
                arrow.classList.toggle('rotated');
            }
        });
        
        // Close dropdown when clicking outside
        document.addEventListener('click', function(e) {
            if (!modelDropdownSelected.contains(e.target) && !modelDropdownMenu.contains(e.target)) {
                modelDropdownMenu.classList.remove('show');
                modelDropdownSelected.classList.remove('active');
                
                // Rotate arrow back
                const arrow = modelDropdownSelected.querySelector('.dropdown-arrow');
                if (arrow) {
                    arrow.classList.remove('rotated');
                }
            }
        });
    }
});

// Load models for the message input area dropdown
function loadMessageInputModels(chatbotId) {
    // This function is intentionally left empty as we no longer use the model-select dropdown
    // Model selection is now handled through the floating model selection component
}

// Update session model
function updateSessionModel(sessionId, modelId) {
    console.log('Updating session model:', sessionId, modelId);
    // Send request to update the session model
    fetch(`/chat/session/${sessionId}/update-model/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            model_id: modelId
        })
    })
    .then(response => {
        console.log('Model update response status:', response.status);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        console.log('Model update response data:', data);
        if (data.error) {
            console.error('Error updating model:', data.error);
            // Show error message
            alert('خطا در تغییر مدل: ' + data.error);
            return;
        }
        
        // Update local storage with the new model name
        const sessionData = JSON.parse(localStorage.getItem(`session_${sessionId}`) || '{}');
        sessionData.ai_model_name = data.model_name;
        localStorage.setItem(`session_${sessionId}`, JSON.stringify(sessionData));
        
        // Update the model info in existing messages
        updateModelInfoInMessages(sessionId, data.model_name);
        
        console.log('Model updated successfully');
    })
    .catch(error => {
        console.error('Error updating model:', error);
        alert('خطا در تغییر مدل: ' + error.message);
    });
}

// Update model info in existing messages
function updateModelInfoInMessages(sessionId, modelName) {
    // Find all assistant messages and update their model info
    const assistantMessages = document.querySelectorAll('.message-assistant');
    assistantMessages.forEach(message => {
        const modelInfo = message.querySelector('.model-info');
        if (modelInfo) {
            modelInfo.innerHTML = `مدل: ${modelName}`;
        }
    });
}

// Load and display uploaded files for current session
// This function has been removed as per the requirement to show files only in their respective messages
// function loadSessionFiles(sessionId) {
//     // This function is intentionally left empty as we no longer show session files in a separate section
// }



// Function to show cost multiplier warning when changing models
function showModelChangeCostWarning(multiplier) {
    // Check if warning already exists
    let warningElement = document.getElementById('model-change-cost-warning');
    if (!warningElement) {
        warningElement = document.createElement('div');
        warningElement.id = 'model-change-cost-warning';
        warningElement.className = 'alert alert-warning alert-dismissible fade show mt-2';
        warningElement.role = 'alert';
        warningElement.innerHTML = `
            <i class="fas fa-exclamation-triangle"></i>
            <strong>هشدار هزینه!</strong>
            <span id="model-change-warning-text"></span>
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        // Insert after the web search button
        const webSearchBtn = document.getElementById('web-search-btn');
        webSearchBtn.parentNode.insertBefore(warningElement, webSearchBtn.nextSibling);
    }
    
    // Update warning text
    const warningText = document.getElementById('model-change-warning-text');
    warningText.textContent = ` این مدل هوش مصنوعی دارای ضریب هزینه ${multiplier} است و به ازای هر توکن مصرفی، ${multiplier} توکن از اعتبار شما کسر خواهد شد.`;
    
    // Make sure it's visible
    warningElement.style.display = 'block';
    
    // Auto hide after 5 seconds
    setTimeout(() => {
        if (warningElement) {
            warningElement.style.display = 'none';
        }
    }, 5000);
}

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
