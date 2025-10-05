// =================================
// نمایش پیام‌ها و رندر محتوا (Messages Display)
// =================================

// Utility function to scroll to bottom with enhanced reliability
function scrollToBottom() {
    // Multiple approaches to ensure scrolling works in all scenarios
    function doScroll() {
        // Try both window and document.documentElement scrolling
        const scrollHeight = Math.max(
            document.body.scrollHeight,
            document.documentElement.scrollHeight,
            document.body.offsetHeight,
            document.documentElement.offsetHeight
        );
        
        // Scroll window to bottom
        window.scrollTo({
            top: scrollHeight,
            behavior: 'smooth'
        });
        
        // Also try document.documentElement for better compatibility
        document.documentElement.scrollTop = scrollHeight;
        document.body.scrollTop = scrollHeight; // For Safari
    }
    
    // Immediate scroll
    doScroll();
    
    // Use requestAnimationFrame for smooth scrolling
    requestAnimationFrame(() => {
        doScroll();
        
        // Additional delayed scrolls to handle dynamic content
        setTimeout(doScroll, 50);
        setTimeout(doScroll, 150);
        setTimeout(doScroll, 300);
    });
}

// Helper function to check if the user is near the bottom of the page
function isUserAtBottom() {
    // A small buffer in pixels to ensure it works on all screen sizes
    const threshold = 50; 
    return (window.innerHeight + window.scrollY) >= (document.body.scrollHeight - threshold);
}

