// =================================
// ویرایش پیام‌ها (Message Editing)
// =================================

// متغیرهای سراسری برای مدیریت ویرایش پیام
let currentEditingMessageId = null;
let originalMessageContent = null;
let currentInlineEditElement = null;

// Utility function to scroll to bottom with better reliability
function scrollToBottom() {
    // Multiple approaches to ensure scrolling works in all scenarios
    function doScroll() {
        window.scrollTo(0, document.body.scrollHeight);
    }
    
    // Immediate scroll
    doScroll();
    
    // Scroll after a short delay to handle DOM updates
    setTimeout(doScroll, 10);
    
    // Scroll using requestAnimationFrame for better timing
    requestAnimationFrame(doScroll);
    
    // Additional scroll attempts with increasing delays
    setTimeout(doScroll, 50);
    setTimeout(doScroll, 100);
    setTimeout(doScroll, 200);
}

// Helper function to check if the user is near the bottom of the page
function isUserAtBottom() {
    // A small buffer in pixels to ensure it works on all screen sizes
    const threshold = 50; 
    return (window.innerHeight + window.scrollY) >= (document.body.scrollHeight - threshold);
}

// Function to add copy buttons to code blocks and quotes
function addCopyButtonsToContent(messageElement) {
    // Add copy buttons to code blocks
    const codeBlocks = messageElement.querySelectorAll('pre');
    codeBlocks.forEach(block => {
        // Check if copy button already exists
        if (!block.querySelector('.copy-code-btn')) {
            const copyBtn = document.createElement('button');
            copyBtn.className = 'btn btn-sm btn-outline-secondary copy-code-btn';
            copyBtn.innerHTML = '<i class="fas fa-copy"></i>';
            copyBtn.title = 'کپی کد';
            copyBtn.style.cssText = 'position: absolute; top: 5px; left: 5px; z-index: 10;';
            
            // Wrap the code block in a relative container if needed
            const parent = block.parentNode;
            if (parent.style.position !== 'relative') {
                block.style.position = 'relative';
                block.style.paddingTop = '30px'; // Make space for the button
            }
            
            block.appendChild(copyBtn);
            
            copyBtn.addEventListener('click', function() {
                const code = block.querySelector('code');
                if (code) {
                    const text = code.textContent || code.innerText;
                    if (navigator.clipboard) {
                        navigator.clipboard.writeText(text).then(() => {
                            // Show success feedback
                            const originalHTML = copyBtn.innerHTML;
                            copyBtn.innerHTML = '<i class="fas fa-check"></i>';
                            setTimeout(() => {
                                copyBtn.innerHTML = originalHTML;
                            }, 2000);
                        }).catch(err => {
                            console.error('Failed to copy: ', err);
                        });
                    } else {
                        // Fallback for older browsers
                        const textArea = document.createElement('textarea');
                        textArea.value = text;
                        document.body.appendChild(textArea);
                        textArea.select();
                        try {
                            document.execCommand('copy');
                            // Show success feedback
                            const originalHTML = copyBtn.innerHTML;
                            copyBtn.innerHTML = '<i class="fas fa-check"></i>';
                            setTimeout(() => {
                                copyBtn.innerHTML = originalHTML;
                            }, 2000);
                        } catch (err) {
                            console.error('Fallback: Oops, unable to copy', err);
                        }
                        document.body.removeChild(textArea);
                    }
                }
            });
        }
    });
    
    // Add copy buttons to blockquotes
    const blockquotes = messageElement.querySelectorAll('blockquote');
    blockquotes.forEach(blockquote => {
        // Check if copy button already exists
        if (!blockquote.querySelector('.copy-quote-btn')) {
            const copyBtn = document.createElement('button');
            copyBtn.className = 'btn btn-sm btn-outline-secondary copy-quote-btn';
            copyBtn.innerHTML = '<i class="fas fa-copy"></i>';
            copyBtn.title = 'کپی نقل قول';
            copyBtn.style.cssText = 'position: absolute; top: 5px; right: 5px; z-index: 10;';
            
            // Wrap the blockquote in a relative container if needed
            const parent = blockquote.parentNode;
            if (parent.style.position !== 'relative') {
                blockquote.style.position = 'relative';
                blockquote.style.paddingRight = '30px'; // Make space for the button
            }
            
            blockquote.appendChild(copyBtn);
            
            copyBtn.addEventListener('click', function() {
                const text = blockquote.textContent || blockquote.innerText;
                if (navigator.clipboard) {
                    navigator.clipboard.writeText(text).then(() => {
                        // Show success feedback
                        const originalHTML = copyBtn.innerHTML;
                        copyBtn.innerHTML = '<i class="fas fa-check"></i>';
                        setTimeout(() => {
                            copyBtn.innerHTML = originalHTML;
                        }, 2000);
                    }).catch(err => {
                        console.error('Failed to copy: ', err);
                    });
                } else {
                    // Fallback for older browsers
                    const textArea = document.createElement('textarea');
                    textArea.value = text;
                    document.body.appendChild(textArea);
                    textArea.select();
                    try {
                        document.execCommand('copy');
                        // Show success feedback
                        const originalHTML = copyBtn.innerHTML;
                        copyBtn.innerHTML = '<i class="fas fa-check"></i>';
                        setTimeout(() => {
                            copyBtn.innerHTML = originalHTML;
                        }, 2000);
                    } catch (err) {
                        console.error('Fallback: Oops, unable to copy', err);
                    }
                    document.body.removeChild(textArea);
                }
            });
        }
    });
}

