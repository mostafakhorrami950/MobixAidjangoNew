// =================================
// مدیریت جلسات چت (Sessions Management)
// =================================

// Load user sessions
function loadSessions() {
    fetch(CHAT_URLS.getUserSessions)
        .then(response => response.json())
        .then(data => {
            const sessionsList = document.getElementById('sessions-list');
            if (!sessionsList) {
                console.warn('Sessions list element not found');
                return;
            }
            
            sessionsList.innerHTML = '';
            
            if (data.sessions.length === 0) {
                sessionsList.innerHTML = '<div class="list-group-item text-center text-muted">چتی وجود ندارد</div>';
                return;
            }
            
            data.sessions.forEach(session => {
                const sessionElement = document.createElement('div');
                sessionElement.className = 'list-group-item session-item';
                if (session.id == currentSessionId) {
                    sessionElement.classList.add('active');
                }
                sessionElement.innerHTML = `
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <strong>${session.title}</strong>
                            <div class="small text-muted">
                                ${session.session_name} 
                                <span class="model-access ${session.model_access.toLowerCase()}">
                                    ${session.model_access === 'Free' ? 'رایگان' : 'ویژه'}
                                </span>
                            </div>
                        </div>
                        <div class="text-muted small">${new Date(session.updated_at).toLocaleTimeString('fa-IR')}</div>
                    </div>
                `;
                sessionElement.addEventListener('click', () => loadSession(session.id));
                sessionsList.appendChild(sessionElement);
            });
        })
        .catch(error => console.error('Error loading sessions:', error));
}

// Load a specific session
function loadSession(sessionId) {
    currentSessionId = sessionId;
    loadSessions(); // Update active state

    // Update URL to reflect the current session
    const newUrl = `/chat/session/${sessionId}/`;

    history.pushState({sessionId: sessionId}, '', newUrl);
    
    fetch(`/chat/session/${sessionId}/messages/`)
        .then(response => response.json())
        .then(data => {
            const currentSessionTitle = document.getElementById('current-session-title');
            if (currentSessionTitle) {
                currentSessionTitle.innerHTML = `
                    <i class="fas fa-comments"></i> ${data.session_title}
                `;
            }
            
            const deleteSessionBtn = document.getElementById('delete-session-btn');
            if (deleteSessionBtn) {
                deleteSessionBtn.style.display = 'inline-block';
            }
            
            // Check if user has access to web search functionality
            checkWebSearchAccess(sessionId);
            
            // Check if user has access to image generation functionality
            checkImageGenerationAccess(sessionId);
            
            // Store session data including AI model name
            const sessionData = {
                ai_model_name: data.ai_model_name,
                session_name: data.session_name,
                chatbot_type: data.chatbot_type,
                chatbot_id: data.chatbot_id
            };
            localStorage.setItem(`session_${sessionId}`, JSON.stringify(sessionData));
            
            // Update the model selection button to show the current model name
            const currentModelName = document.getElementById('current-model-name');
            if (currentModelName && data.ai_model_name) {
                currentModelName.textContent = data.ai_model_name;
            }
            
            const chatContainer = document.getElementById('chat-container');
            if (chatContainer) {
                chatContainer.innerHTML = '';
                
                if (data.messages.length === 0) {
                    chatContainer.innerHTML = `
                        <div class="text-center text-muted">
                            <i class="fas fa-comment-slash"></i> هنوز پیامی وجود ندارد. مکالمه را شروع کنید!
                        </div>
                    `;
                } else {
                    data.messages.forEach(message => {
                        addMessageToChat(message);
                    });
                }
            }
            
            // Enable input fields
            const messageInput = document.getElementById('message-input');
            if (messageInput) {
                messageInput.disabled = false;
            }
            
            const sendButton = document.getElementById('send-button');
            if (sendButton) {
                sendButton.disabled = false;
            }
            
            // Load models for the message input area
            if (data.chatbot_id) {
                loadMessageInputModels(data.chatbot_id);
            }
            
            // Scroll to bottom with enhanced reliability
            scrollToBottom();
            
            // Focus on input
            if (messageInput) {
                messageInput.focus();
            }
            
            // Hide sidebar on mobile after selecting a session
            if (window.innerWidth < 768) {
                const sidebar = document.getElementById('sidebar');
                if (sidebar) {
                    sidebar.classList.remove('show');
                }
                const sidebarOverlay = document.getElementById('sidebar-overlay');
                if (sidebarOverlay) {
                    sidebarOverlay.classList.remove('show');
                }
            }
        })
        .catch(error => console.error('Error loading session:', error));
}