// Add message to chat display
function addMessageToChat(message) {
    const chatContainer = document.getElementById('chat-container');
    const welcomeMessage = document.getElementById('welcome-message');
    if (welcomeMessage) {
        welcomeMessage.remove();
    }
    
    // Check if a message with this ID already exists to prevent duplicates
    if (message.id) {
        const existingMessage = document.querySelector(`[data-message-id="${message.id}"]`);
        if (existingMessage) {
            // If message already exists, update its content instead of creating a new one
            console.log('Updating existing message with ID:', message.id);
            
            // Check if the existing message is disabled and we're trying to add a non-disabled message
            // This can happen when editing messages
            if (existingMessage.dataset.disabled === 'true' && !message.disabled) {
                console.log('Removing disabled message before adding updated version');
                existingMessage.remove();
                // Continue to create a new message element
            } else {
                // Update the existing message
                const contentDiv = existingMessage.querySelector('.message-content');
                if (contentDiv) {
                    if (message.type === 'assistant') {
                        try {
                            contentDiv.innerHTML = md.render(message.content);
                        } catch (e) {
                            console.error('Error rendering markdown:', e);
                            contentDiv.textContent = message.content;
                        }
                    } else {
                        contentDiv.textContent = message.content;
                    }
                }
                
                // Update image content if present
                if (message.image_url) {
                    let imageContent = '';
                    const imageUrls = message.image_url.split(',');
                    imageUrls.forEach(url => {
                        if (url.trim()) {
                            let imageUrl = url.trim();
                            if (!imageUrl.startsWith('http') && !imageUrl.startsWith('/media/')) {
                                imageUrl = '/media/' + imageUrl;
                            }
                            imageContent += `<div class="image-container mt-2">
                                <img src="${imageUrl}" alt="Generated image" class="img-fluid rounded" style="max-width: 100%; height: auto;">
                                <div class="mt-1">
                                    <a href="${imageUrl}" download class="btn btn-sm btn-outline-primary">
                                        <i class="fas fa-download"></i> دانلود تصویر
                                    </a>
                                </div>
                            </div>`;
                        }
                    });
                    
                    // Add images if they don't already exist
                    if (imageContent && !existingMessage.querySelector('.image-container')) {
                        existingMessage.insertAdjacentHTML('beforeend', imageContent);
                    }
                }
                
                // Scroll to bottom
                scrollToBottom();
                return;
            }
        }
    } else {
        console.log('Adding message without ID:', message);
    }
    
    const messageElement = document.createElement('div');
    messageElement.className = `message-${message.type}`;
    
    // Add disabled attribute if message is disabled
    if (message.disabled) {
        messageElement.dataset.disabled = 'true';
        messageElement.style.opacity = '0.5';
        messageElement.style.pointerEvents = 'none';
    }
    
    // Add message_id as data attribute for both user and assistant messages (needed for editing)
    // Fix: Ensure we're using the correct message ID field for both message types
    if ((message.type === 'user' || message.type === 'assistant') && message.id) {
        messageElement.dataset.messageId = message.id;
        console.log(`Setting message ID for ${message.type} message:`, message.id);
    } else if ((message.type === 'user' || message.type === 'assistant') && message.message_id) {
        // Fallback to message_id if id is not available
        messageElement.dataset.messageId = message.message_id;
        console.log(`Setting message_id for ${message.type} message:`, message.message_id);
    } else if (message.type === 'user' || message.type === 'assistant') {
        console.warn('Message missing ID:', message);
    }
    
    // Format timestamp
    const timestamp = new Date(message.created_at).toLocaleTimeString('fa-IR');
    
    // Create message content with metadata
    let messageContent = message.content;
    
    // Render Markdown for both user and assistant messages
    if (message.type === 'assistant' || message.type === 'user') {
        try {
            messageContent = md.render(message.content);
        } catch (e) {
            console.error('Error rendering markdown:', e);
            // Show error message in Persian
            if (e.message && e.message.includes('code')) {
                messageContent = '<div class="alert alert-warning">خطا: فرمت کد ارسال شده شناسایی نشد یا بلوک کد معتبر نیست.</div>' + md.utils.escapeHtml(message.content);
            } else {
                // Fallback to plain text if markdown rendering fails
                messageContent = md.utils.escapeHtml(message.content);
            }
        }
    }
    
    // Add AI model information for assistant messages
    let modelInfo = '';
    if (message.type === 'assistant' && currentSessionId) {
        // Get session info to display AI model name
        const sessionData = JSON.parse(localStorage.getItem(`session_${currentSessionId}`) || '{}');
        if (sessionData.ai_model_name) {
            modelInfo = `<div class="model-info">مدل: ${sessionData.ai_model_name}</div>`;
        }
    }
    
    // Add image display if image_url is present
    let imageContent = '';
    if (message.image_url) {
        // Split image URLs by comma in case there are multiple images
        const imageUrls = message.image_url.split(',');
        imageUrls.forEach(url => {
            if (url.trim()) {
                // Handle both absolute URLs and relative paths
                let imageUrl = url.trim();
                // If it's a relative path, prepend the media URL
                if (!imageUrl.startsWith('http') && !imageUrl.startsWith('/media/')) {
                    imageUrl = '/media/' + imageUrl;
                }
                // If it already starts with /media/, make sure it's properly formatted
                else if (imageUrl.startsWith('/media/')) {
                    // It's already correctly formatted
                }
                // If it's already an absolute URL, leave it as is
                imageContent += `<div class="image-container mt-2">
                    <img src="${imageUrl}" alt="Generated image" class="img-fluid rounded" style="max-width: 100%; height: auto;">
                    <div class="mt-1">
                        <a href="${imageUrl}" download class="btn btn-sm btn-outline-primary">
                            <i class="fas fa-download"></i> دانلود تصویر
                        </a>
                    </div>
                </div>`;
            }
        });
    }
    
    // Add uploaded files display if files are present in message data
    let fileContent = '';
    if (message.type === 'user' && message.uploaded_files && message.uploaded_files.length > 0) {
        fileContent = '<div class="files-container mt-2">';
        fileContent += '<div class="uploaded-files-header"><small class="text-muted"><i class="fas fa-paperclip"></i> فایل‌های آپلود شده:</small></div>';
        
        message.uploaded_files.forEach((file, index) => {
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
            
            fileContent += `
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
        });
        
        fileContent += '</div>';
    } else if (message.type === 'user') {
        // Fallback: Extract file information from message content (legacy support)
        const fileMatches = message.content.match(/\((فایل|تصویر|فایل متنی|فایل PDF|فایل اداری|فایل فشرده): ([^)]+)\)/g);
        if (fileMatches) {
            fileContent = '<div class="files-container mt-2"></div>';
        }
    }
    
    let content = `
        <div class="message-header">
            <strong>${message.type === 'user' ? 'شما' : 'دستیار'}</strong>
            <small class="text-muted float-end">${timestamp}</small>
        </div>
        <div class="message-content">${messageContent}</div>
        ${imageContent}
        ${fileContent}
        ${modelInfo}
        <div class="message-actions mt-2">
            <button class="btn btn-sm btn-outline-secondary copy-btn" title="کپی">
                <i class="fas fa-copy"></i> کپی
            </button>
            <button class="btn btn-sm btn-outline-primary share-btn" title="اشتراک‌گذاری">
                <i class="fas fa-share"></i> اشتراک
            </button>
        </div>
    `;
    
    messageElement.innerHTML = content;
    chatContainer.appendChild(messageElement);
    
    // Apply syntax highlighting to code blocks
    if (message.type === 'assistant' && hljs) {
        const codeBlocks = messageElement.querySelectorAll('pre code');
        codeBlocks.forEach(block => {
            try {
                // اطمینان از اینکه محتوا escape شده است
                if (block.innerHTML && block.innerHTML.includes('<') && !block.innerHTML.includes('&lt;')) {
                    block.innerHTML = block.innerHTML.replace(/</g, '&lt;').replace(/>/g, '&gt;');
                }
                hljs.highlightElement(block);
            } catch (e) {
                console.warn('Syntax highlighting failed for block:', e);
            }
        });
    }
    
    // Add copy buttons to code blocks and quotes
    addCopyButtonsToContent(messageElement);
    
    // If this is a user message with files, set up file functionality
    if (message.type === 'user' && messageElement.querySelector('.files-container')) {
        if (message.uploaded_files && message.uploaded_files.length > 0) {
            // Set up image preview functionality for uploaded files
            setupImagePreviewButtons(messageElement);
        } else {
            // Fallback: display files from message content (legacy support)
            displayFilesFromMessage(message.content, messageElement.querySelector('.files-container'));
        }
    }
    
    // Add event listener for copy button
    const copyBtn = messageElement.querySelector('.copy-btn');
    copyBtn.addEventListener('click', function() {
        // Get the raw text content, not the HTML
        const messageContent = messageElement.querySelector('.message-content').textContent;
        if (navigator.clipboard) {
            navigator.clipboard.writeText(messageContent).then(() => {
                // Show success feedback
                const originalText = copyBtn.innerHTML;
                copyBtn.innerHTML = '<i class="fas fa-check"></i> کپی شد';
                setTimeout(() => {
                    copyBtn.innerHTML = originalText;
                }, 2000);
            }).catch(err => {
                console.error('Failed to copy: ', err);
                alert('کپی موفقیت‌آمیز نبود');
            });
        } else {
            // Fallback for older browsers
            const textArea = document.createElement('textarea');
            textArea.value = messageContent;
            document.body.appendChild(textArea);
            textArea.select();
            try {
                document.execCommand('copy');
                // Show success feedback
                const originalText = copyBtn.innerHTML;
                copyBtn.innerHTML = '<i class="fas fa-check"></i> کپی شد';
                setTimeout(() => {
                    copyBtn.innerHTML = originalText;
                }, 2000);
            } catch (err) {
                console.error('Fallback: Oops, unable to copy', err);
                alert('کپی موفقیت‌آمیز نبود');
            }
            document.body.removeChild(textArea);
        }
    });
    
    // Add event listener for share button
    const shareBtn = messageElement.querySelector('.share-btn');
    shareBtn.addEventListener('click', function() {
        // Get the raw text content, not the HTML
        const messageContent = messageElement.querySelector('.message-content').textContent;
        if (navigator.share) {
            navigator.share({
                title: 'پیام از MobixAI',
                text: messageContent,
            }).catch((error) => console.log('Error sharing:', error));
        } else {
            // Fallback: copy to clipboard
            if (navigator.clipboard) {
                navigator.clipboard.writeText(messageContent).then(() => {
                    // Show success feedback
                    const originalText = shareBtn.innerHTML;
                    shareBtn.innerHTML = '<i class="fas fa-check"></i> کپی شد';
                    setTimeout(() => {
                        shareBtn.innerHTML = originalText;
                    }, 2000);
                }).catch(err => {
                    console.error('Failed to copy: ', err);
                    alert('اشتراک‌گذاری موفقیت‌آمیز نبود');
                });
            } else {
                // Fallback for older browsers
                const textArea = document.createElement('textarea');
                textArea.value = messageContent;
                document.body.appendChild(textArea);
                textArea.select();
                try {
                    document.execCommand('copy');
                    // Show success feedback
                    const originalText = shareBtn.innerHTML;
                    shareBtn.innerHTML = '<i class="fas fa-check"></i> کپی شد';
                    setTimeout(() => {
                        shareBtn.innerHTML = originalText;
                    }, 2000);
                } catch (err) {
                    console.error('Fallback: Oops, unable to copy', err);
                    alert('اشتراک‌گذاری موفقیت‌آمیز نبود');
                }
                document.body.removeChild(textArea);
            }
        }
    });
    
    // Scroll to bottom with enhanced reliability
    scrollToBottom();
}

// Function to extract and display files from a message
function displayFilesFromMessage(messageContent, container) {
    // Extract file information from message content
    const fileRegex = /\((فایل|تصویر|فایل متنی|فایل PDF|فایل اداری|فایل فشرده): ([^)]+)\)/g;
    let match;
    const files = [];
    
    while ((match = fileRegex.exec(messageContent)) !== null) {
        files.push({
            type: match[1],
            name: match[2]
        });
    }
    
    // If files were found, create file previews
    if (files.length > 0) {
        let filesHtml = '<div class="file-previews">';
        files.forEach(file => {
            // Determine file icon based on type
            let iconClass = 'fas fa-file';
            if (file.type === 'تصویر') {
                iconClass = 'fas fa-file-image text-primary';
            } else if (file.type === 'فایل PDF') {
                iconClass = 'fas fa-file-pdf text-danger';
            } else if (file.type === 'فایل متنی') {
                iconClass = 'fas fa-file-alt text-info';
            } else if (file.type === 'فایل اداری') {
                iconClass = 'fas fa-file-word text-primary';
            } else if (file.type === 'فایل فشرده') {
                iconClass = 'fas fa-file-archive text-secondary';
            }
            
            filesHtml += `
                <div class="file-preview-item p-2 mb-2 border rounded">
                    <div class="d-flex align-items-center">
                        <i class="${iconClass} me-2"></i>
                        <div class="flex-grow-1">
                            <div class="fw-bold">${file.name}</div>
                            <div class="small text-muted">${file.type}</div>
                        </div>
                        <button class="btn btn-sm btn-outline-primary download-btn" data-filename="${file.name}">
                            <i class="fas fa-download"></i> دانلود
                        </button>
                    </div>
                </div>
            `;
        });
        filesHtml += '</div>';
        
        container.innerHTML = filesHtml;
        
        // Add event listeners for download buttons
        const downloadButtons = container.querySelectorAll('.download-btn');
        downloadButtons.forEach(button => {
            button.addEventListener('click', function() {
                const filename = this.getAttribute('data-filename');
                // In a real implementation, we would need to know the session ID and file ID
                // to construct the proper download URL
                alert(`دانلود فایل: ${filename}\nدر یک پیاده‌سازی کامل، اینجا فایل دانلود می‌شود.`);
            });
        });
    }
}

// Function to fetch and display files for a session
function fetchSessionFiles(sessionId, container) {
    fetch(`/chat/session/${sessionId}/files/`)
        .then(response => response.json())
        .then(data => {
            if (data.files && data.files.length > 0) {
                // Create file previews
                let filesHtml = '<div class="file-previews mt-2">';
                data.files.forEach(file => {
                    // Determine file icon based on mimetype
                    let iconClass = 'fas fa-file';
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
                    let sizeText;
                    if (file.size < 1024) {
                        sizeText = `${file.size} bytes`;
                    } else if (file.size < 1024 * 1024) {
                        sizeText = `${Math.round(file.size / 1024 * 100) / 100} KB`;
                    } else {
                        sizeText = `${Math.round(file.size / (1024 * 1024) * 100) / 100} MB`;
                    }
                    
                    filesHtml += `
                        <div class="file-preview-item p-2 mb-2 border rounded">
                            <div class="d-flex align-items-center">
                                <i class="${iconClass} me-2"></i>
                                <div class="flex-grow-1">
                                    <div class="fw-bold">${file.filename}</div>
                                    <div class="small text-muted">${sizeText}</div>
                                </div>
                                <a href="${file.download_url}" download="${file.filename}" class="btn btn-sm btn-outline-primary">
                                    <i class="fas fa-download"></i> دانلود
                                </a>
                            </div>
                        </div>
                    `;
                });
                filesHtml += '</div>';
                
                container.innerHTML = filesHtml;
            }
        })
        .catch(error => {
            console.error('Error fetching session files:', error);
        });
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

// Show typing indicator
function showTypingIndicator() {
    const chatContainer = document.getElementById('chat-container');
    const welcomeMessage = document.getElementById('welcome-message');
    if (welcomeMessage) {
        welcomeMessage.remove();
    }
    
    const typingElement = document.createElement('div');
    typingElement.className = 'typing-indicator';
    typingElement.id = 'typing-indicator';
    typingElement.innerHTML = `
        <span></span><span></span><span></span>
        <div class="waiting-message" style="margin-right: 10px; font-size: 14px; color: #6c757d;">
            در حال تولید پاسخ...
        </div>
    `;
    chatContainer.appendChild(typingElement);
    
    // Ensure scroll to bottom with enhanced reliability
    scrollToBottom();
}

// Hide typing indicator
function hideTypingIndicator() {
    const typingElement = document.getElementById('typing-indicator');
    if (typingElement) {
        typingElement.remove();
    }
}

// Update or add assistant message for streaming
// Global variable to store assistant message ID from server
let currentAssistantMessageId = null;

function updateOrAddAssistantMessage(content, messageId = null) {
    const chatContainer = document.getElementById('chat-container');
    let assistantElement = document.getElementById('streaming-assistant');
    
    // Store the message ID if provided
    if (messageId) {
        currentAssistantMessageId = messageId;
    }
    
    if (!assistantElement) {
        // Create new assistant message element with same structure as addMessageToChat
        assistantElement = document.createElement('div');
        assistantElement.className = 'message-assistant';
        assistantElement.id = 'streaming-assistant';
        
        // Add message ID if we have it
        if (currentAssistantMessageId) {
            assistantElement.dataset.messageId = currentAssistantMessageId;
            console.log('Setting assistant message ID:', currentAssistantMessageId);
        }
        
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
    if (isUserAtBottom()) {
        scrollToBottom();
    }
}

// Function to simulate typing effect
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

// Function to format file sizes
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Function to set up image preview buttons
function setupImagePreviewButtons(messageElement) {
    const previewButtons = messageElement.querySelectorAll('.preview-image-btn');
    previewButtons.forEach(button => {
        button.addEventListener('click', function() {
            const imageUrl = this.getAttribute('data-image-url');
            showImagePreview(imageUrl);
        });
    });
}

// Function to show image preview in a modal
function showImagePreview(imageUrl) {
    // Create modal HTML
    const modalHtml = `
        <div class="modal fade" id="imagePreviewModal" tabindex="-1" aria-labelledby="imagePreviewModalLabel" aria-hidden="true">
            <div class="modal-dialog modal-lg modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title" id="imagePreviewModalLabel">
                            <i class="fas fa-image"></i> پیش‌نمایش تصویر
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body text-center">
                        <img src="${imageUrl}" alt="Preview" class="img-fluid rounded" style="max-width: 100%; max-height: 70vh;">
                    </div>
                    <div class="modal-footer">
                        <a href="${imageUrl}" download class="btn btn-primary">
                            <i class="fas fa-download"></i> دانلود تصویر
                        </a>
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                            <i class="fas fa-times"></i> بستن
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Remove existing modal if it exists
    const existingModal = document.getElementById('imagePreviewModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    // Add modal to body
    const modalContainer = document.createElement('div');
    modalContainer.innerHTML = modalHtml;
    document.body.appendChild(modalContainer);
    
    // Show modal
    const imageModal = new bootstrap.Modal(document.getElementById('imagePreviewModal'));
    imageModal.show();
    
    // Remove modal from DOM when hidden
    document.getElementById('imagePreviewModal').addEventListener('hidden.bs.modal', function () {
        modalContainer.remove();
    });
}

// Update the streaming handler to handle images
function updateOrAddAssistantMessageWithImages(content, imagesData = null, messageId = null) {
    const chatContainer = document.getElementById('chat-container');
    let assistantElement = document.getElementById('streaming-assistant');
    
    // Store the message ID if provided
    if (messageId) {
        currentAssistantMessageId = messageId;
    }
    
    if (!assistantElement) {
        // Create new assistant message element with same structure as addMessageToChat
        assistantElement = document.createElement('div');
        assistantElement.className = 'message-assistant';
        assistantElement.id = 'streaming-assistant';
        
        // Add message ID if we have it
        if (currentAssistantMessageId) {
            assistantElement.dataset.messageId = currentAssistantMessageId;
            console.log('Setting assistant message ID for images:', currentAssistantMessageId);
        }
        
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
            imagesData.forEach(img => {
                if (img.image_url && img.image_url.url) {
                    // Handle both absolute URLs and relative paths
                    let imageUrl = img.image_url.url;
                    // If it's a relative path, prepend the media URL
                    if (!imageUrl.startsWith('http') && !imageUrl.startsWith('/media/')) {
                        imageUrl = '/media/' + imageUrl;
                    }
                    imageContent += `<div class="image-container mt-2">
                        <img src="${imageUrl}" alt="Generated image" class="img-fluid rounded" style="max-width: 100%; height: auto;">
                        <div class="mt-1">
                            <a href="${imageUrl}" download class="btn btn-sm btn-outline-primary">
                                <i class="fas fa-download"></i> دانلود تصویر
                            </a>
                        </div>
                    </div>`;
                }
            });
            
            if (imageContent) {
                // Add the image content
                assistantElement.insertAdjacentHTML('beforeend', imageContent);
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

// Function to send message to the server
function sendMessage() {
    // Get form elements
    const messageInput = document.getElementById('message-input');
    const sendButton = document.getElementById('send-button');
    const fileInput = document.getElementById('file-input');
    
    // Get message content
    const messageContent = messageInput.value.trim();
    
    // Check if we have a session
    if (!currentSessionId) {
        alert('لطفاً ابتدا یک چت جدید ایجاد کنید');
        return;
    }
    
    // Validate input
    if (!messageContent && (!fileInput.files || fileInput.files.length === 0)) {
        alert('لطفاً یک پیام یا فایل وارد کنید');
        return;
    }
    
    // Disable send button and show loading state
    sendButton.disabled = true;
    const sendIcon = sendButton.querySelector('.send-icon');
    const stopIcon = sendButton.querySelector('.stop-icon');
    if (sendIcon) sendIcon.style.display = 'none';
    if (stopIcon) stopIcon.style.display = 'inline';
    
    // Show typing indicator
    showTypingIndicator();
    
    // Prepare form data
    const formData = new FormData();
    formData.append('message', messageContent);
    
    // Add files if any
    if (fileInput.files && fileInput.files.length > 0) {
        for (let i = 0; i < fileInput.files.length; i++) {
            formData.append('files', fileInput.files[i]);
        }
    }
    
    // Check if web search is enabled
    const webSearchBtn = document.getElementById('web-search-btn');
    if (webSearchBtn && webSearchBtn.classList.contains('btn-success')) {
        formData.append('web_search', 'true');
    }
    
    // Check if image generation is enabled
    const imageGenerationBtn = document.getElementById('image-generation-btn');
    if (imageGenerationBtn && imageGenerationBtn.classList.contains('btn-success')) {
        formData.append('image_generation', 'true');
    }
    
    // Send message to server using fetch API
    fetch(`/chat/session/${currentSessionId}/send/`, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response;
    })
    .then(response => {
        // Handle streaming response
        const reader = response.body.getReader();
        const decoder = new TextDecoder('utf-8');
        let assistantMessage = '';
        let assistantMessageId = null;
        let isFirstChunk = true;
        
        function read() {
            reader.read().then(({done, value}) => {
                if (done) {
                    // Stream finished
                    hideTypingIndicator();
                    
                    // Reset send button
                    sendButton.disabled = false;
                    if (sendIcon) sendIcon.style.display = 'inline';
                    if (stopIcon) stopIcon.style.display = 'none';
                    
                    // Clear input
                    messageInput.value = '';
                    
                    // Reset file input
                    fileInput.value = '';
                    const filesPreview = document.getElementById('files-preview');
                    if (filesPreview) {
                        filesPreview.style.display = 'none';
                        document.getElementById('files-list').innerHTML = '';
                        document.getElementById('files-count').textContent = '0';
                    }
                    
                    // Scroll to bottom
                    scrollToBottom();
                    return;
                }
                
                // Process chunk
                const chunk = decoder.decode(value, {stream: true});
                const lines = chunk.split('\n');
                
                lines.forEach(line => {
                    if (line.startsWith('data: ')) {
                        const data = line.substring(6);
                        if (data === '[DONE]') {
                            // Stream finished
                            hideTypingIndicator();
                            
                            // Reset send button
                            sendButton.disabled = false;
                            if (sendIcon) sendIcon.style.display = 'inline';
                            if (stopIcon) stopIcon.style.display = 'none';
                            
                            // Clear input
                            messageInput.value = '';
                            
                            // Reset file input
                            fileInput.value = '';
                            const filesPreview = document.getElementById('files-preview');
                            if (filesPreview) {
                                filesPreview.style.display = 'none';
                                document.getElementById('files-list').innerHTML = '';
                                document.getElementById('files-count').textContent = '0';
                            }
                            
                            // Scroll to bottom
                            scrollToBottom();
                        } else {
                            try {
                                const jsonData = JSON.parse(data);
                                if (jsonData.error) {
                                    // Handle error
                                    hideTypingIndicator();
                                    alert('خطا: ' + jsonData.error);
                                    
                                    // Reset send button
                                    sendButton.disabled = false;
                                    if (sendIcon) sendIcon.style.display = 'inline';
                                    if (stopIcon) stopIcon.style.display = 'none';
                                } else if (jsonData.message_id) {
                                    // Store message ID for the first chunk
                                    if (isFirstChunk) {
                                        assistantMessageId = jsonData.message_id;
                                        isFirstChunk = false;
                                    }
                                    
                                    // Update assistant message
                                    assistantMessage += jsonData.content;
                                    updateOrAddAssistantMessage(assistantMessage, assistantMessageId);
                                }
                            } catch (e) {
                                console.error('Error parsing JSON:', e);
                            }
                        }
                    }
                });
                
                // Continue reading
                read();
            }).catch(error => {
                console.error('Error reading stream:', error);
                hideTypingIndicator();
                alert('خطا در دریافت پاسخ: ' + error.message);
                
                // Reset send button
                sendButton.disabled = false;
                if (sendIcon) sendIcon.style.display = 'inline';
                if (stopIcon) stopIcon.style.display = 'none';
            });
        }
        
        // Start reading the stream
        read();
    })
    .catch(error => {
        console.error('Error sending message:', error);
        hideTypingIndicator();
        alert('خطا در ارسال پیام: ' + error.message);
        
        // Reset send button
        sendButton.disabled = false;
        if (sendIcon) sendIcon.style.display = 'inline';
        if (stopIcon) stopIcon.style.display = 'none';
    });
}