// تابع برای اضافه کردن دکمه ویرایش به پیام‌های کاربر
function addEditButtonToUserMessages() {
    console.log('Adding edit buttons to user messages');
    // پیدا کردن تمام پیام‌های کاربر
    const userMessages = document.querySelectorAll('.message-user');
    console.log('Found user messages:', userMessages.length);
    
    userMessages.forEach((messageElement, index) => {
        console.log('Processing message', index, messageElement);
        // بررسی اینکه آیا دکمه ویرایش قبلاً اضافه شده یا نه
        if (!messageElement.querySelector('.edit-message-btn')) {
            // پیدا کردن کانتینر اکشن‌ها
            const actionsContainer = messageElement.querySelector('.message-actions');
            if (actionsContainer) {
                console.log('Found actions container for message', index);
                
                // Check if this is an image editing chatbot
                const sessionData = JSON.parse(localStorage.getItem(`session_${currentSessionId}`) || '{}');
                if (sessionData.chatbot_type === 'image_editing') {
                    // For image editing chatbots, don't add edit buttons
                    console.log('Skipping edit button for image editing chatbot');
                    return;
                }
                
                // ایجاد دکمه ویرایش
                const editButton = document.createElement('button');
                editButton.className = 'btn btn-sm btn-outline-primary edit-message-btn ms-2';
                editButton.innerHTML = '<i class="fas fa-edit"></i> ویرایش';
                editButton.title = 'ویرایش پیام';
                
                // اضافه کردن event listener
                editButton.addEventListener('click', function() {
                    const messageElement = this.closest('.message-user');
                    // Fix: Try multiple ways to get the message ID
                    const messageId = messageElement.dataset.messageId || 
                                     messageElement.getAttribute('data-message-id') ||
                                     messageElement.id;
                    console.log('Message ID from data attribute:', messageId);
                    if (!messageId) {
                        console.error('Message ID not found in data attribute');
                        alert('خطا: شناسه پیام یافت نشد.');
                        return;
                    }
                    const messageContent = messageElement.querySelector('.message-content').textContent;
                    // Open inline editor instead of modal
                    openInlineEditor(messageElement, messageId, messageContent);
                });
                
                // اضافه کردن دکمه به کانتینر اکشن‌ها
                actionsContainer.appendChild(editButton);
                console.log('Added edit button to message', index);
            } else {
                console.log('No actions container found for message', index);
            }
        } else {
            console.log('Edit button already exists for message', index);
        }
    });
}

