// Sets the initial weight value for the corresponding user-selected signal.

window.addEventListener('load', function() {
    const prefixId = "id_transactionqualityevent_set-";
    const suffixId = "-signal";
    const signalSelect = document.getElementById('id_transactionqualityevent_set-__prefix__-signal');    
    const initialWeights = signalSelect.getAttribute('initial_weights');
    // Convert the initialWeights string like "<key>: <value>, <key>: <value>" to the object
    const weightsObj = JSON.parse(initialWeights);
    const qualityFieldset = document.getElementById('transactionqualityevent_set-group');
    qualityFieldset.addEventListener('change', function() {
        // Find the all select fields in dynamic formsets
        const signalFields = document.querySelectorAll(`[id^="${prefixId}"][id$="${suffixId}"]`);
        // Exclude field with id containing "__prefix__"
        const filteredSignalFields = Array.from(signalFields).filter(field => !field.id.includes('__prefix__'));
        // From the resulting list, get the index of the last field
        const lastSignalField = filteredSignalFields[filteredSignalFields.length - 1];
        // Update the corresponding weight input field
        const weightInputId = lastSignalField.id.replace(suffixId, '-weight');
        const lastWeightInput = document.getElementById(weightInputId);
        if (lastWeightInput) {
            const selectedSignalId = lastSignalField.value;
            if (weightsObj.hasOwnProperty(selectedSignalId)) {
                lastWeightInput.value = weightsObj[selectedSignalId];
            } else {
                lastWeightInput.value = '';
            }
        }
    });
});
