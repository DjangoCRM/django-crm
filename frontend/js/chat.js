// Chat functionality for Django CRM
class ChatManager {
    constructor(app) {
        this.app = app;
        this.currentMessages = [];
        this.currentContentType = null;
        this.currentObjectId = null;
        this.pollInterval = null;
        this.unreadCount = 0;
        this.lastMessageId = null;
        this.isTyping = false;
        this.typingTimeout = null;
    }

    /**
     * Load chat interface for a specific object
     * @param {string} contentType - The content type model name (e.g., 'deal', 'task', 'contact')
     * @param {number} objectId - The ID of the object
     */
    async loadChat(contentType, objectId) {
        this.currentContentType = contentType;
        this.currentObjectId = objectId;

        const chatContainer = document.getElementById('chat-container');
        if (!chatContainer) {
            console.error('Chat container not found');
            return;
        }

        chatContainer.innerHTML = `
            <div class="bg-white rounded-lg shadow-lg h-full flex flex-col dark:bg-slate-800">
                <!-- Header -->
                <div class="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
                    <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
                        <svg class="w-5 h-5 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"></path>
                        </svg>
                        Chat
                    </h3>
                    <button class="btn-icon btn-text" onclick="app.chat.closeChat()" title="Close">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                        </svg>
                    </button>
                </div>

                <!-- Messages -->
                <div id="chat-messages" class="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50 dark:bg-slate-900">
                    <div class="text-center py-8">
                        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500 mx-auto"></div>
                        <p class="text-gray-500 mt-2">Loading messages...</p>
                    </div>
                </div>

                <!-- Input -->
                <div class="p-4 border-t border-gray-200 dark:border-gray-700">
                    <form id="chat-form" class="flex gap-2">
                        <textarea id="chat-input" 
                                  rows="1" 
                                  class="input flex-1 resize-none" 
                                  placeholder="Type a message..."
                                  onkeydown="if(event.key==='Enter' && !event.shiftKey){event.preventDefault();document.getElementById('chat-form').dispatchEvent(new Event('submit'));}"></textarea>
                        <button type="submit" class="btn btn-primary">
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"></path>
                            </svg>
                        </button>
                    </form>
                </div>
            </div>
        `;

        // Load messages
        await this.loadMessages();

        // Setup form submission
        const chatForm = document.getElementById('chat-form');
        chatForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.sendMessage();
        });

        // Auto-resize textarea
        const chatInput = document.getElementById('chat-input');
        chatInput.addEventListener('input', () => {
            chatInput.style.height = 'auto';
            chatInput.style.height = Math.min(chatInput.scrollHeight, 120) + 'px';
        });

        // Start polling for new messages
        this.startPolling();
    }

    async loadMessages() {
        const messagesContainer = document.getElementById('chat-messages');
        if (!messagesContainer) return;

        try {
            // Get content type ID
            const contentTypeId = await this.getContentTypeId(this.currentContentType);
            
            const params = new URLSearchParams({
                content_type: contentTypeId,
                object_id: this.currentObjectId,
                ordering: 'creation_date'
            });

            const url = `${window.CRM_CONFIG.ENDPOINTS.CHAT_MESSAGES}?${params.toString()}`;
            const response = await window.apiClient.get(url);
            
            this.currentMessages = response.results || [];

            if (this.currentMessages.length === 0) {
                messagesContainer.innerHTML = `
                    <div class="text-center py-8">
                        <div class="text-4xl mb-2">💬</div>
                        <p class="text-gray-500">No messages yet. Start the conversation!</p>
                    </div>
                `;
                return;
            }

            messagesContainer.innerHTML = this.currentMessages.map(msg => this.renderMessage(msg)).join('');
            
            // Scroll to bottom
            messagesContainer.scrollTop = messagesContainer.scrollHeight;

        } catch (error) {
            console.error('Failed to load messages:', error);
            messagesContainer.innerHTML = `
                <div class="text-center py-8">
                    <div class="text-4xl mb-2">⚠️</div>
                    <p class="text-red-600 mb-2">Failed to load messages</p>
                    <button onclick="app.chat.loadMessages()" class="btn btn-sm btn-primary">Retry</button>
                </div>
            `;
        }
    }

    renderMessage(message, showAvatar = true) {
        const isOwn = message.owner === this.app.currentUser?.id;
        const timestamp = new Date(message.creation_date).toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit'
        });
        
        const date = new Date(message.creation_date).toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric'
        });
        
        const initials = this.getInitials(message.owner_name || 'U');
        
        // Check if message is new (for notification)
        const isNew = this.lastMessageId && message.id > this.lastMessageId;

        return `
            <div class="flex gap-3 ${isOwn ? 'flex-row-reverse' : 'flex-row'} ${isNew ? 'animate-fade-in' : ''}" data-message-id="${message.id}">
                ${showAvatar ? `
                    <div class="flex-shrink-0">
                        <div class="w-8 h-8 rounded-full ${isOwn ? 'bg-primary-500' : 'bg-gray-500'} flex items-center justify-center text-white text-xs font-bold">
                            ${initials}
                        </div>
                    </div>
                ` : `<div class="w-8"></div>`}
                
                <div class="flex-1 max-w-[70%]">
                    <div class="flex items-center gap-2 mb-1 ${isOwn ? 'justify-end' : 'justify-start'}">
                        ${showAvatar ? `
                            <span class="text-xs font-semibold text-gray-700 dark:text-gray-300">
                                ${this.escapeHtml(message.owner_name || 'Unknown')}
                            </span>
                        ` : ''}
                        <span class="text-xs text-gray-500">${timestamp}</span>
                        ${isNew ? '<span class="text-xs text-primary-500 font-semibold">New</span>' : ''}
                    </div>
                    
                    <div class="group relative">
                        <div class="rounded-lg p-3 ${isOwn 
                            ? 'bg-primary-500 text-white rounded-tr-none' 
                            : 'bg-white dark:bg-slate-700 text-gray-900 dark:text-white border border-gray-200 dark:border-gray-600 rounded-tl-none'}">
                            <p class="text-sm whitespace-pre-wrap break-words">${this.formatContent(message.content)}</p>
                        </div>
                        
                        <!-- Message actions -->
                        <div class="absolute ${isOwn ? 'left-0' : 'right-0'} top-0 hidden group-hover:flex gap-1 -translate-y-8">
                            ${message.answer_to ? `
                                <button onclick="app.chat.scrollToMessage(${message.answer_to})" 
                                        class="p-1 bg-white dark:bg-slate-700 rounded shadow-sm hover:bg-gray-100 dark:hover:bg-slate-600" 
                                        title="Go to replied message">
                                    <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h10a8 8 0 018 8v2M3 10l6 6m-6-6l6-6"></path>
                                    </svg>
                                </button>
                            ` : ''}
                            <button onclick="app.chat.replyToMessage(${message.id}, '${this.escapeHtml(message.owner_name)}')" 
                                    class="p-1 bg-white dark:bg-slate-700 rounded shadow-sm hover:bg-gray-100 dark:hover:bg-slate-600" 
                                    title="Reply">
                                <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h10a8 8 0 018 8v2M3 10l6 6m-6-6l6-6"></path>
                                </svg>
                            </button>
                            ${isOwn ? `
                                <button onclick="app.chat.editMessage(${message.id})" 
                                        class="p-1 bg-white dark:bg-slate-700 rounded shadow-sm hover:bg-gray-100 dark:hover:bg-slate-600" 
                                        title="Edit">
                                    <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
                                    </svg>
                                </button>
                                <button onclick="app.chat.deleteMessage(${message.id})" 
                                        class="p-1 bg-white dark:bg-slate-700 rounded shadow-sm hover:bg-red-100 dark:hover:bg-red-900 text-red-600" 
                                        title="Delete">
                                    <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                                    </svg>
                                </button>
                            ` : ''}
                            <button onclick="app.chat.reactToMessage(${message.id})" 
                                    class="p-1 bg-white dark:bg-slate-700 rounded shadow-sm hover:bg-gray-100 dark:hover:bg-slate-600" 
                                    title="React">
                                😊
                            </button>
                        </div>
                    </div>
                    
                    ${message.answer_to ? `
                        <div class="text-xs text-gray-500 mt-1 italic">
                            Replying to ${message.answer_to_owner || 'someone'}
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
    }
    
    getInitials(name) {
        if (!name) return '?';
        const parts = name.split(' ');
        if (parts.length >= 2) {
            return (parts[0][0] + parts[1][0]).toUpperCase();
        }
        return name.substring(0, 2).toUpperCase();
    }
    
    formatContent(content) {
        if (!content) return '';
        
        // Escape HTML first
        let formatted = this.escapeHtml(content);
        
        // Convert markdown-style formatting
        // Bold: **text** or __text__
        formatted = formatted.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
        formatted = formatted.replace(/__(.+?)__/g, '<strong>$1</strong>');
        
        // Italic: *text* or _text_
        formatted = formatted.replace(/\*(.+?)\*/g, '<em>$1</em>');
        formatted = formatted.replace(/_(.+?)_/g, '<em>$1</em>');
        
        // Code: `code`
        formatted = formatted.replace(/`(.+?)`/g, '<code class="bg-gray-200 dark:bg-gray-800 px-1 rounded text-xs">$1</code>');
        
        // Links: [text](url)
        formatted = formatted.replace(/\[(.+?)\]\((.+?)\)/g, '<a href="$2" target="_blank" class="underline hover:text-primary-600">$1</a>');
        
        return formatted;
    }

    async sendMessage() {
        const input = document.getElementById('chat-input');
        const content = input.value.trim();

        if (!content) return;

        try {
            const editingId = input.dataset.editingId;
            const replyToId = input.dataset.replyTo;
            
            if (editingId) {
                // Edit existing message
                await window.apiClient.patch(`${window.CRM_CONFIG.ENDPOINTS.CHAT_MESSAGES}${editingId}/`, {
                    content: content
                });
                
                this.cancelEdit();
                this.app.showToast('Message updated', 'success');
            } else {
                // Send new message
                const contentTypeId = await this.getContentTypeId(this.currentContentType);

                const data = {
                    content: content,
                    content_type: contentTypeId,
                    object_id: this.currentObjectId
                };
                
                // Add reply reference if replying
                if (replyToId) {
                    data.answer_to = parseInt(replyToId);
                }

                await window.apiClient.post(window.CRM_CONFIG.ENDPOINTS.CHAT_MESSAGES, data);
                this.cancelReply();
            }
            
            input.value = '';
            input.style.height = 'auto';
            
            // Reload messages
            const messagesContainer = document.getElementById('chat-messages');
            const wasAtBottom = messagesContainer ? 
                messagesContainer.scrollHeight - messagesContainer.scrollTop <= messagesContainer.clientHeight + 50 : true;
            
            await this.loadMessages();
            
            // Auto-scroll if was at bottom
            if (wasAtBottom && messagesContainer) {
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
            }

        } catch (error) {
            console.error('Failed to send message:', error);
            this.app.showToast('Failed to send message', 'error');
        }
    }

    async getContentTypeId(modelName) {
        // Map model names to content type IDs
        // This is a simplified approach - in production, you'd fetch this from an API
        const contentTypeMap = {
            'deal': 11,
            'task': 12,
            'project': 13,
            'contact': 14,
            'company': 15,
            'lead': 16
        };

        return contentTypeMap[modelName] || 11; // Default to deal
    }

    startPolling() {
        // Poll for new messages every 10 seconds
        this.pollInterval = setInterval(async () => {
            if (this.currentContentType && this.currentObjectId) {
                const messagesContainer = document.getElementById('chat-messages');
                if (!messagesContainer) {
                    this.stopPolling();
                    return;
                }

                const scrolledToBottom = messagesContainer.scrollHeight - messagesContainer.scrollTop <= messagesContainer.clientHeight + 50;
                
                await this.loadMessages();
                
                // Auto-scroll if user was at bottom
                if (scrolledToBottom) {
                    messagesContainer.scrollTop = messagesContainer.scrollHeight;
                }
            }
        }, 10000);
    }

    stopPolling() {
        if (this.pollInterval) {
            clearInterval(this.pollInterval);
            this.pollInterval = null;
        }
    }

    async replyToMessage(messageId, ownerName) {
        const input = document.getElementById('chat-input');
        if (!input) return;
        
        // Show reply indicator
        const form = document.getElementById('chat-form');
        const existingIndicator = document.getElementById('reply-indicator');
        if (existingIndicator) existingIndicator.remove();
        
        const indicator = document.createElement('div');
        indicator.id = 'reply-indicator';
        indicator.className = 'px-4 py-2 bg-gray-100 dark:bg-slate-700 border-t border-gray-200 dark:border-slate-600 flex items-center justify-between';
        indicator.innerHTML = `
            <div class="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-300">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h10a8 8 0 018 8v2M3 10l6 6m-6-6l6-6"></path>
                </svg>
                <span>Replying to <strong>${this.escapeHtml(ownerName)}</strong></span>
            </div>
            <button onclick="app.chat.cancelReply()" class="text-gray-400 hover:text-gray-600">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                </svg>
            </button>
        `;
        
        form.parentElement.insertBefore(indicator, form);
        input.focus();
        input.dataset.replyTo = messageId;
    }
    
    cancelReply() {
        const indicator = document.getElementById('reply-indicator');
        if (indicator) indicator.remove();
        
        const input = document.getElementById('chat-input');
        if (input) delete input.dataset.replyTo;
    }
    
    async editMessage(messageId) {
        try {
            const message = this.currentMessages.find(m => m.id === messageId);
            if (!message) return;
            
            const input = document.getElementById('chat-input');
            if (!input) return;
            
            input.value = message.content;
            input.dataset.editingId = messageId;
            input.focus();
            
            // Show edit indicator
            const form = document.getElementById('chat-form');
            const existingIndicator = document.getElementById('edit-indicator');
            if (existingIndicator) existingIndicator.remove();
            
            const indicator = document.createElement('div');
            indicator.id = 'edit-indicator';
            indicator.className = 'px-4 py-2 bg-yellow-100 dark:bg-yellow-900 border-t border-yellow-200 dark:border-yellow-700 flex items-center justify-between';
            indicator.innerHTML = `
                <div class="flex items-center gap-2 text-sm text-yellow-800 dark:text-yellow-200">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
                    </svg>
                    <span>Editing message</span>
                </div>
                <button onclick="app.chat.cancelEdit()" class="text-yellow-600 hover:text-yellow-800">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                    </svg>
                </button>
            `;
            
            form.parentElement.insertBefore(indicator, form);
        } catch (error) {
            console.error('Failed to edit message:', error);
        }
    }
    
    cancelEdit() {
        const indicator = document.getElementById('edit-indicator');
        if (indicator) indicator.remove();
        
        const input = document.getElementById('chat-input');
        if (input) {
            delete input.dataset.editingId;
            input.value = '';
        }
    }
    
    async deleteMessage(messageId) {
        if (!confirm('Are you sure you want to delete this message?')) {
            return;
        }
        
        try {
            await window.apiClient.delete(`${window.CRM_CONFIG.ENDPOINTS.CHAT_MESSAGES}${messageId}/`);
            await this.loadMessages();
            this.app.showToast('Message deleted', 'success');
        } catch (error) {
            console.error('Failed to delete message:', error);
            this.app.showToast('Failed to delete message', 'error');
        }
    }
    
    scrollToMessage(messageId) {
        const messageElement = document.querySelector(`[data-message-id="${messageId}"]`);
        if (messageElement) {
            messageElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
            messageElement.classList.add('bg-yellow-100', 'dark:bg-yellow-900');
            setTimeout(() => {
                messageElement.classList.remove('bg-yellow-100', 'dark:bg-yellow-900');
            }, 2000);
        }
    }
    
    async reactToMessage(messageId) {
        // Simple emoji picker
        const emoji = prompt('Enter emoji reaction (or use: 👍 👎 ❤️ 😊 🎉 🚀)');
        if (!emoji) return;
        
        this.app.showToast(`Reaction ${emoji} added (reactions feature coming soon)`, 'info');
        // TODO: Implement reactions in backend
    }
    
    showTypingIndicator() {
        const messagesContainer = document.getElementById('chat-messages');
        if (!messagesContainer) return;
        
        const existingIndicator = document.getElementById('typing-indicator');
        if (existingIndicator) return;
        
        const indicator = document.createElement('div');
        indicator.id = 'typing-indicator';
        indicator.className = 'flex gap-3 items-center py-2';
        indicator.innerHTML = `
            <div class="flex-shrink-0">
                <div class="w-8 h-8 rounded-full bg-gray-400 flex items-center justify-center text-white text-xs">
                    ...
                </div>
            </div>
            <div class="bg-gray-200 dark:bg-slate-700 rounded-lg px-4 py-2">
                <div class="flex gap-1">
                    <div class="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style="animation-delay: 0ms"></div>
                    <div class="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style="animation-delay: 150ms"></div>
                    <div class="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style="animation-delay: 300ms"></div>
                </div>
            </div>
        `;
        
        messagesContainer.appendChild(indicator);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
    
    hideTypingIndicator() {
        const indicator = document.getElementById('typing-indicator');
        if (indicator) indicator.remove();
    }

    closeChat() {
        this.stopPolling();
        this.cancelReply();
        this.cancelEdit();
        const chatContainer = document.getElementById('chat-container');
        if (chatContainer) {
            chatContainer.innerHTML = '';
            chatContainer.classList.add('hidden');
        }
    }

    escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}
