// =================================
// ارسال پیام‌ها و streaming (Message Sending & Streaming)
// =================================



// Send message with streaming support
function sendMessage() {
    console.log('sendMessage called');
    const messageInput = document.getElementById('message-input');
    const message = messageInput.value.trim();
    
    // دریافت فایل‌ها از مدیر آپلود چند فایل
    // Get files from multiple file upload manager
    let files = [];
    try {
        files = getSelectedFiles();
        console.log('Files retrieved:', files);
    } catch (error) {
        console.error('Error getting selected files:', error);
        files = [];
    }

    if (!message && !files.length) {
        console.log('No message and no files, returning');
        return;
    }
    
    // بررسی وجود currentSessionId و ایجاد session پیش‌فرض در صورت نیاز
    if (!currentSessionId) {
        // ایجاد session پیش‌فرض
        createDefaultSessionAndSendMessage(message, files);
        return;
    }

    // Prepare display message
    let displayMessage = message;
    if (files.length > 0) {
        const fileNames = files.map(f => f.name).join(', ');
        displayMessage += ` (فایل‌ها: ${fileNames})`;
    }

    // Add user message to chat immediately
    // Note: We'll replace this temporary message with the one from the server later
    const tempUserMessage = {
        type: 'user',
        content: displayMessage,
        created_at: new Date().toISOString()
    };
    console.log('Adding temporary user message:', tempUserMessage);
    addMessageToChat(tempUserMessage);

    // Clear inputs
    messageInput.value = '';
    resetFilesState(); // Clear all selected files

    // Disable input while processing
    messageInput.disabled = true;

    // Show typing indicator
    showTypingIndicator();

    // Title will be auto-generated on server-side after first message

    const isWebSearchEnabled = sessionStorage.getItem(`webSearch_${currentSessionId}`) === 'true';
    const isImageGenerationEnabled = sessionStorage.getItem(`imageGen_${currentSessionId}`) === 'true';

    // ALWAYS use FormData to send the request
    const formData = new FormData();
    formData.append('message', message);
    formData.append('use_web_search', isWebSearchEnabled);
    formData.append('generate_image', isImageGenerationEnabled);
    // اضافه کردن چندین فایل
    files.forEach(file => {
        formData.append('files', file); // تغییر از 'file' به 'files'
    });

    // Use the new endpoint for long polling approach
    fetch(`/chat/session/${currentSessionId}/send_full/`, {
        method: 'POST',
        headers: {
            // 'Content-Type' is automatically set to 'multipart/form-data' by the browser when using FormData
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: formData
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(data => {
                throw new Error(data.error || 'Error sending message');
            });
        }
        return response.json();
    })
    .then(data => {
        // Hide typing indicator
        hideTypingIndicator();
        
        if (data.success) {
            // Update the temporary user message with the real data from server
            if (data.user_message_data) {
                updateUserMessageWithServerData(data.user_message_data);
            }
            
            // Display the assistant response with typing effect
            displayTextGradually(data.content);
        } else {
            // Handle error
            addMessageToChat({
                type: 'assistant',
                content: `خطا: ${data.error || 'خطای نامشخص'}`,
                created_at: new Date().toISOString()
            });
        }
        
        // Re-enable input and reset button state
        messageInput.disabled = false;
        messageInput.focus();
    })
    .catch(error => {
        // Hide typing indicator
        hideTypingIndicator();
        
        // Handle error
        addMessageToChat({
            type: 'assistant',
            content: `خطا: ${error.message || 'خطای نامشخص'}`,
            created_at: new Date().toISOString()
        });
        
        // Re-enable input and reset button state
        messageInput.disabled = false;
        messageInput.focus();
    });
}

// Function to update title in UI after auto-generation
function updateSessionTitleInUI(newTitle) {
    try {
        // Update current session title display
        const titleElement = document.getElementById('current-session-title');
        if (titleElement) {
            titleElement.innerHTML = `<i class="fas fa-comments"></i> ${newTitle}`;
        }
        
        // Refresh sessions list to show new title
        loadSessions();
        
        console.log('Session title updated in UI:', newTitle);
    } catch (error) {
        console.error('Error updating session title in UI:', error);
    }
}





// Generate chat title using AI
function generateChatTitle(firstMessage, chatbotId, modelId) {
    const data = {
        first_message: firstMessage
    };
    
    // Add either chatbot_id or model_id based on what's provided
    if (chatbotId) {
        data.chatbot_id = chatbotId;
    } else if (modelId) {
        data.model_id = modelId;
    }
    
    return fetch(CHAT_URLS.generateChatTitle, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => data.title || 'چت جدید');
}

