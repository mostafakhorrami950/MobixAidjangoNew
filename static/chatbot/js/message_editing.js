// =================================
// ویرایش پیام‌ها (Message Editing)
// =================================

// متغیرهای سراسری برای مدیریت ویرایش پیام
let currentEditingMessageId = null;
let originalMessageContent = null;
let currentInlineEditElement = null;

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
        // نمایش پیام موفقیت
        showSuccessMessage('ویرایش پیام انجام شد. صفحه به‌روزرسانی می‌شود...');
        
        // Refresh the page to ensure clean UI state
        setTimeout(() => {
            location.reload();
        }, 1500); // Refresh after showing success message
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

// تابع برای پردازش response در زمان ویرایش با long polling
function handleEditStreamingResponse(response) {
    return new Promise((resolve, reject) => {
        // نمایش typing indicator
        showTypingIndicator();
        
        response.json().then(data => {
            // حذف typing indicator
            hideTypingIndicator();
            
            if (data.success) {
                // Mark messages as disabled in UI immediately
                if (data.disabled_message_ids) {
                    markMessagesAsDisabled(data.disabled_message_ids);
                    // Remove disabled messages immediately with a small delay to ensure DOM updates
                    setTimeout(() => {
                        removeDisabledMessages(data.disabled_message_ids);
                    }, 200);
                }
                
                // Display the assistant response with typing effect
                displayTextGradually(data.content);
                
                // For all chatbots, refresh the page to ensure clean UI state after editing
                console.log('Message editing completed successfully, refreshing page for clean UI...');
                setTimeout(() => {
                    location.reload();
                }, 1500); // Refresh after 1.5 seconds to show success message first
                
                resolve();
            } else {
                // Handle error
                addMessageToChat({
                    type: 'assistant',
                    content: `خطا: ${data.error || 'خطای نامشخص'}`,
                    created_at: new Date().toISOString()
                });
                reject(new Error(data.error || 'خطای نامشخص'));
            }
        }).catch(error => {
            console.error('Error parsing JSON response:', error);
            hideTypingIndicator();
            reject(error);
        });
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