// Add a function to check if we're on a specific session page
function checkInitialSession() {
    // Check if we're on a session page (URL contains /chat/session/<id>/)
    const pathParts = window.location.pathname.split('/');
    if (pathParts.length >= 4 && pathParts[1] === 'chat' && pathParts[2] === 'session') {
        const sessionId = parseInt(pathParts[3]);
        if (sessionId) {
            loadSession(sessionId);
            
            // Check if there's a pending message to send after session creation
            const pendingMessage = sessionStorage.getItem('pendingMessage');
            const pendingFiles = sessionStorage.getItem('pendingFiles');
            
            if (pendingMessage || pendingFiles) {
                // Clear the session storage
                sessionStorage.removeItem('pendingMessage');
                sessionStorage.removeItem('pendingFiles');
                
                // Send the pending message after a short delay to ensure UI is ready
                setTimeout(() => {
                    const messageInput = document.getElementById('message-input');
                    if (messageInput) {
                        // Set the message content
                        if (pendingMessage) {
                            messageInput.value = pendingMessage;
                        }
                        
                        // Trigger the send button click
                        const sendButton = document.getElementById('send-button');
                        if (sendButton) {
                            sendButton.click();
                        }
                    }
                }, 1000);
            }
        }
    }
}

// Create new chat
async function createNewChat() {
    const chatbotContainer = document.getElementById('modal-chatbot-select');
    const modelContainer = document.getElementById('modal-model-select');
    
    const chatbotId = chatbotContainer.dataset.selected;
    const modelId = modelContainer.dataset.selected;
    
    // Validate selections
    if (!chatbotId || !modelId) {
        alert('لطفاً هم یک چت‌بات و هم یک مدل هوش مصنوعی انتخاب کنید');
        return;
    }
    
    // Use default title
    const title = 'چت جدید';
    
    fetch(CHAT_URLS.createSession, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            title: title,
            chatbot_id: chatbotId,
            ai_model_id: modelId
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert('خطا: ' + data.error);
            return;
        }
        
        // Close modal
        bootstrap.Modal.getInstance(document.getElementById('newChatModal')).hide();
        
        // Load the new session
        loadSession(data.session_id);
        
        // Update the model selection button with the selected model name
        const modelSelect = document.getElementById('modal-model-select');
        if (modelSelect && modelSelect.options && modelSelect.options[modelSelect.selectedIndex]) {
            const selectedModelName = modelSelect.options[modelSelect.selectedIndex].text;
            const currentModelName = document.getElementById('current-model-name');
            if (currentModelName) {
                // Remove any badge text from the model name
                const cleanModelName = selectedModelName.replace(/\s*<span[^>]*>[\s\S]*?<\/span>\s*/gi, '').trim();
                currentModelName.textContent = cleanModelName;
                // Also update the global variable
                currentSelectedModel = modelSelect.value;
            }
        }
        
        // Initialize web search button for the new session
        const webSearchBtn = document.getElementById('web-search-btn');
        if (webSearchBtn) {
            // Reset to default state
            webSearchBtn.classList.remove('btn-success');
            webSearchBtn.classList.add('btn-outline-secondary');
            webSearchBtn.innerHTML = '<i class="fas fa-search"></i> جستجو وب';
            webSearchBtn.title = 'فعال کردن جستجو وب';
            webSearchBtn.disabled = false;
            // Clear any previous session storage
            sessionStorage.removeItem(`webSearch_${data.session_id}`);
        }
        
        // Refresh sessions list
        loadSessions();
    })
    .catch(error => {
        console.error('Error creating chat:', error);
        alert('خطا در ایجاد چت: ' + error.message);
    });
}

// Add event listener for create chat button
document.getElementById('create-chat-btn').addEventListener('click', function() {
    // Validate model selection
    const modelContainer = document.getElementById('modal-model-select');
    if (!modelContainer.dataset.selected) {
        showConfirmationMessage('لطفاً مدل را انتخاب کنید.', 'warning');
        return;
    }
    
    createNewChat();
});

// Delete session
function deleteSession() {
    if (!currentSessionId) return;
    
    if (confirm('آیا مطمئن هستید که می‌خواهید این جلسه چت را حذف کنید؟')) {
        // Send DELETE request to remove the session
        fetch(`/chat/session/${currentSessionId}/delete/`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(response => {
            if (response.ok) {
                // Reset UI
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
                
                loadSessions();
                
                // Hide sidebar on mobile
                if (window.innerWidth < 768) {
                    const sidebar = document.getElementById('sidebar');
                    if (sidebar) {
                        sidebar.classList.remove('show');
                    }
                    const sidebarOverlay = document.getElementById('sidebar-overlay');
                    if (sidebarOverlay) {
                        sidebarOverlay.classList.remove('show');
                    }
                }
            } else {
                alert('خطا در حذف چت');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('خطا در حذف چت');
        });
    }
}