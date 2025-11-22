// Phone management functionality
class PhoneManager {
    constructor(app) {
        this.app = app;
        this.isConnected = false;
        this.currentCall = null;
        this.callTimer = null;
        this.recentCalls = [];
        this.init();
    }

    init() {
        this.setupKeypad();
        this.setupCallActions();
        this.loadRecentCalls();
        this.checkPhoneStatus();
    }

    setupKeypad() {
        document.querySelectorAll('.keypad-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const digit = e.target.dataset.digit;
                this.addDigit(digit);
            });
        });

        document.getElementById('clear-btn').addEventListener('click', () => {
            this.clearNumber();
        });

        document.getElementById('phone-number').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.makeCall();
            }
        });
    }

    setupCallActions() {
        document.getElementById('call-btn').addEventListener('click', () => {
            this.makeCall();
        });

        document.getElementById('hangup-btn').addEventListener('click', () => {
            this.endCall();
        });

        document.getElementById('mute-btn').addEventListener('click', () => {
            this.toggleMute();
        });

        document.getElementById('hold-btn').addEventListener('click', () => {
            this.toggleHold();
        });
    }

    addDigit(digit) {
        const phoneInput = document.getElementById('phone-number');
        phoneInput.value += digit;
        
        // Play DTMF tone if in call
        if (this.currentCall) {
            this.playDTMF(digit);
        }
    }

    clearNumber() {
        const phoneInput = document.getElementById('phone-number');
        phoneInput.value = phoneInput.value.slice(0, -1);
    }

    async makeCall() {
        const phoneNumber = document.getElementById('phone-number').value.trim();
        if (!phoneNumber) return;

        if (!this.isConnected) {
            this.app.showToast('Phone system not connected', 'error');
            return;
        }

        try {
            // Show calling state
            this.showCallingState(phoneNumber);
            
            // Simulate API call to initiate call
            const response = await this.app.apiCall('/voip/call/', {
                method: 'POST',
                body: JSON.stringify({ 
                    number: phoneNumber,
                    action: 'dial'
                })
            });

            this.startCall(phoneNumber, response);
            this.addToRecentCalls(phoneNumber, 'outbound');

        } catch (error) {
            console.error('Call failed:', error);
            this.app.showToast('Call failed: ' + error.message, 'error');
            this.resetDialer();
        }
    }

    startCall(number, callData = {}) {
        this.currentCall = {
            number: number,
            startTime: new Date(),
            isMuted: false,
            isOnHold: false,
            ...callData
        };

        // Show active call interface
        document.getElementById('phone-dialer').classList.add('hidden');
        document.getElementById('active-call').classList.remove('hidden');

        // Update call info
        document.getElementById('caller-number').textContent = number;
        
        // Try to find contact for this number
        this.findContactByNumber(number).then(contact => {
            if (contact) {
                document.getElementById('caller-name').textContent = contact.full_name;
            }
        });

        // Start call timer
        this.startCallTimer();
        
        // Update phone status
        this.updatePhoneStatus('In Call', 'text-success-600');
    }

    endCall() {
        if (!this.currentCall) return;

        try {
            // API call to end call
            this.app.apiCall('/voip/call/', {
                method: 'POST',
                body: JSON.stringify({ 
                    call_id: this.currentCall.id,
                    action: 'hangup'
                })
            }).catch(console.error);

        } catch (error) {
            console.error('Error ending call:', error);
        }

        // Stop timer
        if (this.callTimer) {
            clearInterval(this.callTimer);
            this.callTimer = null;
        }

        // Reset interface
        this.resetDialer();
        this.currentCall = null;
        
        // Update status
        this.updatePhoneStatus('Ready to call', 'text-gray-600');
        
        this.app.showToast('Call ended', 'info');
    }

    toggleMute() {
        if (!this.currentCall) return;

        this.currentCall.isMuted = !this.currentCall.isMuted;
        const muteBtn = document.getElementById('mute-btn');
        const icon = muteBtn.querySelector('i');

        if (this.currentCall.isMuted) {
            muteBtn.classList.add('bg-danger-100');
            icon.classList.remove('fa-microphone-slash');
            icon.classList.add('fa-microphone-slash', 'text-danger-600');
            this.app.showToast('Microphone muted', 'info');
        } else {
            muteBtn.classList.remove('bg-danger-100');
            icon.classList.remove('text-danger-600');
            icon.classList.add('text-gray-600');
            this.app.showToast('Microphone unmuted', 'info');
        }

        // API call to toggle mute
        this.app.apiCall('/voip/call/', {
            method: 'POST',
            body: JSON.stringify({ 
                call_id: this.currentCall.id,
                action: 'mute',
                muted: this.currentCall.isMuted
            })
        }).catch(console.error);
    }

    toggleHold() {
        if (!this.currentCall) return;

        this.currentCall.isOnHold = !this.currentCall.isOnHold;
        const holdBtn = document.getElementById('hold-btn');
        const icon = holdBtn.querySelector('i');

        if (this.currentCall.isOnHold) {
            holdBtn.classList.add('bg-warning-100');
            icon.classList.add('text-warning-600');
            this.updatePhoneStatus('On Hold', 'text-warning-600');
            this.app.showToast('Call on hold', 'info');
        } else {
            holdBtn.classList.remove('bg-warning-100');
            icon.classList.remove('text-warning-600');
            icon.classList.add('text-gray-600');
            this.updatePhoneStatus('In Call', 'text-success-600');
            this.app.showToast('Call resumed', 'info');
        }

        // API call to toggle hold
        this.app.apiCall('/voip/call/', {
            method: 'POST',
            body: JSON.stringify({ 
                call_id: this.currentCall.id,
                action: 'hold',
                on_hold: this.currentCall.isOnHold
            })
        }).catch(console.error);
    }

    startCallTimer() {
        const durationElement = document.getElementById('call-duration');
        
        this.callTimer = setInterval(() => {
            const elapsed = new Date() - this.currentCall.startTime;
            const minutes = Math.floor(elapsed / 60000);
            const seconds = Math.floor((elapsed % 60000) / 1000);
            durationElement.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        }, 1000);
    }

    showCallingState(number) {
        document.getElementById('phone-dialer').classList.add('hidden');
        document.getElementById('active-call').classList.remove('hidden');
        
        document.getElementById('caller-number').textContent = number;
        document.getElementById('caller-name').textContent = 'Calling...';
        document.getElementById('call-duration').textContent = 'Connecting...';
        
        this.updatePhoneStatus('Calling...', 'text-warning-600');
    }

    resetDialer() {
        document.getElementById('active-call').classList.add('hidden');
        document.getElementById('phone-dialer').classList.remove('hidden');
        document.getElementById('phone-number').value = '';
    }

    openDialer() {
        document.getElementById('phone-widget').classList.remove('hidden');
    }

    closeWidget() {
        if (this.currentCall) {
            // Don't close if there's an active call
            this.app.showToast('Cannot close during active call', 'warning');
            return;
        }
        document.getElementById('phone-widget').classList.add('hidden');
    }

    updatePhoneStatus(status, className = 'text-gray-600') {
        const statusElement = document.getElementById('phone-status-text');
        const headerStatus = document.getElementById('phone-status');
        
        if (statusElement) {
            statusElement.textContent = status;
            statusElement.className = `text-primary-100 text-sm ${className}`;
        }

        // Update header phone status
        if (headerStatus) {
            if (this.currentCall) {
                headerStatus.classList.remove('hidden');
                headerStatus.classList.add('flex');
                headerStatus.querySelector('span').textContent = status;
            } else {
                headerStatus.classList.add('hidden');
            }
        }

        // Update sidebar indicator
        const phoneIndicator = document.getElementById('phone-indicator');
        if (phoneIndicator) {
            if (this.currentCall) {
                phoneIndicator.classList.remove('bg-success-500');
                phoneIndicator.classList.add('bg-danger-500');
            } else {
                phoneIndicator.classList.remove('bg-danger-500');
                phoneIndicator.classList.add('bg-success-500');
            }
        }
    }

    async checkPhoneStatus() {
        try {
            const status = await this.app.apiCall('/voip/status/');
            this.isConnected = status.connected;
            
            if (this.isConnected) {
                this.updatePhoneStatus('Ready to call');
                document.getElementById('phone-status').classList.remove('hidden');
                document.getElementById('phone-status').classList.add('flex');
            } else {
                this.updatePhoneStatus('Disconnected', 'text-danger-600');
            }
        } catch (error) {
            this.isConnected = false;
            this.updatePhoneStatus('Error', 'text-danger-600');
        }
    }

    async findContactByNumber(number) {
        try {
            const response = await this.app.apiCall(`/contacts/?phone=${encodeURIComponent(number)}`);
            return response.results && response.results.length > 0 ? response.results[0] : null;
        } catch (error) {
            return null;
        }
    }

    addToRecentCalls(number, direction = 'outbound') {
        const call = {
            number: number,
            direction: direction,
            timestamp: new Date(),
            duration: this.currentCall ? Math.floor((new Date() - this.currentCall.startTime) / 1000) : 0
        };

        this.recentCalls.unshift(call);
        this.recentCalls = this.recentCalls.slice(0, 10); // Keep only last 10 calls
        
        this.updateRecentCallsDisplay();
        this.saveRecentCalls();
    }

    updateRecentCallsDisplay() {
        const container = document.getElementById('recent-calls');
        if (!container) return;

        container.innerHTML = this.recentCalls.slice(0, 5).map(call => `
            <div class="flex items-center justify-between py-2 px-3 hover:bg-gray-50 rounded-lg cursor-pointer" onclick="app.phone.dialNumber('${call.number}')">
                <div class="flex items-center space-x-3">
                    <i class="fas fa-phone-${call.direction === 'inbound' ? 'volume' : 'alt'} text-xs text-gray-400"></i>
                    <div>
                        <p class="text-sm font-medium text-gray-900">${call.number}</p>
                        <p class="text-xs text-gray-500">${this.formatCallTime(call.timestamp)}</p>
                    </div>
                </div>
                <button onclick="event.stopPropagation(); app.phone.dialNumber('${call.number}')" 
                        class="text-primary-600 hover:text-primary-700">
                    <i class="fas fa-phone text-xs"></i>
                </button>
            </div>
        `).join('');
    }

    dialNumber(number) {
        document.getElementById('phone-number').value = number;
        this.makeCall();
    }

    formatCallTime(timestamp) {
        const now = new Date();
        const diff = now - timestamp;
        const minutes = Math.floor(diff / 60000);
        
        if (minutes < 1) return 'Just now';
        if (minutes < 60) return `${minutes}m ago`;
        
        const hours = Math.floor(minutes / 60);
        if (hours < 24) return `${hours}h ago`;
        
        return timestamp.toLocaleDateString();
    }

    loadRecentCalls() {
        const stored = localStorage.getItem('crm_recent_calls');
        if (stored) {
            try {
                this.recentCalls = JSON.parse(stored).map(call => ({
                    ...call,
                    timestamp: new Date(call.timestamp)
                }));
                this.updateRecentCallsDisplay();
            } catch (error) {
                console.error('Error loading recent calls:', error);
            }
        }
    }

    saveRecentCalls() {
        try {
            localStorage.setItem('crm_recent_calls', JSON.stringify(this.recentCalls));
        } catch (error) {
            console.error('Error saving recent calls:', error);
        }
    }

    playDTMF(digit) {
        // Create DTMF tone for better UX
        try {
            const audioContext = new (window.AudioContext || window.webkitAudioContext)();
            const oscillator = audioContext.createOscillator();
            const gainNode = audioContext.createGain();
            
            // DTMF frequencies
            const frequencies = {
                '1': [697, 1209], '2': [697, 1336], '3': [697, 1477],
                '4': [770, 1209], '5': [770, 1336], '6': [770, 1477],
                '7': [852, 1209], '8': [852, 1336], '9': [852, 1477],
                '*': [941, 1209], '0': [941, 1336], '#': [941, 1477]
            };
            
            if (frequencies[digit]) {
                oscillator.frequency.setValueAtTime(frequencies[digit][0], audioContext.currentTime);
                oscillator.connect(gainNode);
                gainNode.connect(audioContext.destination);
                gainNode.gain.setValueAtTime(0.1, audioContext.currentTime);
                
                oscillator.start();
                oscillator.stop(audioContext.currentTime + 0.1);
            }
        } catch (error) {
            // Fallback for browsers that don't support Web Audio API
            console.log('DTMF:', digit);
        }
    }

    // Handle incoming calls (from WebSocket or polling)
    handleIncomingCall(callData) {
        // Show incoming call notification
        this.showIncomingCallNotification(callData);
        
        // Auto-open phone widget
        this.openDialer();
        
        // Update status
        this.updatePhoneStatus('Incoming Call', 'text-warning-600');
    }

    showIncomingCallNotification(callData) {
        // Create incoming call modal
        const modal = document.createElement('div');
        modal.id = 'incoming-call-modal';
        modal.className = 'fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center';
        
        modal.innerHTML = `
            <div class="bg-white rounded-lg shadow-xl p-6 max-w-sm w-full mx-4">
                <div class="text-center">
                    <div class="w-20 h-20 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-4">
                        <i class="fas fa-phone text-primary-600 text-2xl"></i>
                    </div>
                    <h3 class="text-lg font-medium text-gray-900 mb-2">Incoming Call</h3>
                    <p class="text-gray-600 mb-1">${callData.caller_name || 'Unknown Contact'}</p>
                    <p class="text-sm text-gray-500 mb-6">${callData.number}</p>
                    
                    <div class="flex space-x-3">
                        <button onclick="app.phone.declineCall('${callData.call_id}'); this.closest('#incoming-call-modal').remove();" 
                                class="flex-1 bg-danger-600 hover:bg-danger-700 text-white py-2 px-4 rounded-lg font-medium transition-colors">
                            <i class="fas fa-phone-slash mr-2"></i>Decline
                        </button>
                        <button onclick="app.phone.acceptCall('${callData.call_id}'); this.closest('#incoming-call-modal').remove();" 
                                class="flex-1 bg-success-600 hover:bg-success-700 text-white py-2 px-4 rounded-lg font-medium transition-colors">
                            <i class="fas fa-phone mr-2"></i>Accept
                        </button>
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(modal);
    }

    acceptCall(callId) {
        // API call to accept call
        this.app.apiCall('/voip/call/', {
            method: 'POST',
            body: JSON.stringify({ 
                call_id: callId,
                action: 'accept'
            })
        }).then(response => {
            this.startCall(response.number, { id: callId, ...response });
            this.addToRecentCalls(response.number, 'inbound');
        }).catch(error => {
            this.app.showToast('Error accepting call: ' + error.message, 'error');
        });
    }

    declineCall(callId) {
        // API call to decline call
        this.app.apiCall('/voip/call/', {
            method: 'POST',
            body: JSON.stringify({ 
                call_id: callId,
                action: 'decline'
            })
        }).catch(error => {
            console.error('Error declining call:', error);
        });
        
        this.updatePhoneStatus('Ready to call');
        this.app.showToast('Call declined', 'info');
    }
}