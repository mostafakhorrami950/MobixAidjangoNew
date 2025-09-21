// =================================
// مدیریت جلسات چت (Chat Session Management)
// =================================

let currentSessionId = null;

// Load user's chat sessions
function loadSessions() {
    fetch(CHAT_URLS.getUserSessions)
        .then(response => response.json())
        .then(data => {
            const sessionsList = document.getElementById('sessions-list');
            if (!sessionsList) return;
            
            sessionsList.innerHTML = '';
            
            if (data.sessions && data.sessions.length > 0) {
                data.sessions.forEach(session => {
                    const sessionElement = createSessionElement(session);
                    sessionsList.appendChild(sessionElement);
                });
            } else {
                sessionsList.innerHTML = `
                    <div class="text-center text-muted p-3">
                        <i class="fas fa-comment-slash fa-2x mb-2"></i>
                        <p class="mb-0">هنوز چتی ایجاد نکرده‌اید</p>
                    </div>
                `;
            }
        })
        .catch(error => console.error('Error loading sessions:', error));
}

// Create session element for the sidebar
function createSessionElement(session) {
    const sessionElement = document.createElement('div');
    sessionElement.className = 'session-item';
    sessionElement.dataset.sessionId = session.id;
    
    // Format the update time
    const updateTime = new Date(session.updated_at);
    const timeString = updateTime.toLocaleTimeString('fa-IR', { 
        hour: '2-digit', 
        minute: '2-digit' 
    });
    const dateString = updateTime.toLocaleDateString('fa-IR');
    
    sessionElement.innerHTML = `
        <div class="flex-grow-1">
            <strong>${session.title || 'چت بدون عنوان'}</strong>
            <div class="small d-flex justify-content-between">
                <span>${session.session_name}</span>
                <span class="model-access ${session.model_access.toLowerCase()}">
                    ${session.model_access === 'Free' ? 'رایگان' : 'ویژه'}
                </span>
            </div>
            <div class="small text-muted d-flex justify-content-between">
                <span>${timeString}</span>
                <span>${dateString}</span>
            </div>
        </div>
    `;
    
    sessionElement.addEventListener('click', () => {
        loadSession(session.id);
        // Update URL without page reload
        history.pushState({sessionId: session.id}, '', `/chat/session/${session.id}/`);
        
        // Close sidebar on mobile after selecting a session
        if (window.innerWidth < 768) {
            toggleSidebar();
        }
    });
    
    return sessionElement;
}

// Load a specific chat session
function loadSession(sessionId) {
    // Remove active class from all session items
    document.querySelectorAll('.session-item').forEach(item => {
        item.classList.remove('active');
    });
    
    // Add active class to selected session
    const selectedSession = document.querySelector(`.session-item[data-session-id="${sessionId}"]`);
    if (selectedSession) {
        selectedSession.classList.add('active');
    }
    
    // Set current session ID
    currentSessionId = sessionId;
    
    // Fetch session messages
    fetch(`/chat/session/${sessionId}/messages/`)
        .then(response => response.json())
        .then(data => {
            const chatContainer = document.getElementById('chat-container');
            const currentSessionTitle = document.getElementById('current-session-title');
            const messageInput = document.getElementById('message-input');
            const sendButton = document.getElementById('send-button');
            const deleteSessionBtn = document.getElementById('delete-session-btn');
            const modelSelect = document.getElementById('model-select');
            const webSearchBtn = document.getElementById('web-search-btn');
            const imageGenerationBtn = document.getElementById('image-generation-btn');
            
            if (!chatContainer || !currentSessionTitle) return;
            
            // Update session title
            currentSessionTitle.innerHTML = `
                <i class="fas fa-comments"></i> ${data.session_title || 'چت بدون عنوان'}
            `;
            
            // Clear chat container
            chatContainer.innerHTML = '';
            
            // Add messages
            if (data.messages && data.messages.length > 0) {
                data.messages.forEach(message => {
                    if (!message.disabled) { // Only show non-disabled messages
                        const messageElement = createMessageElement(message);
                        chatContainer.appendChild(messageElement);
                    }
                });
                
                // Scroll to bottom
                chatContainer.scrollTop = chatContainer.scrollHeight;
            } else {
                chatContainer.innerHTML = `
                    <div class="text-center text-muted welcome-message">
                        <i class="fas fa-robot fa-3x mb-3"></i>
                        <h4>به چت‌بات MobixAI خوش آمدید</h4>
                        <p class="mb-0">پیام خود را شروع کنید</p>
                    </div>
                `;
            }
            
            // Enable input fields
            if (messageInput) messageInput.disabled = false;
            if (sendButton) sendButton.disabled = false;
            if (deleteSessionBtn) deleteSessionBtn.style.display = 'inline-block';
            
            // Show model selection if available
            if (modelSelect && data.ai_model_name) {
                modelSelect.style.display = 'inline-block';
                // Update model selection with session model
                updateModelSelectionOptions(data.ai_model_name);
            }
            
            // Check web search access
            checkWebSearchAccess(sessionId, webSearchBtn);
            
            // Check image generation access
            checkImageGenerationAccess(sessionId, imageGenerationBtn);
            
            // Add edit buttons to user messages
            setTimeout(addEditButtonToUserMessages, 1000);
        })
        .catch(error => console.error('Error loading session:', error));
}

