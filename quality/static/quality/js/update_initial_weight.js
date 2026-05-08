// Sets the initial weight value for the corresponding user-selected signal.

window.addEventListener('load', function() {
    const prefixId = "id_transactionqualityevent_set-";
    const suffixId = "-signal";
    const signalSelect = document.getElementById('id_transactionqualityevent_set-__prefix__-signal');    
    const initialWeights = signalSelect.getAttribute('initial_weights');
    // Convert the initialWeights string like "<key>: <value>, <key>: <value>" to the object
    const weightsObj = JSON.parse(initialWeights);
    const qualityFieldset = document.getElementById('transactionqualityevent_set-group');
    
    // Use event delegation to listen only to signal field changes
    qualityFieldset.addEventListener('change', function(event) {
        // Check if the changed element is a signal field
        if (!event.target.id.startsWith(prefixId) || !event.target.id.endsWith(suffixId)) {
            return;
        }
        
        // Update the corresponding weight input field
        const weightInputId = event.target.id.replace(suffixId, '-weight');
        const weightInput = document.getElementById(weightInputId);
        if (weightInput) {
            const selectedSignalId = event.target.value;
            if (weightsObj.hasOwnProperty(selectedSignalId)) {
                weightInput.value = weightsObj[selectedSignalId];
            } else {
                weightInput.value = '';
            }
        }
    });
});