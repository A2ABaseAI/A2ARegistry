// Shopify Status Agent - Frontend JavaScript

class ChatApp {
    constructor() {
        this.sessionId = null;
        this.isConnected = false;
        this.isTyping = false;
        
        this.initializeElements();
        this.attachEventListeners();
        this.updateConnectionStatus('disconnected');
    }
    
    initializeElements() {
        this.messageInput = document.getElementById('message-input');
        this.sendButton = document.getElementById('send-button');
        this.chatMessages = document.getElementById('chat-messages');
        this.connectionStatus = document.getElementById('connection-status');
        this.sessionInfo = document.getElementById('session-info');
    }
    
    attachEventListeners() {
        this.sendButton.addEventListener('click', () => this.sendMessage());
        this.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // Auto-focus input
        this.messageInput.focus();
    }
    
    async sendMessage() {
        const message = this.messageInput.value.trim();
        if (!message) return;
        
        // Disable input while processing
        this.setInputState(false);
        
        // Add user message to chat
        this.addMessage('user', message);
        
        // Clear input
        this.messageInput.value = '';
        
        // Show typing indicator
        this.showTypingIndicator();
        
        try {
            // Send message to server
            await this.sendToServer(message);
        } catch (error) {
            console.error('Error sending message:', error);
            this.addMessage('assistant', 'Sorry, I encountered an error. Please try again.');
            this.updateConnectionStatus('disconnected');
        } finally {
            this.hideTypingIndicator();
            this.setInputState(true);
        }
    }
    
    async sendToServer(message) {
        const response = await fetch('/api/chat/stream', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                session_id: this.sessionId
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        this.updateConnectionStatus('connected');
        
        // Handle streaming response
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let assistantMessage = '';
        let messageElement = null;
        
        try {
            while (true) {
                const { done, value } = await reader.read();
                if (done) break;
                
                const chunk = decoder.decode(value);
                const lines = chunk.split('\n');
                
                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        const data = line.slice(6);
                        
                        if (data === '[DONE]') {
                            this.hideTypingIndicator();
                            return;
                        }
                        
                        try {
                            const parsed = JSON.parse(data);
                            await this.handleStreamChunk(parsed, messageElement);
                            
                            if (parsed.type === 'content' && !messageElement) {
                                messageElement = this.addMessage('assistant', '');
                            }
                            
                            if (parsed.session_id && !this.sessionId) {
                                this.sessionId = parsed.session_id;
                                this.updateSessionInfo();
                            }
                            
                        } catch (e) {
                            console.warn('Failed to parse SSE data:', data);
                        }
                    }
                }
            }
        } finally {
            reader.releaseLock();
        }
    }
    
    async handleStreamChunk(chunk, messageElement) {
        switch (chunk.type) {
            case 'content':
                if (messageElement) {
                    const contentElement = messageElement.querySelector('.message-content');
                    contentElement.textContent += chunk.content;
                    this.scrollToBottom();
                }
                break;
                
            case 'tool_call':
                this.addToolCall(chunk.tool, chunk.result);
                break;
                
            case 'order_info':
                if (chunk.order_info) {
                    this.addOrderInfo(chunk.order_info);
                }
                break;
                
            case 'error':
                this.addMessage('assistant', `Error: ${chunk.content}`);
                break;
        }
    }
    
    addMessage(sender, content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        contentDiv.textContent = content;
        
        messageDiv.appendChild(contentDiv);
        this.chatMessages.appendChild(messageDiv);
        
        this.scrollToBottom();
        return messageDiv;
    }
    
    addToolCall(toolName, result) {
        const toolDiv = document.createElement('div');
        toolDiv.className = 'tool-call';
        toolDiv.innerHTML = `
            <strong>🔧 ${toolName}:</strong> ${result}
        `;
        this.chatMessages.appendChild(toolDiv);
        this.scrollToBottom();
    }
    
    addOrderInfo(orderInfo) {
        const orderDiv = document.createElement('div');
        orderDiv.className = 'order-info';
        
        let html = '<h4>📦 Order Information</h4>';
        if (orderInfo.order_number) {
            html += `<p><strong>Order:</strong> ${orderInfo.order_number}</p>`;
        }
        if (orderInfo.status) {
            html += `<p><strong>Status:</strong> ${orderInfo.status}</p>`;
        }
        if (orderInfo.financial_status) {
            html += `<p><strong>Payment:</strong> ${orderInfo.financial_status}</p>`;
        }
        if (orderInfo.tracking_number) {
            html += `<p><strong>Tracking:</strong> ${orderInfo.tracking_number}</p>`;
        }
        
        orderDiv.innerHTML = html;
        this.chatMessages.appendChild(orderDiv);
        this.scrollToBottom();
    }
    
    showTypingIndicator() {
        if (this.isTyping) return;
        
        this.isTyping = true;
        const typingDiv = document.createElement('div');
        typingDiv.className = 'typing-indicator';
        typingDiv.id = 'typing-indicator';
        typingDiv.innerHTML = `
            <span>Assistant is typing</span>
            <div class="typing-dots">
                <span></span>
                <span></span>
                <span></span>
            </div>
        `;
        
        this.chatMessages.appendChild(typingDiv);
        this.scrollToBottom();
    }
    
    hideTypingIndicator() {
        const typingIndicator = document.getElementById('typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
        this.isTyping = false;
    }
    
    setInputState(enabled) {
        this.messageInput.disabled = !enabled;
        this.sendButton.disabled = !enabled;
        
        if (enabled) {
            this.messageInput.focus();
        }
    }
    
    updateConnectionStatus(status) {
        this.connectionStatus.className = `status-indicator ${status}`;
        this.isConnected = status === 'connected';
    }
    
    updateSessionInfo() {
        if (this.sessionId) {
            this.sessionInfo.textContent = `Session: ${this.sessionId.substring(0, 8)}...`;
        }
    }
    
    scrollToBottom() {
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }
}

// Initialize the chat app when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new ChatApp();
});