// تابع برای تغییر وضعیت دکمه
function setButtonState(isSending) {
    const sendButton = document.getElementById('send-button');
    const sendIcon = sendButton.querySelector('.send-icon');
    const stopIcon = sendButton.querySelector('.stop-icon');

    if (isSending) {
        sendIcon.style.display = 'none';
        stopIcon.style.display = 'inline-block';
        sendButton.classList.add('btn-danger'); // تغییر رنگ به قرمز
        sendButton.disabled = false; // فعال کردن دکمه در حالت توقف
        sendButton.onclick = function(event) {
            event.preventDefault();
            abortController.abort(); // لغو درخواست در صورت کلیک
        };
    } else {
        sendIcon.style.display = 'inline-block';
        stopIcon.style.display = 'none';
        sendButton.classList.remove('btn-danger');
        sendButton.disabled = false; // همیشه دکمه را فعال نگه دار
        sendButton.onclick = null; // حذف رویداد کلیک قبلی
    }
}

// رویداد ترک صفحه
window.addEventListener('beforeunload', function() {
    // اگر درخواستی در حال پردازش است، آن را لغو کن
    if (abortController && !abortController.signal.aborted) {
        abortController.abort();
    }
});

/**
 * ایجاد جلسه پیش‌فرض و ارسال پیام
 * Create default session and send message
 */
async function createDefaultSessionAndSendMessage(message, files) {
    try {
        // نمایش پیام انتظار
        showTypingIndicator();
        
        // Prepare data for creating session
        const sessionCreateData = {};
        
        // If a model is selected for new session, use it
        if (selectedModelForNewSession) {
            sessionCreateData.ai_model_id = selectedModelForNewSession;
        }
        
        // ایجاد جلسه پیش‌فرض
        const response = await fetch(CHAT_URLS.createDefaultSession, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify(sessionCreateData)
        });
        
        const data = await response.json();
        
        if (data.error) {
            hideTypingIndicator();
            alert('خطا در ایجاد چت جدید: ' + data.error);
            return;
        }
        
        // تنظیم session ID جدید
        currentSessionId = data.session_id;
        
        // Redirect to the new session URL
        const newUrl = `/chat/session/${currentSessionId}/`;
        history.pushState({sessionId: currentSessionId}, '', newUrl);
        
        // بروزرسانی UI
        document.getElementById('current-session-title').innerHTML = `
            <i class="fas fa-comments"></i> ${data.title}
        `;
        document.getElementById('delete-session-btn').style.display = 'inline-block';
        
        // فعال کردن input ها
        const messageInput = document.getElementById('message-input');
        messageInput.disabled = false;
        document.getElementById('send-button').disabled = false;
        
        // Store session data in localStorage (important for auto-refresh functionality)
        const sessionData = {
            ai_model_name: data.ai_model_name || 'مدل پیش‌فرض',
            session_name: data.title,
            chatbot_type: data.chatbot_type,
            chatbot_id: data.chatbot_id
        };
        localStorage.setItem(`session_${currentSessionId}`, JSON.stringify(sessionData));
        console.log('Stored session data for auto-refresh:', sessionData);
        
        // Load models for the message input area
        if (data.chatbot_id) {
            loadMessageInputModels(data.chatbot_id);
        }
        
        // Check web search and image generation access
        checkWebSearchAccess(currentSessionId);
        checkImageGenerationAccess(currentSessionId);
        
        // Set web search state if it was enabled for new session
        if (isWebSearchEnabledForNewSession) {
            sessionStorage.setItem(`webSearch_${currentSessionId}`, 'true');
            // Update the web search button UI
            const webSearchBtn = document.getElementById('web-search-btn');
            if (webSearchBtn) {
                webSearchBtn.classList.remove('btn-outline-secondary');
                webSearchBtn.classList.add('btn-success');
                webSearchBtn.innerHTML = '<i class="fas fa-search"></i> جستجو وب فعال';
                webSearchBtn.title = 'غیرفعال کردن جستجو وب';
            }
        }
        
        // بروزرسانی لیست sessions
        loadSessions();
        
        // مخفی کردن welcome message
        const welcomeMessage = document.getElementById('welcome-message');
        if (welcomeMessage) {
            welcomeMessage.style.display = 'none';
        }
        
        hideTypingIndicator();
        
        // حالا پیام را ارسال کنیم
        // Re-enable input before sending message
        messageInput.disabled = false;
        // Use the improved sendMessage function
        sendMessage();
        
    } catch (error) {
        hideTypingIndicator();
        console.error('Error creating default session:', error);
        alert('خطا در ایجاد چت جدید: ' + error.message);
    }
}

// sendMessageInternal function has been removed as it contained problematic streaming logic
// We now use the improved sendMessage function exclusively

