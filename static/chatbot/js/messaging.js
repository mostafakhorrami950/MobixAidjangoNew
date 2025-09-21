// =================================
// ارسال پیام‌ها و long polling (Message Sending & Long Polling)
// =================================

// Send message with long polling support (replaces streaming)
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
    // Don't disable the send button immediately - keep it enabled for stop functionality
    // document.getElementById('send-button').disabled = true;

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

    // ساخت یک کنترلر جدید برای هر درخواست
    abortController = new AbortController(); // ساخت یک کنترلر جدید برای هر درخواست
    setButtonState(true); // تغییر دکمه به حالت "توقف"

    // Unified fetch request to 'initiate_ai_response' endpoint instead of 'send_message'
    fetch(`/chat/session/${currentSessionId}/initiate-ai-response/`, {
        method: 'POST',
        headers: {
            // 'Content-Type' is automatically set to 'multipart/form-data' by the browser when using FormData
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: formData,
        signal: abortController.signal // اتصال کنترلر به درخواست
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(data => {
                throw new Error(data.error || 'Error sending message');
            });
        }
        
        // Parse the JSON response
        return response.json();
    })
    .then(data => {
        if (data.status === 'processing_started' && data.assistant_message_id) {
            // Create an empty assistant message element
            const assistantMessageElement = addMessageToChat({
                type: 'assistant',
                content: '',
                created_at: new Date().toISOString(),
                id: data.assistant_message_id
            });
            
            // Verify that the assistantMessageElement was created successfully
            if (assistantMessageElement) {
                // Start polling for chunks
                pollForChunks(data.assistant_message_id, assistantMessageElement, 0);
            } else {
                console.error('Failed to create assistant message element');
                throw new Error('Failed to create assistant message element');
            }
        } else {
            throw new Error('Invalid response from server');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        hideTypingIndicator();
        addMessageToChat({
            type: 'assistant',
            content: `خطا: ${error.message || 'خطای نامشخص'}`,
            created_at: new Date().toISOString()
        });
        
        // Re-enable input and reset button state
        messageInput.disabled = false;
        messageInput.focus();
        setButtonState(false);
    });
}

// Polling function for getting response chunks
function pollForChunks(messageId, assistantMessageElement, offset) {
    // Add error checking to ensure assistantMessageElement exists
    if (!assistantMessageElement) {
        console.error('assistantMessageElement is undefined in pollForChunks');
        hideTypingIndicator();
        setButtonState(false);
        return;
    }
    
    // Try to get the contentDiv, with error handling
    let contentDiv = assistantMessageElement.querySelector('.message-content');
    if (!contentDiv) {
        console.error('Could not find .message-content element in assistantMessageElement');
        // Try to find the element by messageId as a fallback
        const messageElement = document.querySelector(`[data-message-id="${messageId}"]`);
        if (messageElement) {
            contentDiv = messageElement.querySelector('.message-content');
        }
        
        // If still not found, create a temporary error message
        if (!contentDiv) {
            console.error('Could not find message element with ID:', messageId);
            hideTypingIndicator();
            setButtonState(false);
            return;
        }
    }

    fetch(`/chat/session/${currentSessionId}/get_chunk/?message_id=${messageId}&offset=${offset}`)
        .then(response => response.json())
        .then(data => {
            if (data.status === 'new_chunk') {
                // Add the new chunk to the current content
                contentDiv.textContent += data.content_chunk;

                // If the user is at the bottom, scroll
                if (isUserAtBottom()) {
                    scrollToBottom();
                }

                // Call pollForChunks again with the new offset after a short delay
                setTimeout(() => {
                    pollForChunks(messageId, assistantMessageElement, data.new_offset);
                }, 100); // Short delay for smooth streaming

            } else if (data.status === 'complete') {
                // Polling is complete
                hideTypingIndicator();
                setButtonState(false); // Enable the send button

                // Now that the text is complete, render it with Markdown
                const fullText = contentDiv.textContent;
                contentDiv.innerHTML = md.render(fullText);

                // Style code and add copy buttons
                if (hljs) {
                    contentDiv.querySelectorAll('pre code').forEach(block => {
                        hljs.highlightElement(block);
                    });
                }
                addCopyButtonsToContent(assistantMessageElement);
                scrollToBottom();
            }
        })
        .catch(error => {
            console.error('Polling Error:', error);
            hideTypingIndicator();
            setButtonState(false);
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
        document.getElementById('message-input').disabled = false;
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
        sendMessage();
        
    } catch (error) {
        hideTypingIndicator();
        console.error('Error creating default session:', error);
        alert('خطا در ایجاد چت جدید: ' + error.message);
    }
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