// Create message element
function createMessageElement(message) {
    const messageElement = document.createElement('div');
    messageElement.className = `message-${message.type}`;
    messageElement.dataset.messageId = message.id;
    messageElement.dataset.dbId = message.db_id;
    
    // Format timestamp
    const timestamp = new Date(message.created_at);
    const timeString = timestamp.toLocaleTimeString('fa-IR', { 
        hour: '2-digit', 
        minute: '2-digit' 
    });
    
    // Process content with markdown
    let processedContent = message.content || '';
    
    // Handle image URLs if present
    let imageHtml = '';
    if (message.image_url) {
        const imageUrls = message.image_url.split(',');
        imageHtml = imageUrls.map(url => `
            <div class="message-image mt-2">
                <img src="${url.trim()}" alt="تصویر تولید شده" class="img-fluid rounded" style="max-width: 100%; height: auto;">
            </div>
        `).join('');
    }
    
    // Handle uploaded files if present
    let filesHtml = '';
    if (message.uploaded_files && message.uploaded_files.length > 0) {
        filesHtml = `
            <div class="files-container mt-2 p-2 bg-light rounded">
                <div class="uploaded-files-header d-flex justify-content-between align-items-center">
                    <small class="fw-bold text-muted">
                        <i class="fas fa-paperclip"></i> فایل‌های پیوست شده
                    </small>
                </div>
                ${message.uploaded_files.map(file => `
                    <div class="uploaded-file-item d-flex justify-content-between align-items-center p-2 mt-1 rounded bg-white border">
                        <div>
                            <span class="fw-semibold text-primary">${file.filename}</span>
                            <small class="text-muted d-block">${formatFileSize(file.size)}</small>
                        </div>
                        <div class="file-actions">
                            <a href="${file.download_url}" class="btn btn-sm btn-outline-primary" download>
                                <i class="fas fa-download"></i>
                            </a>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    }
    
    messageElement.innerHTML = `
        <div class="message-header">
            <strong>${message.type === 'user' ? 'شما' : (message.session_name || 'چت‌بات')}</strong>
            <small>${timeString}</small>
        </div>
        <div class="message-content">
            ${processedContent}
        </div>
        ${imageHtml}
        ${filesHtml}
        <div class="message-actions">
            <!-- Edit button will be added dynamically for user messages -->
        </div>
    `;
    
    return messageElement;
}

// Update model selection options
function updateModelSelectionOptions(currentModelName) {
    const modelSelect = document.getElementById('model-select');
    if (!modelSelect) return;
    
    // Fetch available models
    fetch('/chat/models/')
        .then(response => response.json())
        .then(data => {
            // Clear current options
            modelSelect.innerHTML = '<option value="">انتخاب مدل...</option>';
            
            // Add available models
            data.models.forEach(model => {
                if (model.user_has_access) {
                    const option = document.createElement('option');
                    option.value = model.model_id;
                    option.textContent = model.name;
                    if (model.name === currentModelName) {
                        option.selected = true;
                    }
                    modelSelect.appendChild(option);
                }
            });
        })
        .catch(error => console.error('Error loading models:', error));
}

// Check web search access for session
function checkWebSearchAccess(sessionId, webSearchBtn) {
    if (!webSearchBtn) return;
    
    fetch(`/chat/session/${sessionId}/web-search-access/`)
        .then(response => response.json())
        .then(data => {
            if (data.has_access) {
                webSearchBtn.style.display = 'inline-block';
            } else {
                webSearchBtn.style.display = 'none';
            }
        })
        .catch(error => {
            console.error('Error checking web search access:', error);
            webSearchBtn.style.display = 'none';
        });
}

// Check image generation access for session
function checkImageGenerationAccess(sessionId, imageGenerationBtn) {
    if (!imageGenerationBtn) return;
    
    fetch(`/chat/session/${sessionId}/image-generation-access/`)
        .then(response => response.json())
        .then(data => {
            if (data.has_access) {
                imageGenerationBtn.style.display = 'inline-block';
            } else {
                imageGenerationBtn.style.display = 'none';
            }
        })
        .catch(error => {
            console.error('Error checking image generation access:', error);
            imageGenerationBtn.style.display = 'none';
        });
}