// Function to update the temporary user message with real data from server
function updateUserMessageWithServerData(userData) {
    console.log('Updating user message with server data:', userData);
    
    // Find the last user message element (which should be our temporary one)
    const userMessages = document.querySelectorAll('.message-user');
    if (userMessages.length > 0) {
        const lastUserMessage = userMessages[userMessages.length - 1];
        
        // Check if this message already has an ID and uploaded files data
        if (lastUserMessage.dataset.messageId && lastUserMessage.querySelector('.files-container')) {
            console.log('Last user message already has an ID and files:', lastUserMessage.dataset.messageId);
            // If it already has an ID, make sure it matches the server ID
            if (userData.id && lastUserMessage.dataset.messageId !== userData.id) {
                console.warn('Message ID mismatch. Expected:', userData.id, 'Actual:', lastUserMessage.dataset.messageId);
                // Update the ID to match the server
                lastUserMessage.dataset.messageId = userData.id;
            }
            return;
        }
        
        // Update the message ID data attribute for editing functionality
        if (userData.id) {
            lastUserMessage.dataset.messageId = userData.id;
            console.log('Updated user message with server ID:', userData.id);
        }
        
        // Add uploaded files display if files are present in server data
        if (userData.uploaded_files && userData.uploaded_files.length > 0) {
            console.log('Adding uploaded files to user message:', userData.uploaded_files);
            
            // Check if files container already exists
            let filesContainer = lastUserMessage.querySelector('.files-container');
            if (!filesContainer) {
                // Create files container
                filesContainer = document.createElement('div');
                filesContainer.className = 'files-container mt-2';
                filesContainer.innerHTML = '<div class="uploaded-files-header"><small class="text-muted"><i class="fas fa-paperclip"></i> فایل‌های آپلود شده:</small></div>';
                
                // Insert before message actions (if they exist) or at the end
                const messageActions = lastUserMessage.querySelector('.message-actions');
                if (messageActions) {
                    lastUserMessage.insertBefore(filesContainer, messageActions);
                } else {
                    lastUserMessage.appendChild(filesContainer);
                }
            }
            
            // Add each file
            userData.uploaded_files.forEach((file, index) => {
                // Determine file icon based on mimetype
                let iconClass = 'fas fa-file text-muted';
                if (file.mimetype.startsWith('image/')) {
                    iconClass = 'fas fa-file-image text-primary';
                } else if (file.mimetype === 'application/pdf') {
                    iconClass = 'fas fa-file-pdf text-danger';
                } else if (file.mimetype.startsWith('text/')) {
                    iconClass = 'fas fa-file-alt text-info';
                } else if (file.mimetype.includes('word')) {
                    iconClass = 'fas fa-file-word text-primary';
                } else if (file.mimetype.includes('excel') || file.mimetype.includes('sheet')) {
                    iconClass = 'fas fa-file-excel text-success';
                }
                
                // Format file size
                let sizeText = formatFileSize(file.size);
                
                const fileItemHtml = `
                    <div class="uploaded-file-item d-flex align-items-center p-2 mb-1 bg-light rounded">
                        <i class="${iconClass} me-2"></i>
                        <div class="flex-grow-1">
                            <div class="fw-semibold">${file.filename}</div>
                            <div class="small text-muted">${sizeText}</div>
                        </div>
                        <div class="file-actions">
                            ${file.mimetype.startsWith('image/') ? 
                                `<button class="btn btn-sm btn-outline-primary me-1 preview-image-btn" data-image-url="${file.download_url}" title="پیش‌نمایش"><i class="fas fa-eye"></i></button>` : ''
                            }
                            <a href="${file.download_url}" download="${file.filename}" class="btn btn-sm btn-outline-success" title="دانلود">
                                <i class="fas fa-download"></i>
                            </a>
                        </div>
                    </div>
                `;
                
                filesContainer.insertAdjacentHTML('beforeend', fileItemHtml);
            });
            
            // Set up image preview functionality for uploaded files
            setupImagePreviewButtons(lastUserMessage);
            
            // Scroll to show the updated message
            setTimeout(() => {
                scrollToBottom();
            }, 100);
        }
    } else {
        console.warn('No user messages found to update with server data');
    }
}

// Function to ensure all messages have proper IDs
function ensureMessageIds() {
    // Get all messages that don't have IDs
    const messagesWithoutIds = document.querySelectorAll('.message-user:not([data-message-id]), .message-assistant:not([data-message-id])');
    console.log('Found messages without IDs:', messagesWithoutIds.length);
    
    // For each message without an ID, we can't do much except log a warning
    // In a real implementation, we might want to reload the session or handle this differently
    messagesWithoutIds.forEach((message, index) => {
        console.warn('Message without ID found:', message);
    });
}





// Function to show image generation success notification
function showImageGenerationSuccess() {
    // Create a temporary success notification
    const notification = document.createElement('div');
    notification.className = 'alert alert-success alert-dismissible fade show position-fixed';
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 1050; max-width: 320px;';
    notification.innerHTML = `
        <div class="d-flex align-items-center">
            <i class="fas fa-check-circle me-2"></i>
            <div>
                <strong>تصویر با موفقیت تولید شد!</strong><br>
                <small>صفحه در حال به‌روزرسانی...</small>
            </div>
            <button type="button" class="btn-close ms-2" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remove notification after 5 seconds (though page will refresh before that)
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}