// تابع برای باز کردن مودال ویرایش پیام
function openEditModal(messageId, content) {
    // ذخیره اطلاعات پیام اصلی
    currentEditingMessageId = messageId;
    originalMessageContent = content;
    
    // ایجاد مودال HTML
    const modalHtml = `
        <div class="modal fade" id="editMessageModal" tabindex="-1" aria-labelledby="editMessageModalLabel" aria-hidden="true">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title" id="editMessageModalLabel">
                            <i class="fas fa-edit"></i> ویرایش پیام
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        <div class="mb-3">
                            <label for="editMessageContent" class="form-label">محتوای پیام:</label>
                            <textarea class="form-control" id="editMessageContent" rows="4">${content}</textarea>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                            <i class="fas fa-times"></i> لغو
                        </button>
                        <button type="button" class="btn btn-primary" id="saveEditButton">
                            <i class="fas fa-save"></i> ذخیره تغییرات
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // اضافه کردن مودال به body
    const modalContainer = document.createElement('div');
    modalContainer.innerHTML = modalHtml;
    document.body.appendChild(modalContainer);
    
    // نمایش مودال
    const editModal = new bootstrap.Modal(document.getElementById('editMessageModal'));
    editModal.show();
    
    // اضافه کردن event listener برای دکمه ذخیره
    document.getElementById('saveEditButton').addEventListener('click', saveEditedMessage);
    
    // حذف مودال بعد از بسته شدن
    document.getElementById('editMessageModal').addEventListener('hidden.bs.modal', function () {
        document.body.removeChild(modalContainer);
        currentEditingMessageId = null;
        originalMessageContent = null;
    });
}

// تابع برای باز کردن ویرایشگر درون خطی
function openInlineEditor(messageElement, messageId, content) {
    // ذخیره اطلاعات پیام اصلی
    currentEditingMessageId = messageId;
    originalMessageContent = content;
    currentInlineEditElement = messageElement;
    
    // گرفتن المان محتوای پیام
    const contentElement = messageElement.querySelector('.message-content');
    
    // ایجاد textarea برای ویرایش
    const textarea = document.createElement('textarea');
    textarea.className = 'form-control';
    textarea.value = content;
    textarea.rows = 4;
    
    // ایجاد دکمه‌های ذخیره و لغو
    const buttonContainer = document.createElement('div');
    buttonContainer.className = 'mt-2';
    buttonContainer.innerHTML = `
        <button class="btn btn-sm btn-primary save-inline-edit">
            <i class="fas fa-save"></i> ذخیره تغییرات
        </button>
        <button class="btn btn-sm btn-secondary cancel-inline-edit ms-2">
            <i class="fas fa-times"></i> لغو
        </button>
    `;
    
    // جایگزینی محتوای پیام با textarea
    contentElement.innerHTML = '';
    contentElement.appendChild(textarea);
    contentElement.appendChild(buttonContainer);
    
    // فوکوس روی textarea
    textarea.focus();
    
    // اضافه کردن event listener برای دکمه ذخیره
    buttonContainer.querySelector('.save-inline-edit').addEventListener('click', function() {
        saveInlineEdit(messageId, textarea.value.trim());
    });
    
    // اضافه کردن event listener برای دکمه لغو
    buttonContainer.querySelector('.cancel-inline-edit').addEventListener('click', function() {
        cancelInlineEdit(messageElement, content);
    });
    
    // اضافه کردن event listener برای کلید Enter
    textarea.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && e.ctrlKey) {
            saveInlineEdit(messageId, textarea.value.trim());
        }
    });
}

// تابع برای ذخیره پیام ویرایش شده
function saveEditedMessage() {
    const newContent = document.getElementById('editMessageContent').value.trim();
    
    if (!newContent) {
        alert('محتوای پیام نمی‌تواند خالی باشد.');
        return;
    }
    
    if (!currentEditingMessageId) {
        console.error('currentEditingMessageId is null or undefined');
        alert('خطا: شناسه پیام یافت نشد.');
        return;
    }
    
    console.log('Editing message with ID:', currentEditingMessageId);
    
    if (newContent === originalMessageContent) {
        // اگر محتوا تغییر نکرده، فقط مودال را ببند
        const editModal = bootstrap.Modal.getInstance(document.getElementById('editMessageModal'));
        editModal.hide();
        return;
    }
    
    // بررسی محدودیت‌ها قبل از ویرایش
    if (!checkUsageLimitsBeforeEdit()) {
        return;
    }
    
    // نمایش loading state
    const saveButton = document.getElementById('saveEditButton');
    const originalButtonText = saveButton.innerHTML;
    saveButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> در حال پردازش...';
    saveButton.disabled = true;
    
    // ارسال درخواست به سرور برای ویرایش پیام
    fetch(`/chat/session/${currentSessionId}/message/${currentEditingMessageId}/edit/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            content: newContent
        })
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(data => {
                throw new Error(data.error || 'خطا در ویرایش پیام');
            });
        }
        
        // پردازش streaming response برای پاسخ جدید
        return handleEditStreamingResponse(response);
    })
    .then(() => {
        // بستن مودال
        const editModal = bootstrap.Modal.getInstance(document.getElementById('editMessageModal'));
        editModal.hide();
        
        // بروزرسانی محتوای پیام در UI
        updateMessageContentInUI(currentEditingMessageId, newContent);
        
        // نمایش پیام موفقیت
        showSuccessMessage('پیام با موفقیت ویرایش شد.');
    })
    .catch(error => {
        console.error('Error editing message:', error);
        alert(`خطا: ${error.message || 'خطای نامشخص در ویرایش پیام'}`);
    })
    .finally(() => {
        // بازگرداندن وضعیت دکمه
        saveButton.innerHTML = originalButtonText;
        saveButton.disabled = false;
    });
}

