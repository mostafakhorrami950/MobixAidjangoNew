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
    
    // Clear current options
    modelSelect.innerHTML = '<option value="">-- مدلی را انتخاب کنید --</option>';
    
    // Load models for this chatbot
    fetch(`/chat/chatbot/${chatbotId}/models/`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error('Error loading models:', data.error);
                return;
            }
            
            // Populate model select
            data.models.forEach(model => {
                const option = document.createElement('option');
                option.value = model.model_id;
                option.textContent = model.name;
                option.dataset.isFree = model.is_free;
                
                // Add badge for free/premium models
                if (model.is_free) {
                    option.innerHTML += ' <span class="badge bg-success">رایگان</span>';
                } else {
                    option.innerHTML += ' <span class="badge bg-warning">ویژه</span>';
                }
                
                modelSelect.appendChild(option);
            });
            
            // Show/hide image generation button based on chatbot type
            const imageGenBtn = document.getElementById('image-generation-btn');
            const webSearchBtn = document.getElementById('web-search-btn');
            if (data.chatbot_type === 'image_editing') {
                // For image editing chatbots:
                // 1. Hide the image generation button (it's automatic)
                imageGenBtn.style.display = 'none';
                // 2. Enable image generation by default
                sessionStorage.setItem(`imageGen_${currentSessionId}`, 'true');
                // 3. Hide the web search button
                webSearchBtn.style.display = 'none';
            } else {
                // For other chatbots:
                // 1. Show the image generation button
                imageGenBtn.style.display = 'inline-block';
                // 2. Restore web search button visibility
                webSearchBtn.style.display = 'inline-block';
                // Also disable image generation if it was enabled
                imageGenBtn.classList.remove('btn-primary');
                imageGenBtn.classList.add('btn-outline-primary');
                imageGenBtn.innerHTML = '<i class="fas fa-image"></i> تولید تصویر';
                imageGenBtn.title = 'فعال کردن تولید تصویر';
                sessionStorage.setItem(`imageGen_${currentSessionId}`, 'false');
            }
        })
        .catch(error => console.error('Error loading models:', error));
}

// Load models for the message input area dropdown
function loadMessageInputModels(chatbotId) {
    const modelSelect = document.getElementById('model-select');
    
    // Clear current options
    modelSelect.innerHTML = '<option value="">انتخاب مدل...</option>';
    
    // Load models for this chatbot
    fetch(`/chat/chatbot/${chatbotId}/models/`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error('Error loading models:', data.error);
                return;
            }
            
            // Get current session data to determine the current model
            let currentModelId = null;
            if (currentSessionId) {
                const sessionData = JSON.parse(localStorage.getItem(`session_${currentSessionId}`) || '{}');
                // Find the model ID based on the model name
                const models = data.models;
                for (let i = 0; i < models.length; i++) {
                    if (models[i].name === sessionData.ai_model_name) {
                        currentModelId = models[i].model_id;
                        break;
                    }
                }
            }
            
            // Populate model select
            data.models.forEach(model => {
                const option = document.createElement('option');
                option.value = model.model_id;
                option.textContent = model.name;
                
                // Set as selected if this is the current model
                if (model.model_id === currentModelId) {
                    option.selected = true;
                }
                
                // Add badge for free/premium models
                if (model.is_free) {
                    option.innerHTML += ' <span class="badge badge-free">رایگان</span>';
                } else {
                    option.innerHTML += ' <span class="badge badge-premium">ویژه</span>';
                }
                
                modelSelect.appendChild(option);
            });
            
            // Show the model selection dropdown
            modelSelect.style.display = 'inline-block';
        })
        .catch(error => console.error('Error loading models:', error));
}

// Update session model
function updateSessionModel(sessionId, modelId) {
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
    .then(response => response.json())
    .then(data => {
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