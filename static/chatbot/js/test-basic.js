// Test basic JavaScript loading
console.log('=== TEST BASIC JS LOADED ===');

// Test if we can access basic DOM elements
document.addEventListener('DOMContentLoaded', function() {
    console.log('=== DOM LOADED ===');
    
    // Test message input access
    const messageInput = document.getElementById('message-input');
    console.log('Message input found:', !!messageInput);
    
    // Test send button access
    const sendButton = document.getElementById('send-button');
    console.log('Send button found:', !!sendButton);
    
    // Test chat container access
    const chatContainer = document.getElementById('chat-container');
    console.log('Chat container found:', !!chatContainer);
    
    // Add click event to send button for testing
    if (sendButton) {
        sendButton.addEventListener('click', function(e) {
            e.preventDefault();
            console.log('=== SEND BUTTON CLICKED ===');
            
            if (messageInput) {
                const message = messageInput.value;
                console.log('Message value:', message);
                
                if (message.trim()) {
                    // Simple test: add a test message to chat container
                    if (chatContainer) {
                        const testDiv = document.createElement('div');
                        testDiv.innerHTML = `
                            <div class="message-assistant">
                                <div class="message-header">
                                    <strong>تست</strong>
                                    <small class="text-muted float-end">${new Date().toLocaleTimeString('fa-IR')}</small>
                                </div>
                                <div class="message-content">این یک پیام تست است: ${message}</div>
                            </div>
                        `;
                        chatContainer.appendChild(testDiv);
                        messageInput.value = '';
                        console.log('Test message added to chat');
                    }
                }
            }
        });
    }
});