// تابع برای ذخیره ویرایش درون خطی
function saveInlineEdit(messageId, newContent) {
    if (!newContent) {
        alert('محتوای پیام نمی‌تواند خالی باشد.');
        return;
    }
    
    if (!messageId) {
        console.error('Message ID not found');
        alert('خطا: شناسه پیام یافت نشد.');
        return;
    }
    
    if (newContent === originalMessageContent) {
        // اگر محتوا تغییر نکرده، فقط لغو ویرایش کن
        cancelInlineEdit(currentInlineEditElement, originalMessageContent);
        return;
    }
    
    // بررسی محدودیت‌ها قبل از ویرایش
    if (!checkUsageLimitsBeforeEdit()) {
        return;
    }
    
    // نمایش loading state
    const contentElement = currentInlineEditElement.querySelector('.message-content');
    contentElement.innerHTML = '<div class="text-center"><span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> در حال پردازش...</div>';
    
    // ارسال درخواست به سرور برای ویرایش پیام
    fetch(`/chat/session/${currentSessionId}/message/${messageId}/edit/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            content: newContent
        })
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(data => {
                throw new Error(data.error || 'خطا در ویرایش پیام');
            });
        }
        
        // پردازش streaming response برای پاسخ جدید
        return handleEditStreamingResponse(response);
    })
    .then(() => {
        // Check if this is an image editing chatbot
        const sessionData = JSON.parse(localStorage.getItem(`session_${currentSessionId}`) || '{}');
        if (sessionData.chatbot_type === 'image_editing') {
            // For image editing chatbots, refresh the page after successful image generation
            showSuccessMessage('ویرایش پیام انجام شد. صفحه به‌روزرسانی می‌شود...');
            setTimeout(() => {
                location.reload();
            }, 1500); // Refresh after showing success message
        } else {
            // For regular chatbots, show success message and don't refresh
            showSuccessMessage('پیام با موفقیت ویرایش شد.');
        }
    })
    .catch(error => {
        console.error('Error editing message:', error);
        // بازگرداندن محتوای اصلی در صورت خطا
        if (currentInlineEditElement) {
            const contentElement = currentInlineEditElement.querySelector('.message-content');
            contentElement.textContent = originalMessageContent;
        }
        alert(`خطا: ${error.message || 'خطای نامشخص در ویرایش پیام'}`);
    });
}

// تابع برای بررسی محدودیت‌ها قبل از ویرایش
function checkUsageLimitsBeforeEdit() {
    // در اینجا می‌توانید بررسی‌های لازم را انجام دهید
    // مثلاً بررسی تعداد توکن‌ها، محدودیت‌های اشتراک و غیره
    // برای سادگی، فعلاً true برمی‌گردانیم
    return true;
}

// تابع برای پردازش streaming response در زمان ویرایش
function handleEditStreamingResponse(response) {
    return new Promise((resolve, reject) => {
        // نمایش typing indicator
        showTypingIndicator();
        
        let assistantContent = '';
        let imagesData = [];
        let disabledMessageIds = []; // Array to store IDs of disabled messages
        let assistantMessageId = null; // To store the ID of the new assistant message
        
        const reader = response.body.getReader();
        const decoder = new TextDecoder('utf-8');
        
        function read() {
            reader.read().then(({ done, value }) => {
                if (done) {
                    console.log('Stream finished, finalizing response');
                    // حذف typing indicator
                    hideTypingIndicator();
                    
                    // Remove the streaming assistant message if it exists
                    const streamingElement = document.getElementById('streaming-assistant');
                    if (streamingElement) {
                        streamingElement.remove();
                    }
                    
                    // اضافه کردن پیام دستیار
                    const messageData = {
                        type: 'assistant',
                        content: assistantContent,
                        created_at: new Date().toISOString()
                    };
                    
                    // Add the assistant message ID if we have it
                    if (assistantMessageId) {
                        messageData.id = assistantMessageId;
                    }
                    
                    // اضافه کردن URL تصاویر در صورت وجود
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
                    
                    console.log('Adding final assistant message to chat:', messageData);
                    addMessageToChat(messageData);
                    
                    // Check if this is an image editing chatbot and we have images
                    const sessionData = JSON.parse(localStorage.getItem(`session_${currentSessionId}`) || '{}');
                    if (sessionData.chatbot_type === 'image_editing' && hasImages) {
                        // For image editing chatbots, refresh the page after successful image generation
                        console.log('Image generated successfully during editing, refreshing page...');
                        setTimeout(() => {
                            location.reload();
                        }, 2000); // Refresh after 2 seconds to allow user to see the message
                        return;
                    }
                    
                    // For all other chatbots, don't refresh the page to allow users to see the streaming updates
                    console.log('Message editing completed successfully, keeping page for user to see updates...');
                    
                    return;
                }
                
                try {
                    const chunk = decoder.decode(value, { stream: true });
                    console.log('Received chunk:', chunk);
                    
                    // پردازش داده‌های پیام‌های غیرفعال
                    if (chunk.includes('[DISABLED_MESSAGES]') && chunk.includes('[DISABLED_MESSAGES_END]')) {
                        const startIdx = chunk.indexOf('[DISABLED_MESSAGES]') + 19;
                        const endIdx = chunk.indexOf('[DISABLED_MESSAGES_END]');
                        const disabledMessagesJson = chunk.substring(startIdx, endIdx);
                        try {
                            const disabledData = JSON.parse(disabledMessagesJson);
                            disabledMessageIds = disabledData.disabled_message_ids || [];
                            console.log('Received disabled message IDs:', disabledMessageIds);
                            // Mark messages as disabled in UI immediately
                            markMessagesAsDisabled(disabledMessageIds);
                            // Remove disabled messages immediately with a small delay to ensure DOM updates
                            setTimeout(() => {
                                removeDisabledMessages(disabledMessageIds);
                            }, 200); // افزایش تاخیر به 200 میلی‌ثانیه
                        } catch (parseError) {
                            console.error('Error parsing disabled messages data:', parseError);
                        }
                    }
                    // پردازش داده‌های شناسه پیام دستیار
                    else if (chunk.includes('[ASSISTANT_MESSAGE_ID]') && chunk.includes('[ASSISTANT_MESSAGE_ID_END]')) {
                        const startIdx = chunk.indexOf('[ASSISTANT_MESSAGE_ID]') + 22;
                        const endIdx = chunk.indexOf('[ASSISTANT_MESSAGE_ID_END]');
                        const assistantMessageJson = chunk.substring(startIdx, endIdx);
                        try {
                            const assistantMessageData = JSON.parse(assistantMessageJson);
                            assistantMessageId = assistantMessageData.assistant_message_id;
                            console.log('Received assistant message ID:', assistantMessageId);
                        } catch (parseError) {
                            console.error('Error parsing assistant message ID data:', parseError);
                        }
                    }
                    
                    // Buffer to accumulate partial data
                    let buffer = chunk;
                    
                    // Process complete markers from buffer
                    while (true) {
                        // Check for different types of markers
                        const imagesStart = buffer.indexOf('[IMAGES]');
                        const imagesEnd = buffer.indexOf('[IMAGES_END]');
                        const usageDataStart = buffer.indexOf('[USAGE_DATA]');
                        const usageDataEnd = buffer.indexOf('[USAGE_DATA_END]');
                        
                        let processed = false;
                        
                        // Find the first marker in the buffer
                        const markers = [
                            { start: imagesStart, end: imagesEnd, name: 'IMAGES' },
                            { start: usageDataStart, end: usageDataEnd, name: 'USAGE_DATA' }
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
                                case 'IMAGES':
                                    const imagesJson = buffer.substring(8, imagesEnd); // 8 = length of '[IMAGES]'
                                    try {
                                        const newImages = JSON.parse(imagesJson);
                                        imagesData = imagesData.concat(newImages);
                                        console.log('Received images data:', imagesData);
                                        // Update the streaming message with images immediately
                                        updateOrAddAssistantMessageWithImages(assistantContent, imagesData);
                                        
                                        // Force scroll to show the new images
                                        setTimeout(() => {
                                            scrollToBottom();
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
                            }
                        } else if (buffer.length > 0) {
                            // If no markers found, add the entire buffer as regular content
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
                console.error('Stream reading error:', error);
                // Remove the streaming assistant message if it exists
                const streamingElement = document.getElementById('streaming-assistant');
                if (streamingElement) {
                    streamingElement.remove();
                }
                
                hideTypingIndicator();
                reject(error);
            });
        }
        read();
    });
}

// تابع برای بروزرسانی محتوای پیام در UI
function updateMessageContentInUI(messageId, newContent) {
    console.log('Updating message content in UI for message ID:', messageId);
    // پیدا کردن پیام مربوطه
    const messageElement = document.querySelector(`.message-user[data-message-id="${messageId}"]`);
    if (messageElement) {
        console.log('Found message element to update:', messageElement);
        // بروزرسانی محتوای پیام
        const contentElement = messageElement.querySelector('.message-content');
        if (contentElement) {
            // رندر Markdown برای محتوای جدید
            try {
                contentElement.innerHTML = md.render(newContent);
            } catch (e) {
                console.error('Error rendering markdown:', e);
                contentElement.textContent = newContent;
            }
            
            // اضافه کردن دکمه‌های کپی به بلوک‌های کد و نقل‌قول‌ها
            addCopyButtonsToContent(messageElement);
        }
        
        // نمایش نشان ویرایش شده
        const headerElement = messageElement.querySelector('.message-header');
        if (headerElement && !headerElement.querySelector('.edited-badge')) {
            const editedBadge = document.createElement('span');
            editedBadge.className = 'badge bg-secondary ms-2 edited-badge';
            editedBadge.textContent = 'ویرایش شده';
            editedBadge.title = 'این پیام ویرایش شده است';
            headerElement.appendChild(editedBadge);
        }
        
        // ریست کردن متغیرهای سراسری
        currentEditingMessageId = null;
        originalMessageContent = null;
        currentInlineEditElement = null;
    } else {
        console.warn('Message element not found for ID:', messageId);
    }
    
    // Scroll to bottom after updating message
    // Add a delay to ensure scrolling happens after content is updated
    setTimeout(() => {
        scrollToBottom();
    }, 100); // افزایش تاخیر به 100 میلی‌ثانیه
}

// تابع برای نمایش پیام موفقیت
function showSuccessMessage(message) {
    // ایجاد المان پیام موفقیت
    const alertElement = document.createElement('div');
    alertElement.className = 'alert alert-success alert-dismissible fade show position-fixed';
    alertElement.style.cssText = 'bottom: 20px; left: 50%; transform: translateX(-50%); z-index: 10000;';
    alertElement.innerHTML = `
        <i class="fas fa-check-circle"></i> ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    // اضافه کردن به body
    document.body.appendChild(alertElement);
    
    // حذف خودکار پیام بعد از 3 ثانیه
    setTimeout(() => {
        if (alertElement.parentNode) {
            alertElement.parentNode.removeChild(alertElement);
        }
    }, 3000);
}

// تابع برای لغو ویرایش درون خطی
function cancelInlineEdit(messageElement, originalContent) {
    const contentElement = messageElement.querySelector('.message-content');
    try {
        contentElement.innerHTML = md.render(originalContent);
    } catch (e) {
        console.error('Error rendering markdown:', e);
        contentElement.textContent = originalContent;
    }
    
    // اضافه کردن دکمه‌های کپی به بلوک‌های کد و نقل‌قول‌ها
    addCopyButtonsToContent(messageElement);
    
    // ریست کردن متغیرهای سراسری
    currentEditingMessageId = null;
    originalMessageContent = null;
    currentInlineEditElement = null;
}

// تابع برای حذف پیام‌های بعد از پیام ویرایش شده
function removeSubsequentMessages(messageId) {
    // پیدا کردن پیام ویرایش شده
    const editedMessageElement = document.querySelector(`.message-user[data-message-id="${messageId}"]`);
    if (editedMessageElement) {
        // حذف تمام پیام‌های بعد از آن
        let nextElement = editedMessageElement.nextElementSibling;
        while (nextElement) {
            const elementToRemove = nextElement;
            nextElement = nextElement.nextElementSibling;
            elementToRemove.remove();
        }
    }
}

// تابع برای علامت‌گذاری پیام‌ها به عنوان غیرفعال
function markMessagesAsDisabled(messageIds) {
    console.log('Marking messages as disabled with IDs:', messageIds);
    try {
        messageIds.forEach(messageId => {
            // پیدا کردن پیام‌های با شناسه مشخص
            const messageElements = document.querySelectorAll(`[data-message-id="${messageId}"]`);
            console.log(`Found ${messageElements.length} elements with message ID ${messageId}`);
            messageElements.forEach(element => {
                // علامت‌گذاری به عنوان غیرفعال
                element.dataset.disabled = 'true';
                element.style.opacity = '0.5';
                element.style.pointerEvents = 'none';
                console.log('Marked element as disabled:', element);
            });
        });
        
        // Scroll to bottom after marking messages
        // Add a small delay to ensure scrolling happens after elements are marked
        setTimeout(() => {
            scrollToBottom();
        }, 100); // افزایش تاخیر به 100 میلی‌ثانیه
    } catch (error) {
        console.error('Error marking messages as disabled:', error);
    }
}

// Variable to track if we're currently removing disabled messages
let isRemovingDisabledMessages = false;

// تابع برای حذف پیام‌های غیرفعال شده
function removeDisabledMessages(disabledMessageIds) {
    // Prevent duplicate calls
    if (isRemovingDisabledMessages) {
        console.log('Already removing disabled messages, skipping duplicate call');
        return;
    }
    
    isRemovingDisabledMessages = true;
    console.log('Attempting to remove disabled messages with IDs:', disabledMessageIds);
    
    try {
        // If we have specific message IDs to remove, use them
        if (disabledMessageIds && disabledMessageIds.length > 0) {
            disabledMessageIds.forEach(messageId => {
                // پیدا کردن پیام‌های با شناسه مشخص و حذف آنها
                const messageElements = document.querySelectorAll(`[data-message-id="${messageId}"]`);
                console.log(`Found ${messageElements.length} elements with message ID ${messageId}`);
                messageElements.forEach(element => {
                    console.log('Removing element:', element);
                    // Add a delay to ensure the element is fully removed
                    setTimeout(() => {
                        if (element.parentNode) {
                            element.remove();
                        }
                    }, 50); // افزایش تاخیر به 50 میلی‌ثانیه
                });
            });
        } else {
            // پیدا کردن تمام پیام‌های غیرفعال و حذف آنها
            const disabledMessages = document.querySelectorAll('.message-user[data-disabled="true"], .message-assistant[data-disabled="true"]');
            console.log(`Found ${disabledMessages.length} disabled messages by attribute`);
            disabledMessages.forEach(messageElement => {
                console.log('Removing disabled message element:', messageElement);
                // Add a delay to ensure the element is fully removed
                setTimeout(() => {
                    if (messageElement.parentNode) {
                        messageElement.remove();
                    }
                }, 50); // افزایش تاخیر به 50 میلی‌ثانیه
            });
            
            // همچنین پیدا کردن پیام‌هایی که ممکن است با کلاس‌های دیگر علامت‌گذاری شده باشند
            const allMessages = document.querySelectorAll('.message-user, .message-assistant');
            console.log(`Found ${allMessages.length} total messages`);
            allMessages.forEach(messageElement => {
                if (messageElement.dataset.disabled === 'true') {
                    console.log('Removing message element with dataset disabled:', messageElement);
                    // Add a delay to ensure the element is fully removed
                    setTimeout(() => {
                        if (messageElement.parentNode) {
                            messageElement.remove();
                        }
                    }, 50); // افزایش تاخیر به 50 میلی‌ثانیه
                }
            });
        }
        
        // Scroll to bottom after removing messages
        // Add a delay to ensure scrolling happens after elements are removed
        setTimeout(() => {
            scrollToBottom();
            // Reset the flag after scrolling
            isRemovingDisabledMessages = false;
        }, 100); // افزایش تاخیر به 100 میلی‌ثانیه
    } catch (error) {
        console.error('Error removing disabled messages:', error);
        // Reset the flag in case of error
        isRemovingDisabledMessages = false;
    }
}

// Update or add assistant message for streaming
function updateOrAddAssistantMessage(content) {
    const chatContainer = document.getElementById('chat-container');
    let assistantElement = document.getElementById('streaming-assistant');
    
    // Render Markdown for the content
    let renderedContent;
    try {
        renderedContent = md.render(content);
    } catch (e) {
        console.error('Error rendering markdown:', e);
        // Show error message in Persian
        if (e.message && e.message.includes('code') || e.message.includes('quote') || e.message.includes('newline')) {
            renderedContent = '<div class="alert alert-warning">هشدار: فرمت خط جدید یا نقل‌قول‌ها به درستی رندر نشدند.</div>' + md.utils.escapeHtml(content);
        } else {
            // Fallback to plain text if markdown rendering fails
            renderedContent = md.utils.escapeHtml(content);
        }
    }
    
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
            <div class="message-content">${renderedContent}</div>
        `;
        assistantElement.innerHTML = elementContent;
        chatContainer.appendChild(assistantElement);
    } else {
        // Update existing element content only
        const contentDiv = assistantElement.querySelector('.message-content');
        if (contentDiv) {
            contentDiv.innerHTML = renderedContent;
            
            // Apply syntax highlighting to new code blocks
            if (hljs) {
                const codeBlocks = contentDiv.querySelectorAll('pre code');
                codeBlocks.forEach(block => {
                    if (!block.dataset.highlighted) {
                        try {
                            // اطمینان از اینکه محتوا escape شده است
                            if (block.innerHTML && !block.dataset.highlighted) {
                                // بررسی امنیتی HTML
                                if (block.innerHTML.includes('<') && !block.innerHTML.includes('&lt;')) {
                                    block.innerHTML = block.innerHTML.replace(/</g, '&lt;').replace(/>/g, '&gt;');
                                }
                                hljs.highlightElement(block);
                                block.dataset.highlighted = 'true';
                            }
                        } catch (e) {
                            console.warn('Syntax highlighting failed for block:', e);
                        }
                    }
                });
            }
        }
    }
    
    // Add copy buttons to code blocks and quotes
    addCopyButtonsToContent(assistantElement);
    
    // Scroll to bottom during streaming ONLY if the user is already at the bottom
    if (isUserAtBottom()) {
        scrollToBottom();
    }
}

// Update the streaming handler to handle images
function updateOrAddAssistantMessageWithImages(content, imagesData = null) {
    const chatContainer = document.getElementById('chat-container');
    let assistantElement = document.getElementById('streaming-assistant');
    
    // Render Markdown for the content
    let renderedContent;
    try {
        renderedContent = md.render(content);
    } catch (e) {
        console.error('Error rendering markdown:', e);
        // Show error message in Persian
        if (e.message && e.message.includes('code') || e.message.includes('quote') || e.message.includes('newline')) {
            renderedContent = '<div class="alert alert-warning">هشدار: فرمت خط جدید یا نقل‌قول‌ها به درستی رندر نشدند.</div>' + md.utils.escapeHtml(content);
        } else {
            // Fallback to plain text if markdown rendering fails
            renderedContent = md.utils.escapeHtml(content);
        }
    }
    
    // Add image display if imagesData is present
    let imageContent = '';
    if (imagesData && imagesData.length > 0) {
        console.log('Processing images for display:', imagesData);
        imagesData.forEach((img, index) => {
            if (img.image_url && img.image_url.url) {
                // Handle both absolute URLs and relative paths
                let imageUrl = img.image_url.url;
                // If it's a relative path, prepend the media URL
                if (!imageUrl.startsWith('http') && !imageUrl.startsWith('/media/')) {
                    imageUrl = '/media/' + imageUrl;
                }
                // If it already starts with /media/, make sure it's properly formatted
                else if (imageUrl.startsWith('/media/')) {
                    // It's already correctly formatted
                }
                // If it's already an absolute URL, leave it as is
                console.log(`Image ${index + 1} URL:`, imageUrl);
                imageContent += `<div class="image-container mt-2" data-image-index="${index}">
                    <img src="${imageUrl}" alt="Generated image" class="img-fluid rounded" style="max-width: 100%; height: auto;" onload="console.log('Image ${index + 1} loaded successfully')" onerror="console.error('Failed to load image ${index + 1}:', this.src)">
                    <div class="mt-1">
                        <a href="${imageUrl}" download class="btn btn-sm btn-outline-primary">
                            <i class="fas fa-download"></i> دانلود تصویر
                        </a>
                    </div>
                </div>`;
            }
        });
        console.log('Generated image content HTML:', imageContent);
    }
    
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
            <div class="message-content">${renderedContent}</div>
            ${imageContent}
        `;
        assistantElement.innerHTML = elementContent;
        chatContainer.appendChild(assistantElement);
    } else {
        // Update existing element content only
        const contentDiv = assistantElement.querySelector('.message-content');
        if (contentDiv) {
            contentDiv.innerHTML = renderedContent;
            
            // Apply syntax highlighting to new code blocks
            if (hljs) {
                const codeBlocks = contentDiv.querySelectorAll('pre code');
                codeBlocks.forEach(block => {
                    if (!block.dataset.highlighted) {
                        try {
                            // اطمینان از اینکه محتوا escape شده است
                            if (block.innerHTML && !block.dataset.highlighted) {
                                // بررسی امنیتی HTML
                                if (block.innerHTML.includes('<') && !block.innerHTML.includes('&lt;')) {
                                    block.innerHTML = block.innerHTML.replace(/</g, '&lt;').replace(/>/g, '&gt;');
                                }
                                hljs.highlightElement(block);
                                block.dataset.highlighted = 'true';
                            }
                        } catch (e) {
                            console.warn('Syntax highlighting failed for block:', e);
                        }
                    }
                });
            }
        }
        
        // Add images if they exist
        // Always update/replace images to ensure they're current
        const existingImageContainers = assistantElement.querySelectorAll('.image-container');
        if (existingImageContainers.length > 0) {
            // Remove existing image containers
            existingImageContainers.forEach(container => container.remove());
        }
        
        if (imageContent) {
            // Add the new image content
            assistantElement.insertAdjacentHTML('beforeend', imageContent);
            
            // Force image loading and display
            const newImages = assistantElement.querySelectorAll('.image-container img');
            newImages.forEach(img => {
                img.onload = function() {
                    // Scroll to show the image when it loads
                    setTimeout(() => {
                        scrollToBottom();
                    }, 50);
                };
                // Ensure image loads even if cached
                if (img.complete) {
                    setTimeout(() => {
                        scrollToBottom();
                    }, 50);
                }
            });
        }
    }
    
    // Add copy buttons to code blocks and quotes
    addCopyButtonsToContent(assistantElement);
    
    // Scroll to bottom during streaming ONLY if the user is already at the bottom
    if (isUserAtBottom()) {
        scrollToBottom();
    }
}