// Create new chat session
function createNewChat() {
    const chatbotSelect = document.getElementById('modal-chatbot-select');
    const modelSelect = document.getElementById('modal-model-select');
    
    const chatbotId = chatbotSelect.value;
    const modelId = modelSelect.value;
    
    if (!chatbotId) {
        alert('لطفاً یک چت‌بات انتخاب کنید');
        return;
    }
    
    if (!modelId) {
        alert('لطفاً یک مدل انتخاب کنید');
        return;
    }
    
    // Close modal
    const modal = bootstrap.Modal.getInstance(document.getElementById('newChatModal'));
    modal.hide();
    
    // Create session
    fetch(CHAT_URLS.createSession, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            chatbot_id: chatbotId,
            ai_model_id: modelId,
            title: 'چت جدید'
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert(data.error);
            return;
        }
        
        // Reload sessions list
        loadSessions();
        
        // Load the new session
        loadSession(data.session_id);
        
        // Update URL without page reload
        history.pushState({sessionId: data.session_id}, '', `/chat/session/${data.session_id}/`);
    })
    .catch(error => {
        console.error('Error creating session:', error);
        alert('خطا در ایجاد جلسه');
    });
}

// Delete current session
function deleteSession() {
    if (!currentSessionId) return;
    
    if (!confirm('آیا مطمئن هستید که می‌خواهید این چت را حذف کنید؟')) {
        return;
    }
    
    fetch(`/chat/session/${currentSessionId}/delete/`, {
        method: 'DELETE',
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Reset UI
            const chatContainer = document.getElementById('chat-container');
            const currentSessionTitle = document.getElementById('current-session-title');
            const messageInput = document.getElementById('message-input');
            const sendButton = document.getElementById('send-button');
            const deleteSessionBtn = document.getElementById('delete-session-btn');
            const modelSelect = document.getElementById('model-select');
            const webSearchBtn = document.getElementById('web-search-btn');
            const imageGenerationBtn = document.getElementById('image-generation-btn');
            
            if (chatContainer) {
                chatContainer.innerHTML = `
                    <div class="text-center text-muted welcome-message">
                        <i class="fas fa-robot fa-3x mb-3"></i>
                        <h4>به چت‌بات MobixAI خوش آمدید</h4>
                        <p class="mb-0">چتی را انتخاب کنید یا جدیدی ایجاد کنید</p>
                    </div>
                `;
            }
            
            if (currentSessionTitle) {
                currentSessionTitle.innerHTML = '<i class="fas fa-comments"></i> چت را انتخاب کنید یا جدیدی ایجاد کنید';
            }
            
            if (messageInput) messageInput.disabled = true;
            if (sendButton) sendButton.disabled = true;
            if (deleteSessionBtn) deleteSessionBtn.style.display = 'none';
            if (modelSelect) modelSelect.style.display = 'none';
            if (webSearchBtn) webSearchBtn.style.display = 'none';
            if (imageGenerationBtn) imageGenerationBtn.style.display = 'none';
            
            // Reset current session ID
            currentSessionId = null;
            
            // Reload sessions list
            loadSessions();
            
            // Update URL to base chat page
            history.pushState({}, '', '/chat/');
        } else {
            alert('خطا در حذف چت');
        }
    })
    .catch(error => {
        console.error('Error deleting session:', error);
        alert('خطا در حذف چت');
    });
}

// Load models for a specific chatbot
function loadModelsForChatbot(chatbotId) {
    const modelSelect = document.getElementById('modal-model-select');
    if (!modelSelect) return;
    
    // Show loading state
    modelSelect.innerHTML = '<option value="">در حال بارگذاری...</option>';
    modelSelect.disabled = true;
    
    fetch(`/chat/chatbot/${chatbotId}/models/`)
        .then(response => response.json())
        .then(data => {
            // Clear current options
            modelSelect.innerHTML = '<option value="">انتخاب مدل...</option>';
            modelSelect.disabled = false;
            
            // Add models
            if (data.models && data.models.length > 0) {
                data.models.forEach(model => {
                    if (model.user_has_access) {
                        const option = document.createElement('option');
                        option.value = model.model_id;
                        option.textContent = model.name;
                        option.dataset.tokenCostMultiplier = model.token_cost_multiplier || 1.0;
                        
                        // Add badge for free/premium models
                        if (model.is_free) {
                            option.innerHTML = `${model.name} <span class="badge bg-success ms-2">رایگان</span>`;
                        } else {
                            option.innerHTML = `${model.name} <span class="badge bg-warning ms-2">ویژه</span>`;
                        }
                        
                        modelSelect.appendChild(option);
                    }
                });
            } else {
                const option = document.createElement('option');
                option.value = '';
                option.textContent = 'هیچ مدلی در دسترس نیست';
                option.disabled = true;
                modelSelect.appendChild(option);
            }
            
            // Check selections
            checkModalSelections();
        })
        .catch(error => {
            console.error('Error loading models:', error);
            modelSelect.innerHTML = '<option value="">خطا در بارگذاری مدل‌ها</option>';
            modelSelect.disabled = false;
        });
}

// Update session model
function updateSessionModel(sessionId, modelId) {
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
        }
    })
    .catch(error => {
        console.error('Error updating model:', error);
    });
}

// Helper function to get CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Helper function to format file size
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Check if we should load a specific session on page load
function checkInitialSession() {
    // Check if we're on a specific session URL
    const pathParts = window.location.pathname.split('/');
    if (pathParts.length >= 4 && pathParts[2] === 'session') {
        const sessionId = parseInt(pathParts[3]);
        if (sessionId) {
            loadSession(sessionId);
        }
    }
}