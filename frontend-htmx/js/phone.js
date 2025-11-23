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
        this.setupTabs();
    }

    setupTabs() {
        const tabs = document.querySelectorAll('.phone-tab');
        const panels = document.querySelectorAll('.phone-tab-panel');

        tabs.forEach(tab => {
            tab.addEventListener('click', () => {
                const tabId = tab.dataset.tab;

                tabs.forEach(t => {
                    t.classList.remove('active', 'border-primary', 'text-primary');
                    t.classList.add('border-transparent', 'text-gray-500', 'hover:text-gray-700', 'hover:border-gray-300');
                });
                tab.classList.add('active', 'border-primary', 'text-primary');
                tab.classList.remove('border-transparent', 'text-gray-500', 'hover:text-gray-700', 'hover:border-gray-300');

                panels.forEach(panel => {
                    if (panel.id === `phone-panel-${tabId}`) {
                        panel.classList.remove('hidden');
                    } else {
                        panel.classList.add('hidden');
                    }
                });
            });
        });
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
            
            // --- MOCK FOR DEVELOPMENT ---
            // The '/voip/call/' endpoint is not yet implemented.
            // This simulates a successful call initiation.
            console.log(`MOCK: Initiating call to ${phoneNumber}`);
            const response = { id: `mock_call_${Date.now()}` };
            
            /*
            // ORIGINAL CODE - Restore when backend is ready
            // Simulate API call to initiate call
            const response = await this.app.apiCall('/voip/call/', {
                method: 'POST',
                body: JSON.stringify({ 
                    number: phoneNumber,
                    action: 'dial'
                })
            });
            */

            // Simulate a short delay for call connection
            setTimeout(() => {
                this.startCall(phoneNumber, response);
                this.addToRecentCalls(phoneNumber, 'outbound');
            }, 1500); // 1.5 second delay to simulate connection time

        } catch (error) {
            // This catch block will now only handle errors from the mocked process
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
            direction: callData.direction || 'outbound',
            ...callData
        };

        // Show active call interface
        document.getElementById('phone-main-content').classList.add('hidden');
        document.getElementById('active-call').classList.remove('hidden');

        // Update call info
        document.getElementById('caller-number').textContent = number;
        
        // Try to find contact for this number
        this.findContactByNumber(number).then(contact => {
            if (contact) {
                document.getElementById('caller-name').textContent = contact.full_name;
            } else {
                document.getElementById('caller-name').textContent = 'Unknown Contact';
            }
        });

        // Start call timer
        this.startCallTimer();
        
        // Update phone status
        this.updatePhoneStatus('In Call', 'text-success-600');
    }

    endCall() {
        if (!this.currentCall) return;

        console.log("MOCK: Ending call", this.currentCall.id);
        /*
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
        */

        // Stop timer
        if (this.callTimer) {
            clearInterval(this.callTimer);
            this.callTimer = null;
        }

        // Log the call before clearing it
        this.addToRecentCalls(this.currentCall.number, this.currentCall.direction || 'outbound');

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

        // MOCK: Simulate API call to toggle mute
        console.log(`MOCK: Toggling mute to ${this.currentCall.isMuted}`);
        /*
        // API call to toggle mute
        this.app.apiCall('/voip/call/', {
            method: 'POST',
            body: JSON.stringify({ 
                call_id: this.currentCall.id,
                action: 'mute',
                muted: this.currentCall.isMuted
            })
        }).catch(console.error);
        */
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

        // MOCK: Simulate API call to toggle hold
        console.log(`MOCK: Toggling hold to ${this.currentCall.isOnHold}`);
        /*
        // API call to toggle hold
        this.app.apiCall('/voip/call/', {
            method: 'POST',
            body: JSON.stringify({ 
                call_id: this.currentCall.id,
                action: 'hold',
                on_hold: this.currentCall.isOnHold
            })
        }).catch(console.error);
        */
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
        document.getElementById('phone-main-content').classList.add('hidden');
        document.getElementById('active-call').classList.remove('hidden');
        
        document.getElementById('caller-number').textContent = number;
        document.getElementById('caller-name').textContent = 'Calling...';
        document.getElementById('call-duration').textContent = 'Connecting...';
        
        this.updatePhoneStatus('Calling...', 'text-warning-600');
    }

    resetDialer() {
        document.getElementById('active-call').classList.add('hidden');
        document.getElementById('phone-main-content').classList.remove('hidden');
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
        // --- MOCK FOR DEVELOPMENT ---
        // This is mocked because the backend API endpoint /voip/status/ is not yet implemented.
        // This ensures the phone widget is accessible for UI development.
        this.isConnected = true;
        if (this.isConnected) {
            this.updatePhoneStatus('Ready to call');
            const phoneStatusElement = document.getElementById('phone-status');
            if (phoneStatusElement) {
                phoneStatusElement.classList.remove('hidden');
                phoneStatusElement.classList.add('flex');
            }
        } else {
            this.updatePhoneStatus('Disconnected', 'text-danger-600');
        }
        // --- END MOCK ---

        /*
        // ORIGINAL CODE - Restore when backend is ready
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
        */
    }

    async findContactByNumber(number) {
        try {
            const response = await this.app.apiCall(`/contacts/?phone=${encodeURIComponent(number)}`);
            return response.results && response.results.length > 0 ? response.results[0] : null;
        } catch (error) {
            return null;
        }
    }

    async addToRecentCalls(number, direction = 'outbound') {
        let contact = null;
        try {
            contact = await this.findContactByNumber(number);
        } catch (e) {
            console.warn("Could not find contact for number:", number, e);
        }

        const callData = {
            number: number,
            direction: direction,
            duration: this.currentCall ? Math.floor((new Date() - this.currentCall.startTime) / 1000) : 0,
            contact: contact ? contact.id : null,
            voip_call_id: this.currentCall ? this.currentCall.id : null, // Assuming this.currentCall.id holds the voip_call_id
        };

        try {
            // Send call log to backend
            const response = await this.app.apiCall(window.CRM_CONFIG.ENDPOINTS.CALL_LOGS, {
                method: 'POST',
                body: JSON.stringify(callData)
            });
            // Add backend-persisted call to local recentCalls for immediate UI update
            this.recentCalls.unshift({
                ...response, // Use response from backend which includes timestamp and id
                timestamp: new Date(response.timestamp) // Convert timestamp string to Date object
            });
            this.recentCalls = this.recentCalls.slice(0, 10); // Keep only last 10 calls
            this.updateRecentCallsDisplay();
        } catch (error) {
            console.error('Error saving call log to backend, falling back to local storage:', error);
            // Fallback to local storage if backend save fails
            const call = {
                number: number,
                direction: direction,
                timestamp: new Date(),
                duration: callData.duration,
                contact: contact ? contact.id : null,
                voip_call_id: callData.voip_call_id,
            };
            this.recentCalls.unshift(call);
            this.recentCalls = this.recentCalls.slice(0, 10); // Keep only last 10 calls
            this.updateRecentCallsDisplay();
            this._saveRecentCallsLocally(); // Use a private helper for local storage
        }
    }

    _renderCallItem(call) {
        const callItem = document.createElement('div');
        callItem.className = 'flex items-center justify-between py-2 px-3 hover:bg-gray-50 dark:hover:bg-slate-700 rounded-lg cursor-pointer';
        callItem.addEventListener('click', () => {
            this.dialNumber(call.number);
        });

        const flexDiv1 = document.createElement('div');
        flexDiv1.className = 'flex items-center space-x-3';

        const iconI = document.createElement('i');
        // TODO: Update icon for missed calls when backend supports it (e.g. call.status === 'missed')
        iconI.className = `fas fa-phone-${call.direction === 'inbound' ? 'volume' : 'alt'} text-xs text-gray-400`;
        flexDiv1.appendChild(iconI);

        const div2 = document.createElement('div');
        const pNumber = document.createElement('p');
        pNumber.className = 'text-sm font-medium text-gray-900';
        pNumber.textContent = call.number;
        div2.appendChild(pNumber);

        const pTime = document.createElement('p');
        pTime.className = 'text-xs text-gray-500';
        pTime.textContent = this.formatCallTime(new Date(call.timestamp));
        div2.appendChild(pTime);
        flexDiv1.appendChild(div2);
        callItem.appendChild(flexDiv1);

        const button = document.createElement('button');
        button.className = 'text-primary-600 hover:text-primary-700';
        button.addEventListener('click', (e) => {
            e.stopPropagation();
            this.dialNumber(call.number);
        });
        const buttonIcon = document.createElement('i');
        buttonIcon.className = 'fas fa-phone text-xs';
        button.appendChild(buttonIcon);
        callItem.appendChild(button);

        return callItem;
    }

    updateRecentCallsDisplay() {
        const allContainer = document.getElementById('phone-panel-all');
        const missedContainer = document.getElementById('phone-panel-missed');
        if (!allContainer || !missedContainer) return;

        allContainer.innerHTML = '';
        missedContainer.innerHTML = '';
        // Resetting classes in case "No calls" message was shown
        allContainer.className = 'space-y-2';
        missedContainer.className = 'space-y-2';

        const allCalls = this.recentCalls.slice(0, 10); // Show more calls now
        // TODO: Replace this with a proper filter once the backend can identify missed calls.
        // Currently, it just shows all inbound calls as a placeholder.
        const missedCalls = this.recentCalls.filter(call => call.direction === 'inbound').slice(0, 10);

        if (allCalls.length > 0) {
            allCalls.forEach(call => {
                allContainer.appendChild(this._renderCallItem(call));
            });
        } else {
            allContainer.textContent = 'No recent calls.';
            allContainer.className = 'text-center text-gray-500 text-sm py-4';
        }

        if (missedCalls.length > 0) {
            missedCalls.forEach(call => {
                missedContainer.appendChild(this._renderCallItem(call));
            });
        } else {
            missedContainer.textContent = 'No missed calls.';
            missedContainer.className = 'text-center text-gray-500 text-sm py-4';
        }
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

    async loadRecentCalls() {
        try {
            const response = await this.app.apiCall(window.CRM_CONFIG.ENDPOINTS.CALL_LOGS);
            // Assuming backend returns a list of call logs
            this.recentCalls = response.results.map(call => ({
                ...call,
                timestamp: new Date(call.timestamp)
            }));
            this.updateRecentCallsDisplay();
        } catch (error) {
            console.error('Error loading recent calls from backend, falling back to local storage:', error);
            this._loadRecentCallsLocally();
        }
    }

    _saveRecentCallsLocally() {
        try {
            localStorage.setItem('crm_recent_calls', JSON.stringify(this.recentCalls));
        } catch (error) {
            console.error('Error saving recent calls locally:', error);
        }
    }

    _loadRecentCallsLocally() {
        const stored = localStorage.getItem('crm_recent_calls');
        if (stored) {
            try {
                this.recentCalls = JSON.parse(stored).map(call => ({
                    ...call,
                    timestamp: new Date(call.timestamp)
                }));
                this.updateRecentCallsDisplay();
            } catch (error) {
                console.error('Error loading recent calls from local storage:', error);
            }
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

        const modalContent = document.createElement('div');
        modalContent.className = 'bg-white rounded-lg shadow-xl p-6 max-w-sm w-full mx-4 dark:bg-slate-800';

        const textCenterDiv = document.createElement('div');
        textCenterDiv.className = 'text-center';

        const iconContainer = document.createElement('div');
        iconContainer.className = 'w-20 h-20 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-4';
        const icon = document.createElement('i');
        icon.className = 'fas fa-phone text-primary-600 text-2xl';
        iconContainer.appendChild(icon);
        textCenterDiv.appendChild(iconContainer);

        const h3 = document.createElement('h3');
        h3.className = 'text-lg font-medium text-gray-900 mb-2';
        h3.textContent = 'Incoming Call';
        textCenterDiv.appendChild(h3);

        const pCallerName = document.createElement('p');
        pCallerName.className = 'text-gray-600 mb-1';
        pCallerName.textContent = callData.caller_name || 'Unknown Contact'; // XSS-safe
        textCenterDiv.appendChild(pCallerName);

        const pNumber = document.createElement('p');
        pNumber.className = 'text-sm text-gray-500 mb-6';
        pNumber.textContent = callData.number; // XSS-safe
        textCenterDiv.appendChild(pNumber);

        const flexSpaceXDiv = document.createElement('div');
        flexSpaceXDiv.className = 'flex space-x-3';

        const declineButton = document.createElement('button');
        declineButton.className = 'flex-1 bg-danger-600 hover:bg-danger-700 text-white py-2 px-4 rounded-lg font-medium transition-colors';
        declineButton.addEventListener('click', () => {
            this.declineCall(callData.call_id);
            modal.remove();
        });
        const declineIcon = document.createElement('i');
        declineIcon.className = 'fas fa-phone-slash mr-2';
        declineButton.appendChild(declineIcon);
        declineButton.append('Decline');
        flexSpaceXDiv.appendChild(declineButton);

        const acceptButton = document.createElement('button');
        acceptButton.className = 'flex-1 bg-success-600 hover:bg-success-700 text-white py-2 px-4 rounded-lg font-medium transition-colors';
        acceptButton.addEventListener('click', () => {
            this.acceptCall(callData);
            modal.remove();
        });
        const acceptIcon = document.createElement('i');
        acceptIcon.className = 'fas fa-phone mr-2';
        acceptButton.appendChild(acceptIcon);
        acceptButton.append('Accept');
        flexSpaceXDiv.appendChild(acceptButton);

        textCenterDiv.appendChild(flexSpaceXDiv);
        modalContent.appendChild(textCenterDiv);
        modal.appendChild(modalContent);
        document.body.appendChild(modal);
    }

    acceptCall(callData) {
        console.log("MOCK: Accepting call", callData);
        // MOCK: Simulate API call to accept call
        const mockResponse = { number: callData.number, ...callData };
        this.startCall(mockResponse.number, { id: callData.call_id, ...mockResponse });
        // this.addToRecentCalls(mockResponse.number, 'inbound'); // This is now called in endCall

        /*
        // ORIGINAL CODE
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
        */
    }

    declineCall(callId) {
        console.log("MOCK: Declining call", callId);
        // MOCK: Simulate API call to decline call
        /*
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
        */
        
        this.updatePhoneStatus('Ready to call');
        this.app.showToast('Call declined', 'info');
    }
}