// تابع برای بارگذاری مجدد پیام‌های جلسه
function reloadSessionMessages() {
    if (!currentSessionId) return;
    
    fetch(`/chat/session/${currentSessionId}/messages/`)
        .then(response => response.json())
        .then(data => {
            const chatContainer = document.getElementById('chat-container');
            chatContainer.innerHTML = ''; // پاک کردن محتوای فعلی
            
            // اضافه کردن پیام‌ها
            data.messages.forEach(message => {
                addMessageToChat(message);
            });
            
            // اضافه کردن دکمه‌های ویرایش
            addEditButtonToUserMessages();
        })
        .catch(error => {
            console.error('Error reloading messages:', error);
        });
}

// تابع برای آغاز ویرایش پیام
function startEditingMessage(messageId, content) {
    openEditModal(messageId, content);
}

// اضافه کردن event listener برای بارگذاری دکمه‌های ویرایش
document.addEventListener('DOMContentLoaded', function() {
    // اضافه کردن دکمه‌های ویرایش بعد از بارگذاری پیام‌ها
    setTimeout(addEditButtonToUserMessages, 1000);
});

//
// اضافه کردن دکمه‌های ویرایش بعد از هر بار اضافه شدن پیام جدید
const originalAddMessageToChat = addMessageToChat;
addMessageToChat = function(message) {
    originalAddMessageToChat(message);
    // اضافه کردن دکمه‌های ویرایش با تاخیر کم
    setTimeout(addEditButtonToUserMessages, 100);
};