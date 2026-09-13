(function(){
    // Recalculate amount for an inline output row when product or quantity changes.
    // Listens to changes on inputs named like "<prefix>-product" and "<prefix>-quantity".
    // Fetches product tier price by calling the server endpoint with current deal tier and deal currency.

    function getPrefixFromName(name, suffix) {
        // name e.g. "outputs-0-product" suffix "-product"
        if (!name || !suffix) return null;
        if (name.endsWith(suffix)) return name.slice(0, -suffix.length);
        return null;
    }

    function findField(prefix, fieldName) {
        var input = document.querySelector('[name="' + prefix + '-' + fieldName + '"]');
        if (!input) {
            // try id based
            input = document.getElementById('id_' + prefix + '-' + fieldName);
        }
        return input;
    }

    var debounceTimers = {};
    // keep last seen values for product/quantity inputs to detect programmatic changes
    var prevValues = {};

    function getDealPriceContext() {
        var tierEl = document.getElementById('id_tier_name');
        var dealCurrencyEl = document.getElementById('id_currency');
        if (!tierEl || !dealCurrencyEl) return null;

        var tierId = tierEl.value;
        var dealCurrencyId = dealCurrencyEl.value;
        if (!tierId || !dealCurrencyId) return null;

        var base = tierEl.getAttribute('product_price_info_url');
        if (!base) return null;

        return {
            tierId: tierId,
            dealCurrencyId: dealCurrencyId,
            base: base
        };
    }

    function updateOutputCurrencyReadonlyFields() {
        var dealCurrencyEl = document.getElementById('id_currency');
        if (!dealCurrencyEl) return;

        var text = '';
        if (dealCurrencyEl.options && dealCurrencyEl.selectedIndex >= 0) {
            text = (dealCurrencyEl.options[dealCurrencyEl.selectedIndex] || {}).text || '';
        }
        if (!text && dealCurrencyEl.value) {
            text = dealCurrencyEl.value;
        }

        var selectors = [
            '.field-show_currency .readonly',
            '[id$="-show_currency"]',
            '[name$="-show_currency"]'
        ];
        var seen = [];
        selectors.forEach(function(selector){
            var nodes = document.querySelectorAll(selector);
            nodes.forEach(function(el){
                if (!el || seen.indexOf(el) !== -1 || !el.tagName) return;
                seen.push(el);
                var value = text || '—';
                if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA' || el.tagName === 'SELECT') {
                    el.value = value;
                    return;
                }
                if (el.textContent !== undefined) {
                    el.textContent = value;
                } else {
                    el.innerHTML = value;
                }
            });
        });
    }

    function updateAmountForPrefix(prefix) {
        var productField = findField(prefix, 'product');
        var quantityField = findField(prefix, 'quantity');
        var amountField = findField(prefix, 'amount');
        if (!productField || !quantityField || !amountField) return;

        var productId = productField.value;
        var quantity = parseFloat(quantityField.value) || 0;
        if (!productId || !quantity) return;

        var priceContext = getDealPriceContext();
        if (!priceContext) return;

        var params = new URLSearchParams({
            product: productId,
            quantity: quantity,
            tier_name: priceContext.tierId,
            deal_currency: priceContext.dealCurrencyId
        });
        var url = priceContext.base + '?' + params.toString();

        if (debounceTimers[prefix]) clearTimeout(debounceTimers[prefix]);
        debounceTimers[prefix] = setTimeout(function(){
            fetch(url, {credentials: 'same-origin'})
                .then(function(resp){ return resp.json(); })
                .then(function(data){
                    if (!data.ok) return;
                    if (!data.amount) return;
                    amountField.value = data.amount;
                    var evt = new Event('change', {bubbles: true});
                    amountField.dispatchEvent(evt);
                })
                .catch(function(err){
                    console.error('product price info error', err);
                });
        }, 150);
    }

    function recalculateAllOutputAmounts() {
        var productFields = document.querySelectorAll('input[name$="-product"]');
        productFields.forEach(function(productField){
            var name = productField.name || productField.getAttribute('name');
            var prefix = getPrefixFromName(name, '-product');
            if (!prefix) return;
            updateAmountForPrefix(prefix);
        });
    }

    function onChangeProductOrQuantity(e) {
        // allow calling with element or event
        var target = e && e.target ? e.target : e;
        if (!target) return;
        // if called with a synthetic object having name/value
        var name = target.name || target.getAttribute && target.getAttribute('name');
        if (!name) return;
        var name = name || (target.name || (target.getAttribute && target.getAttribute('name')));
        if (!name) return;
        var prefix = null;
        if (name.indexOf('-product') !== -1) prefix = getPrefixFromName(name, '-product');
        if (name.indexOf('-quantity') !== -1) prefix = getPrefixFromName(name, '-quantity');
        if (!prefix) return;

        updateAmountForPrefix(prefix);
    }

    function attachListeners() {
        // delegate to document: attach change/input/blur listeners to catch different widgets
        function delegateEvent(e){
            var name = e.target.name || '';
            if (name.indexOf('-product') !== -1 || name.indexOf('-quantity') !== -1) {
                onChangeProductOrQuantity(e);
            }
        }
        document.addEventListener('change', delegateEvent);
        document.addEventListener('input', delegateEvent);
        document.addEventListener('blur', delegateEvent, true); // capture blurs

        // related-lookup popup links: when clicked, the value will be set later by popup - call handler after short delay
        document.addEventListener('click', function(e){
            var el = e.target;
            if (el && el.classList && el.classList.contains('related-lookup')) {
                // poll for changes in product inputs for short period after popup likely closes
                var start = Date.now();
                var prev = {};
                var interval = setInterval(function(){
                    var inputs = document.querySelectorAll('input[name$="-product"]');
                    inputs.forEach(function(inp){
                        var name = inp.getAttribute('name') || inp.name;
                        var val = inp.value;
                        if (prev[name] !== val) {
                            prev[name] = val;
                            var evt = new Event('change', {bubbles: true});
                            inp.dispatchEvent(evt);
                        }
                    });
                    if (Date.now() - start > 2000) clearInterval(interval);
                }, 200);
            }
        });

        function handleDealFieldChange(){
            updateOutputCurrencyReadonlyFields();
            setTimeout(recalculateAllOutputAmounts, 100);
        }

        ['id_tier_name', 'id_currency'].forEach(function(fieldId){
            var field = document.getElementById(fieldId);
            if (!field) return;
            field.addEventListener('change', handleDealFieldChange);
            field.addEventListener('input', handleDealFieldChange);
        });

        // MutationObserver as fallback to detect programmatic value changes
        var observer = new MutationObserver(function(muts){
            muts.forEach(function(m){
                var target = m.target;
                if (target && target.name && (target.name.indexOf('-product') !== -1 || target.name.indexOf('-quantity') !== -1)) {
                    onChangeProductOrQuantity({target: target});
                }
                if (target && (target.id === 'id_tier_name' || target.id === 'id_currency')) {
                    handleDealFieldChange();
                }
            });
        });
        // observe attribute changes for inputs
        var inputs = document.querySelectorAll('input[name$="-product"], input[name$="-quantity"]');
        inputs.forEach(function(inp){
            observer.observe(inp, {attributes: true, attributeFilter: ['value']});
        });
        ['id_tier_name', 'id_currency'].forEach(function(fieldId){
            var field = document.getElementById(fieldId);
            if (field) {
                observer.observe(field, {attributes: true, attributeFilter: ['value']});
            }
        });
    }

    // run on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function(){ attachListeners(); startPolling(); });
    } else {
        attachListeners();
        startPolling();
    }

    // global polling to detect programmatic changes that don't trigger events
    function startPolling(){
        // initialize prevValues
        var inputs = document.querySelectorAll('input[name$="-product"], input[name$="-quantity"]');
        inputs.forEach(function(inp){
            var n = inp.name || inp.getAttribute('name');
            prevValues[n] = inp.value;
        });
        setInterval(function(){
            var inputs = document.querySelectorAll('input[name$="-product"], input[name$="-quantity"]');
            inputs.forEach(function(inp){
                var name = inp.name || inp.getAttribute('name');
                var val = inp.value;
                if (prevValues[name] === undefined) {
                    prevValues[name] = val;
                } else if (prevValues[name] !== val) {
                    prevValues[name] = val;
                    // call handler with element
                    onChangeProductOrQuantity(inp);
                }
            });
        }, 500);
    }

})();
