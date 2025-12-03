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
        // Instead of storing in session storage, send the message directly after creating session
        createDefaultSession().then(sessionData => {
            if (sessionData && sessionData.session_id) {
                // Session created successfully, now send the message
                // Re-call sendMessage after a short delay to ensure UI is updated
                setTimeout(() => {
                    // Update the message input with the original message
                    const msgInput = document.getElementById('message-input');
                    if (msgInput) {
                        msgInput.value = message;
                        // Now send the message
                        sendMessage();
                    }
                }, 100);
            } else {
                // Handle error in session creation
                console.error('Failed to create session:', sessionData.error || 'No session ID returned');
                alert('خطا در ایجاد چت جدید: ' + (sessionData.error || 'پاسخ نامعتبر از سرور'));
            }
        }).catch(error => {
            // Handle network or other unexpected errors
            console.error('Error creating default session:', error);
            alert('یک خطای غیرمنتظره در هنگام ایجاد چت جدید رخ داد. لطفا اتصال اینترنت خود را بررسی کرده و صفحه را دوباره بارگیری کنید.');
        });
        return;
    }

    // Prepare display message
    let displayMessage = message;
    if (files.length > 0) {
        const fileNames = files.map(f => f.name).join(', ');
        displayMessage += ` (فایل‌ها: ${fileNames})`;
    }

    // Add user message to chat immediately with Markdown support
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

    // Check if this is an image generation session
    const sessionData = JSON.parse(localStorage.getItem(`session_${currentSessionId}`) || '{}');
    const isImageEditingChatbot = sessionData.chatbot_type === 'image_editing';
    
    // Hide cancel button for image editing chatbots
    const sendButton = document.getElementById('send-button');
    if (isImageEditingChatbot) {
        // Hide the stop icon completely for image editing chatbots
        const stopIcon = sendButton.querySelector('.stop-icon');
        if (stopIcon) {
            stopIcon.style.display = 'none';
        }
        // Also hide the send icon to prevent cancellation
        const sendIcon = sendButton.querySelector('.send-icon');
        if (sendIcon) {
            sendIcon.style.display = 'none';
        }
        // Disable the button completely
        sendButton.disabled = true;
    } else {
        // For regular chatbots, show the stop button as usual
        setButtonState(true); // Change button to stop state
    }

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

    let assistantContent = '';
    let imagesData = [];
    let userMessageData = null; // To store user message data from server
    let userMessageElement = null; // To store reference to user message element
    let assistantMessageId = null; // To store assistant message ID from server
    
    // ساخت یک کنترلر جدید برای هر درخواست
    abortController = new AbortController(); // ساخت یک کنترلر جدید برای هر درخواست

    // Unified fetch request to 'send_message' endpoint
    fetch(`/chat/session/${currentSessionId}/send/`, {
        method: 'POST',
        headers: {
            // 'Content-Type' is automatically set to 'multipart/form-data' by the browser when using FormData
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: formData,
        signal: abortController.signal // Connect controller to request
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(data => {
                throw new Error(data.error || 'Error sending message');
            });
        }

        // Handle streaming response
        const reader = response.body.getReader();
        const decoder = new TextDecoder('utf-8');
        
        // Buffer to accumulate partial data
        let buffer = '';

        function read() {
            reader.read().then(({ done, value }) => {
                if (done) {
                    console.log('Message sending stream finished');
                    const streamingElement = document.getElementById('streaming-assistant');
                    if (streamingElement) {
                        streamingElement.remove();
                    }
                
                    // Add final message with images if any
                    const messageData = {
                        type: 'assistant',
                        content: assistantContent,
                        created_at: new Date().toISOString()
                    };
                    
                    // Add the assistant message ID if we have it
                    if (assistantMessageId) {
                        messageData.id = assistantMessageId;
                    }
                
                    // Add image URLs if any images were generated
                    let hasImages = false;
                    if (imagesData.length > 0) {
                        const formattedImageUrls = imagesData.map(img => {
                            if (img.image_url && img.image_url.url) {
                                let imageUrl = img.image_url.url;
                                if (!imageUrl.startsWith('http') && !imageUrl.startsWith('/media/')) {
                                    imageUrl = '/media/' + imageUrl;
                                }
                                return imageUrl;
                            }
                            return '';
                        }).filter(url => url.trim() !== '');
                        
                        if (formattedImageUrls.length > 0) {
                            messageData.image_url = formattedImageUrls.join(',');
                            hasImages = true;
                        }
                    }
                
                    addMessageToChat(messageData);
                    hideTypingIndicator();
                    
                    // Check if this is an image editing chatbot
                    const sessionData = JSON.parse(localStorage.getItem(`session_${currentSessionId}`) || '{}');
                    if (sessionData.chatbot_type === 'image_editing') {
                        // For image editing chatbots, refresh page after every AI message
                        console.log('AI message received in image editing chatbot, refreshing page...');
                        
                        // Re-enable message input after image generation
                        enableNewMessagesAfterImageGeneration();
                        
                        // Refresh the page after a short delay
                        setTimeout(() => {
                            window.location.reload();
                        }, 1000); // 1 second delay
                        return;
                    } else if (sessionData.chatbot_type === 'image_editing' && hasImages) {
                        // For image editing chatbots with images, show success notification and refresh page
                        console.log('Image generated successfully, refreshing page...');
                        
                        // Re-enable message input after image generation
                        enableNewMessagesAfterImageGeneration();
                        
                        // Show a brief success notification
                        showImageGenerationSuccess();
                        
                        // Refresh the page after a short delay to show the notification
                        setTimeout(() => {
                            window.location.reload();
                        }, 1500); // 1.5 second delay to show notification
                        return;
                    } else if (hasImages) {
                        // For any other chatbot with images, ensure they're visible
                        setTimeout(() => {
                            // Only scroll if user hasn't scrolled up
                            if (typeof userScrolledUp !== 'undefined' && !userScrolledUp) {
                                scrollToBottom();
                            }
                        }, 200);
                    }
                    
                    // Re-enable input and reset button state
                    messageInput.disabled = false;
                    messageInput.focus();
                    
                    // For image editing chatbots, don't restore the button state since we hid it completely
                    if (!isImageEditingChatbot) {
                        setButtonState(false);
                    } else {
                        // Re-enable the button but keep it hidden for image editing chatbots
                        sendButton.disabled = false;
                    }
                    return;
                }

                try {
                    const chunk = decoder.decode(value, { stream: true });
                    console.log('Received chunk from message sending:', chunk);
                    
                    // Accumulate chunk in buffer
                    buffer += chunk;
                    
                    // Process complete markers from buffer
                    while (true) {
                        // Check for different types of markers
                        const userMessageStart = buffer.indexOf('[USER_MESSAGE]');
                        const userMessageEnd = buffer.indexOf('[USER_MESSAGE_END]');
                        const assistantMessageIdStart = buffer.indexOf('[ASSISTANT_MESSAGE_ID]');
                        const assistantMessageIdEnd = buffer.indexOf('[ASSISTANT_MESSAGE_ID_END]');
                        const imagesStart = buffer.indexOf('[IMAGES]');
                        const imagesEnd = buffer.indexOf('[IMAGES_END]');
                        const usageDataStart = buffer.indexOf('[USAGE_DATA]');
                        const usageDataEnd = buffer.indexOf('[USAGE_DATA_END]');
                        const titleUpdateStart = buffer.indexOf('[TITLE_UPDATE]');
                        const titleUpdateEnd = buffer.indexOf('[TITLE_UPDATE_END]');
                        
                        let processed = false;
                        
                        // Find the first marker in the buffer
                        const markers = [
                            { start: userMessageStart, end: userMessageEnd, name: 'USER_MESSAGE' },
                            { start: assistantMessageIdStart, end: assistantMessageIdEnd, name: 'ASSISTANT_MESSAGE_ID' },
                            { start: imagesStart, end: imagesEnd, name: 'IMAGES' },
                            { start: usageDataStart, end: usageDataEnd, name: 'USAGE_DATA' },
                            { start: titleUpdateStart, end: titleUpdateEnd, name: 'TITLE_UPDATE' }
                        ];
                        
                        // Filter out markers that are not found (-1)
                        const foundMarkers = markers.filter(marker => marker.start !== -1 && marker.end !== -1);
                        
                        if (foundMarkers.length > 0) {
                            // Find the marker with the earliest start position
                            const firstMarker = foundMarkers.reduce((earliest, current) => 
                                current.start < earliest.start ? current : earliest
                            );
                            
                            // Process any text before the first marker
                            if (firstMarker.start > 0) {
                                const textBeforeMarker = buffer.substring(0, firstMarker.start);
                                assistantContent += textBeforeMarker;
                                console.log('Adding text before marker to assistant message:', textBeforeMarker);
                                
                                // Update the streaming message with current content
                                if (imagesData.length > 0) {
                                    updateOrAddAssistantMessageWithImages(assistantContent, imagesData);
                                } else {
                                    updateOrAddAssistantMessage(assistantContent);
                                }
                                
                                // Remove processed text from buffer
                                buffer = buffer.substring(firstMarker.start);
                                processed = true;
                                continue;
                            }
                            
                            // Handle the first marker based on its type
                            switch (firstMarker.name) {
                                case 'USER_MESSAGE':
                                    const userMessageJson = buffer.substring(14, userMessageEnd); // 14 = length of '[USER_MESSAGE]'
                                    try {
                                        userMessageData = JSON.parse(userMessageJson);
                                        console.log('Received user message data from server:', userMessageData);
                                        // Update the temporary user message with the real data from server
                                        updateUserMessageWithServerData(userMessageData);
                                    } catch (parseError) {
                                        console.error('Error parsing user message data:', parseError);
                                    }
                                    
                                    // Remove processed data from buffer
                                    buffer = buffer.substring(userMessageEnd + 18); // 18 = length of '[USER_MESSAGE_END]'
                                    processed = true;
                                    continue;
                                    
                                case 'ASSISTANT_MESSAGE_ID':
                                    const assistantMessageJson = buffer.substring(22, assistantMessageIdEnd); // 22 = length of '[ASSISTANT_MESSAGE_ID]'
                                    try {
                                        const assistantData = JSON.parse(assistantMessageJson);
                                        assistantMessageId = assistantData.assistant_message_id;
                                        console.log('Received assistant message ID:', assistantMessageId);
                                    } catch (parseError) {
                                        console.error('Error parsing assistant message ID:', parseError);
                                    }
                                    
                                    // Remove processed data from buffer
                                    buffer = buffer.substring(assistantMessageIdEnd + 26); // 26 = length of '[ASSISTANT_MESSAGE_ID_END]'
                                    processed = true;
                                    continue;
                                    
                                case 'IMAGES':
                                    const imagesJson = buffer.substring(8, imagesEnd); // 8 = length of '[IMAGES]'
                                    try {
                                        const newImages = JSON.parse(imagesJson);
                                        imagesData = imagesData.concat(newImages);
                                        console.log('Received images data:', imagesData);
                                        // Update the streaming message with images immediately
                                        updateOrAddAssistantMessageWithImages(assistantContent, imagesData);
                                        
                                        // Force scroll to show the new images ONLY if user hasn't scrolled up
                                        setTimeout(() => {
                                            if (typeof userScrolledUp !== 'undefined' && !userScrolledUp) {
                                                scrollToBottom();
                                            }
                                        }, 100);
                                    } catch (parseError) {
                                        console.error('Error parsing images data:', parseError);
                                    }
                                    
                                    // Remove processed data from buffer
                                    buffer = buffer.substring(imagesEnd + 12); // 12 = length of '[IMAGES_END]'
                                    processed = true;
                                    continue;
                                    
                                case 'USAGE_DATA':
                                    // We don't need to do anything with usage data here
                                    // It's handled on the server side
                                    console.log('Received usage data, ignoring');
                                    
                                    // Remove processed data from buffer
                                    buffer = buffer.substring(usageDataEnd + 16); // 16 = length of '[USAGE_DATA_END]'
                                    processed = true;
                                    continue;
                                    
                                case 'TITLE_UPDATE':
                                    const titleJson = buffer.substring(14, titleUpdateEnd); // 14 = length of '[TITLE_UPDATE]'
                                    try {
                                        const titleData = JSON.parse(titleJson);
                                        console.log('Received title update:', titleData);
                                        if (titleData.title && titleData.session_id == currentSessionId) {
                                            updateSessionTitleInUI(titleData.title);
                                        }
                                    } catch (parseError) {
                                        console.error('Error parsing title update data:', parseError);
                                    }
                                    
                                    // Remove processed data from buffer
                                    buffer = buffer.substring(titleUpdateEnd + 18); // 18 = length of '[TITLE_UPDATE_END]'
                                    processed = true;
                                    continue;
                            }
                        } else if (buffer.length > 0) {
                            // If no markers found, check if buffer contains any marker start sequences
                            // If it does, we should wait for more data to complete the marker
                            // Otherwise, add the entire buffer as regular content
                            
                            // Check if buffer contains the start of any marker
                            const hasMarkerStart = 
                                buffer.includes('[USER_MESSAGE') || 
                                buffer.includes('[ASSISTANT_MESSAGE_ID') || 
                                buffer.includes('[IMAGES') || 
                                buffer.includes('[USAGE_DATA') || 
                                buffer.includes('[TITLE_UPDATE');
                            
                            if (!hasMarkerStart) {
                                // Safe to add the entire buffer as regular content
                                assistantContent += buffer;
                                console.log('Adding remaining buffer content to assistant message:', buffer);
                                
                                // Update the streaming message with current content
                                if (imagesData.length > 0) {
                                    updateOrAddAssistantMessageWithImages(assistantContent, imagesData);
                                } else {
                                    updateOrAddAssistantMessage(assistantContent);
                                }
                                
                                // Clear buffer
                                buffer = '';
                                processed = true;
                            }
                            // If buffer contains marker start, we wait for more data
                            // Don't set processed = true to continue the loop
                        }
                        
                        // If no content was processed, break
                        if (!processed) {
                            break;
                        }
                    }
                } catch (decodeError) {
                    console.error('Decoding error:', decodeError);
                }
                
                read();
            }).catch(error => {
                if (error.name === 'AbortError') {
                    console.log('درخواست توسط کاربر متوقف شد.');
                    // پیام ناقص قبلاً در سمت سرور ذخیره شده است
                    const streamingElement = document.getElementById('streaming-assistant');
                    if (streamingElement) {
                        streamingElement.remove();
                    }
                    hideTypingIndicator();
                    
                    // Check if we have images and this is an image editing chatbot
                    let hasImages = false;
                    let shouldRefresh = false;
                    
                    // Add final message with whatever content we have so far
                    if (assistantContent) {
                        const messageData = {
                            type: 'assistant',
                            content: assistantContent,
                            created_at: new Date().toISOString()
                        };
                        // Add image URLs if any images were generated
                        if (imagesData.length > 0) {
                            // Format image URLs properly
                            const formattedImageUrls = imagesData.map(img => {
                                if (img.image_url && img.image_url.url) {
                                    let imageUrl = img.image_url.url;
                                    // If it's a relative path, prepend the media URL
                                    if (!imageUrl.startsWith('http') && !imageUrl.startsWith('/media/')) {
                                        imageUrl = '/media/' + imageUrl;
                                    }
                                    return imageUrl;
                                }
                                return '';
                            }).filter(url => url.trim() !== '');
                            
                            messageData.image_url = formattedImageUrls.join(',');
                            hasImages = true;
                        }
                        addMessageToChat(messageData);
                    }
                    
                    // Check if this is an image editing chatbot and we have images
                    const sessionData = JSON.parse(localStorage.getItem(`session_${currentSessionId}`) || '{}');
                    if (sessionData.chatbot_type === 'image_editing' && hasImages) {
                        shouldRefresh = true;
                        console.log('Image generated via abort, refreshing page...');
                    }
                    
                    // Re-enable input and reset button state after streaming is complete
                    messageInput.disabled = false;
                    messageInput.focus();
                    setButtonState(false); // بازگرداندن دکمه به حالت "ارسال"
                    
                    // For image editing chatbots, re-enable message input
                    if (sessionData.chatbot_type === 'image_editing') {
                        enableNewMessagesAfterImageGeneration();
                    }
                    
                    // Refresh if needed
                    if (shouldRefresh) {
                        setTimeout(() => {
                            console.log('Refreshing page after aborted image generation');
                            window.location.reload();
                        }, 1000);
                    }
                } else {
                    console.error('Streaming error:', error);
                    const streamingElement = document.getElementById('streaming-assistant');
                    if (streamingElement) {
                        streamingElement.remove();
                    }
                    hideTypingIndicator();
                    addMessageToChat({
                        type: 'assistant',
                        content: `خطا: ${error.message || 'خطای نامشخص'}`,
                        created_at: new Date().toISOString()
                    });
                    // Re-enable input and reset button state after streaming is complete
                    messageInput.disabled = false;
                    messageInput.focus();
                    setButtonState(false); // بازگرداندن دکمه به حالت "ارسال"
                }
            });
        }
        read();
    })
    .then(data => {
        // Handle any additional data or actions after streaming is complete
        // For example, you can check if certain conditions are met and perform actions accordingly
        console.log('Message streaming complete:', data);
    })
    .catch(error => {
        // Remove the streaming assistant message if it exists
        const streamingElement = document.getElementById('streaming-assistant');
        if (streamingElement) {
            streamingElement.remove();
        }
        
        if (error.name === 'AbortError') {
            console.log('درخواست توسط کاربر متوقف شد.');
            // پیام ناقص قبلاً در سمت سرور ذخیره شده است
            hideTypingIndicator();
            
            let hasImages = false;
            let shouldRefresh = false;
            
            // Add final message with whatever content we have so far
            if (assistantContent) {
                const messageData = {
                    type: 'assistant',
                    content: assistantContent,
                    created_at: new Date().toISOString()
                };
                // Add image URLs if any images were generated
                if (imagesData.length > 0) {
                    // Format image URLs properly
                    const formattedImageUrls = imagesData.map(img => {
                        if (img.image_url && img.image_url.url) {
                            let imageUrl = img.image_url.url;
                            // If it's a relative path, prepend the media URL
                            if (!imageUrl.startsWith('http') && !imageUrl.startsWith('/media/')) {
                                imageUrl = '/media/' + imageUrl;
                            }
                            return imageUrl;
                        }
                        return '';
                    }).filter(url => url.trim() !== '');
                    
                    messageData.image_url = formattedImageUrls.join(',');
                    hasImages = true;
                }
                addMessageToChat(messageData);
            }
            
            // Check if this is an image editing chatbot
            const sessionData = JSON.parse(localStorage.getItem(`session_${currentSessionId}`) || '{}');
            if (sessionData.chatbot_type === 'image_editing') {
                shouldRefresh = true;
                console.log('Image editing chatbot message completed via abort, refreshing page...');
            } else if (sessionData.chatbot_type === 'image_editing' && hasImages) {
                shouldRefresh = true;
                console.log('Image generated via catch abort, refreshing page...');
            }
            
            // Re-enable input and reset button state after streaming is complete
            messageInput.disabled = false;
            messageInput.focus();
            
            // For image editing chatbots, don't restore the button state since we hid it completely
            if (!isImageEditingChatbot) {
                setButtonState(false); // Restore button to send state
            } else {
                // Re-enable the button but keep it hidden for image editing chatbots
                sendButton.disabled = false;
                // Re-enable message input for image editing chatbots
                enableNewMessagesAfterImageGeneration();
            }
            
            // Refresh if needed
            if (shouldRefresh) {
                setTimeout(() => {
                    console.log('Refreshing page after catch aborted image generation');
                    window.location.reload();
                }, 1000);
            }
        } else {
            console.error('Error:', error);
            hideTypingIndicator();
            addMessageToChat({
                type: 'assistant',
                content: `Error: ${error.message || 'Unknown error'}`,
                created_at: new Date().toISOString()
            });
            
            // Re-enable input and reset button state after streaming is complete
            messageInput.disabled = false;
            messageInput.focus();
            
            // For image editing chatbots, don't restore the button state since we hid it completely
            if (!isImageEditingChatbot) {
                setButtonState(false); // Restore button to send state
            } else {
                // Re-enable the button but keep it hidden for image editing chatbots
                sendButton.disabled = false;
                // Re-enable message input for image editing chatbots
                enableNewMessagesAfterImageGeneration();
            }
        }
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

// Update or add assistant message for streaming
function updateOrAddAssistantMessage(content) {
    const chatContainer = document.getElementById('chat-container');
    let assistantElement = document.getElementById('streaming-assistant');
    
    if (!assistantElement) {
        // Create new assistant message element with same structure as addMessageToChat
        assistantElement = document.createElement('div');
        assistantElement.className = 'message-assistant';
        assistantElement.id = 'streaming-assistant';
        
        // Format timestamp
        const timestamp = new Date().toLocaleTimeString('fa-IR');
        
        // Create message content with metadata (similar to addMessageToChat)
        let elementContent = `
            <div class="message-header">
                <strong>دستیار</strong>
                <small class="text-muted float-end">${timestamp}</small>
            </div>
            <div class="message-content"></div>
        `;
        assistantElement.innerHTML = elementContent;
        chatContainer.appendChild(assistantElement);
    }
    
    // Update content immediately without typing effect for better streaming experience
    const contentDiv = assistantElement.querySelector('.message-content');
    if (contentDiv) {
        // Render Markdown for the content
        let renderedContent;
        try {
            renderedContent = md.render(content);
        } catch (e) {
            console.error('Error rendering markdown:', e);
            renderedContent = md.utils.escapeHtml(content).replace(/\n/g, '<br>');
        }
        
        contentDiv.innerHTML = renderedContent;
        
        // Apply syntax highlighting to code blocks immediately
        if (hljs) {
            const codeBlocks = contentDiv.querySelectorAll('pre code');
            codeBlocks.forEach(block => {
                if (!block.dataset.highlighted) {
                    try {
                        hljs.highlightElement(block);
                        block.dataset.highlighted = 'true';
                    } catch (e) {
                        console.warn('Syntax highlighting failed for block:', e);
                    }
                }
            });
        }
    }
    
    // Add copy buttons to code blocks and quotes
    addCopyButtonsToContent(assistantElement);
    
    // Scroll to bottom during streaming ONLY if the user is already at the bottom
    // and hasn't scrolled up manually
    if (typeof userScrolledUp !== 'undefined' && !userScrolledUp && isUserAtBottom()) {
        scrollToBottom();
    }
}

// Update the streaming handler to handle images
function updateOrAddAssistantMessageWithImages(content, imagesData = null) {
    const chatContainer = document.getElementById('chat-container');
    let assistantElement = document.getElementById('streaming-assistant');
    
    if (!assistantElement) {
        // Create new assistant message element with same structure as addMessageToChat
        assistantElement = document.createElement('div');
        assistantElement.className = 'message-assistant';
        assistantElement.id = 'streaming-assistant';
        
        // Format timestamp
        const timestamp = new Date().toLocaleTimeString('fa-IR');
        
        // Create message content with metadata (similar to addMessageToChat)
        let elementContent = `
            <div class="message-header">
                <strong>دستیار</strong>
                <small class="text-muted float-end">${timestamp}</small>
            </div>
            <div class="message-content"></div>
        `;
        assistantElement.innerHTML = elementContent;
        chatContainer.appendChild(assistantElement);
    }
    
    // Update content immediately without typing effect for better streaming experience
    const contentDiv = assistantElement.querySelector('.message-content');
    if (contentDiv) {
        // Render Markdown for the content
        let renderedContent;
        try {
            renderedContent = md.render(content);
        } catch (e) {
            console.error('Error rendering markdown:', e);
            renderedContent = md.utils.escapeHtml(content).replace(/\n/g, '<br>');
        }
        
        contentDiv.innerHTML = renderedContent;
        
        // Apply syntax highlighting to code blocks immediately
        if (hljs) {
            const codeBlocks = contentDiv.querySelectorAll('pre code');
            codeBlocks.forEach(block => {
                if (!block.dataset.highlighted) {
                    try {
                        hljs.highlightElement(block);
                        block.dataset.highlighted = 'true';
                    } catch (e) {
                        console.warn('Syntax highlighting failed for block:', e);
                    }
                }
            });
        }
    }
    
    // Add images if they exist
    if (imagesData && imagesData.length > 0) {
        // Check if images have already been added
        const existingImageContainers = assistantElement.querySelectorAll('.image-container');
        if (existingImageContainers.length === 0) {
            // Add image display
            let imageContent = '';
            imagesData.forEach((img, index) => {
                if (img.image_url && img.image_url.url) {
                    // Handle both absolute URLs and relative paths
                    let imageUrl = img.image_url.url;
                    // If it's a relative path, prepend the media URL
                    if (!imageUrl.startsWith('http') && !imageUrl.startsWith('/media/')) {
                        imageUrl = '/media/' + imageUrl;
                    }
                    imageContent += `<div class="image-container mt-2" data-image-index="${index}">
                        <img src="${imageUrl}" alt="Generated image" class="img-fluid rounded" style="max-width: 100%; height: auto;">
                        <div class="mt-1">
                            <a href="${imageUrl}" download class="btn btn-sm btn-outline-primary">
                                <i class="fas fa-download"></i> Download image
                            </a>
                        </div>
                    </div>`;
                }
            });
            
            if (imageContent) {
                // Add the image content
                assistantElement.insertAdjacentHTML('beforeend', imageContent);
                
                // Force image loading and display
                const newImages = assistantElement.querySelectorAll('.image-container img');
                newImages.forEach(img => {
                    img.onload = function() {
                        // Scroll to show the image when it loads ONLY if user hasn't scrolled up
                        setTimeout(() => {
                            if (typeof userScrolledUp !== 'undefined' && !userScrolledUp) {
                                scrollToBottom();
                            }
                        }, 50);
                    };
                    // Ensure image loads even if cached
                    if (img.complete) {
                        setTimeout(() => {
                            if (typeof userScrolledUp !== 'undefined' && !userScrolledUp) {
                                scrollToBottom();
                            }
                        }, 50);
                    }
                });
            }
        }
    }
    
    // Add copy buttons to code blocks and quotes
    addCopyButtonsToContent(assistantElement);
    
    // Scroll to bottom during streaming ONLY if the user is already at the bottom
    // and hasn't scrolled up manually
    if (typeof userScrolledUp !== 'undefined' && !userScrolledUp && isUserAtBottom()) {
        scrollToBottom();
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
    // For image editing chatbots, don't abort the request so image generation can continue
    const sessionData = JSON.parse(localStorage.getItem(`session_${currentSessionId}`) || '{}');
    if (sessionData.chatbot_type !== 'image_editing') {
        // For non-image editing chatbots, abort the request
        if (abortController && !abortController.signal.aborted) {
            abortController.abort();
        }
    }
    // For image editing chatbots, let the request continue in the background
});

/**
 * ایجاد جلسه پیش‌فرض و ارسال پیام
 * Create default session and send message
 */
async function createDefaultSessionAndSendMessage(message, files) {
    try {
        // نمایش پیام انتظار
        showTypingIndicator();
        
        // Store the message content in session storage so it can be sent after page refresh
        if (message) {
            sessionStorage.setItem('pendingMessage', message);
        }
        
        // Store files info in session storage if needed
        if (files && files.length > 0) {
            // For simplicity, we'll just store the fact that files were selected
            sessionStorage.setItem('pendingFiles', 'true');
        }
        
        // ایجاد جلسه پیش‌فرض
        const sessionData = await createDefaultSession();
        
        // The page will refresh automatically after createDefaultSession
        // so the following code will not execute
        /*
        // حالا پیام را ارسال کنیم
        // Re-enable input before sending message
        const messageInput = document.getElementById('message-input');
        messageInput.disabled = false;
        // Use the improved sendMessage function
        sendMessage();
        */
        
    } catch (error) {
        hideTypingIndicator();
        console.error('Error creating default session:', error);
        alert('خطا در ایجاد چت جدید: ' + error.message);
    }
}

// Standalone function to create a default session without sending a message
async function createDefaultSession() {
    try {
        // Prepare data for creating session
        const sessionCreateData = {};
        
        // If a model is selected for new session, use it
        if (selectedModelForNewSession) {
            sessionCreateData.ai_model_id = selectedModelForNewSession;
        }
        
        // Create default session
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
            alert('خطا در ایجاد چت جدید: ' + data.error);
            return data; // Return error data
        }
        
        // Set new session ID
        currentSessionId = data.session_id;
        
        // Instead of refreshing the page, update the URL and UI without refresh
        const newUrl = `/chat/session/${currentSessionId}/`;
        history.pushState({sessionId: currentSessionId}, '', newUrl);
        
        // Update UI with null checks
        const sessionTitleElement = document.getElementById('current-session-title');
        if (sessionTitleElement) {
            sessionTitleElement.innerHTML = `
                <i class="fas fa-comments"></i> ${data.title}
            `;
        }
        
        const deleteSessionBtn = document.getElementById('delete-session-btn');
        if (deleteSessionBtn) {
            deleteSessionBtn.style.display = 'inline-block';
        }
        
        // Enable inputs
        const messageInput = document.getElementById('message-input');
        if (messageInput) {
            messageInput.disabled = false;
        }
        
        const sendButton = document.getElementById('send-button');
        if (sendButton) {
            sendButton.disabled = false;
        }
        
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
        
        // Update sessions list
        loadSessions();
        
        // Hide welcome message
        const welcomeMessage = document.getElementById('welcome-message');
        if (welcomeMessage) {
            welcomeMessage.style.display = 'none';
        }
        
        return data; // Return session data
    } catch (error) {
        console.error('Error creating default session:', error);
        alert('خطا در ایجاد چت جدید: ' + error.message);
        throw error; // Re-throw error for caller to handle
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
        
        // Update the message content with Markdown support
        const contentDiv = lastUserMessage.querySelector('.message-content');
        if (contentDiv && userData.content) {
            try {
                contentDiv.innerHTML = md.render(userData.content);
            } catch (e) {
                console.error('Error rendering markdown for user message:', e);
                // Fallback to plain text if markdown rendering fails
                contentDiv.textContent = userData.content;
            }
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

// Function to display text immediately for streaming
function typeText(element, text) {
    // For streaming, we want to display text immediately as it arrives
    // Store the target element and text as data attributes
    element.dataset.targetText = text;
    
    // Clear any existing timeouts
    if (element.typingTimeout) {
        clearTimeout(element.typingTimeout);
        element.typingTimeout = null;
    }
    
    // Display the text immediately without any typing effect
    // Convert markdown to HTML for the current text
    let htmlContent;
    try {
        // For streaming, we render the partial text as-is without markdown
        // to avoid issues with incomplete markdown tags
        htmlContent = md.utils.escapeHtml(text);
        // But we can still handle line breaks
        htmlContent = htmlContent.replace(/\n/g, '<br>');
    } catch (e) {
        console.error('Error rendering markdown:', e);
        htmlContent = md.utils.escapeHtml(text);
    }
    
    element.innerHTML = htmlContent;
    
    // Store current text
    element.dataset.currentText = text;
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
                <strong>Image generated successfully!</strong><br>
                <small>Page refreshing...</small>
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

// Add a new function to prevent new messages during image generation
function preventNewMessagesDuringImageGeneration() {
    const sessionData = JSON.parse(localStorage.getItem(`session_${currentSessionId}`) || '{}');
    if (sessionData.chatbot_type === 'image_editing') {
        // Disable the message input and send button
        const messageInput = document.getElementById('message-input');
        const sendButton = document.getElementById('send-button');
        
        if (messageInput) {
            messageInput.disabled = true;
            messageInput.placeholder = "لطفاً تا پایان تولید تصویر منتظر بمانید...";
        }
        
        if (sendButton) {
            sendButton.disabled = true;
        }
    }
}

// Add a new function to re-enable message sending after image generation
function enableNewMessagesAfterImageGeneration() {
    const sessionData = JSON.parse(localStorage.getItem(`session_${currentSessionId}`) || '{}');
    if (sessionData.chatbot_type === 'image_editing') {
        // Re-enable the message input and send button
        const messageInput = document.getElementById('message-input');
        const sendButton = document.getElementById('send-button');
        
        if (messageInput) {
            messageInput.disabled = false;
            messageInput.placeholder = "پیام خود را وارد کنید...";
            messageInput.focus();
        }
        
        if (sendButton) {
            sendButton.disabled = false;
        }
    }
}
