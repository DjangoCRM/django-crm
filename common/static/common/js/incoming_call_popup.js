(function () {
  if (window.CRMIncomingCallPollerStarted) return;
  window.CRMIncomingCallPollerStarted = true;

  const pollUrl = window.INCOMING_CALL_POLL_URL;
  if (!pollUrl) return;

  const pollIntervalMs = window.INCOMING_CALL_POLL_INTERVAL_MS || 4000;
  const popupTtlMs = window.INCOMING_CALL_POPUP_TTL_MS || 20000;
  let hideTimer = null;
  let snoozedUntil = Number(sessionStorage.getItem('crmIncomingCallSnoozeUntil') || 0);

  function createContainer() {
    let box = document.getElementById('crm-incoming-call');
    if (box) return box;
    box = document.createElement('div');
    box.id = 'crm-incoming-call';
    box.setAttribute('role', 'alert');
    box.style.position = 'fixed';
    box.style.top = '16px';
    box.style.right = '16px';
    box.style.zIndex = '9999';
    box.style.minWidth = '280px';
    box.style.maxWidth = '360px';
    box.style.padding = '16px';
    box.style.borderRadius = '10px';
    box.style.boxShadow = '0 12px 32px rgba(0, 0, 0, 0.25)';
    box.style.background = 'linear-gradient(135deg, #233d4d 0%, #23949f 100%)';
    box.style.color = '#fff';
    box.style.display = 'none';
    box.style.fontFamily = 'Inter, "Segoe UI", system-ui, -apple-system, sans-serif';
    box.innerHTML = `
      <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px;">
        <span class="material-icons" aria-hidden="true">call</span>
        <div>
          <div style="font-size:14px;opacity:0.85;">Incoming call</div>
          <div id="crm-incoming-call-number" style="font-size:18px;font-weight:700;"></div>
        </div>
        <button id="crm-incoming-call-close" aria-label="Close" style="margin-left:auto;background:rgba(255,255,255,0.1);border:none;color:white;border-radius:8px;padding:4px 8px;cursor:pointer;">×</button>
      </div>
      <div id="crm-incoming-call-name" style="font-size:15px;font-weight:600;margin-bottom:6px;"></div>
      <div id="crm-incoming-call-type" style="font-size:13px;opacity:0.85;margin-bottom:10px;"></div>
      <a id="crm-incoming-call-link" href="#" target="_blank" style="display:inline-flex;align-items:center;gap:6px;background:#fff;color:#233d4d;border-radius:8px;padding:10px 12px;font-weight:700;text-decoration:none;box-shadow:0 4px 12px rgba(0,0,0,0.2);">
        <span class="material-icons" aria-hidden="true" style="font-size:20px;">open_in_new</span>
        Open client card
      </a>
      <div style="margin-top:10px;display:flex;gap:8px;">
        <button id="crm-incoming-call-snooze" style="flex:1;background:rgba(255,255,255,0.12);border:none;color:#fff;padding:8px 10px;border-radius:8px;cursor:pointer;">Snooze 10m</button>
      </div>
    `;
    document.body.appendChild(box);
    const closeBtn = box.querySelector('#crm-incoming-call-close');
    closeBtn.addEventListener('click', hideBox);
    const snoozeBtn = box.querySelector('#crm-incoming-call-snooze');
    snoozeBtn.addEventListener('click', snoozeTenMinutes);
    return box;
  }

  function showCall(call) {
    if (Date.now() < snoozedUntil) {
      return;
    }
    const box = createContainer();
    if (!box) return;
    box.querySelector('#crm-incoming-call-number').textContent = call.caller_id || 'Unknown number';
    box.querySelector('#crm-incoming-call-name').textContent = call.client_name || 'Client';
    box.querySelector('#crm-incoming-call-type').textContent = call.client_type || '';
    const link = box.querySelector('#crm-incoming-call-link');
    if (call.client_url) {
      link.href = call.client_url;
      link.style.pointerEvents = 'auto';
      link.style.opacity = '1';
    } else {
      link.removeAttribute('href');
      link.style.pointerEvents = 'none';
      link.style.opacity = '0.6';
    }
    box.style.display = 'block';
    box.style.transform = 'translateY(-8px)';
    box.style.opacity = '0';
    requestAnimationFrame(() => {
      box.style.transition = 'opacity 150ms ease, transform 150ms ease';
      box.style.opacity = '1';
      box.style.transform = 'translateY(0)';
    });
    if (hideTimer) clearTimeout(hideTimer);
    hideTimer = setTimeout(hideBox, popupTtlMs);
  }

  function hideBox() {
    const box = document.getElementById('crm-incoming-call');
    if (!box) return;
    box.style.display = 'none';
  }

  function snoozeTenMinutes() {
    snoozedUntil = Date.now() + 10 * 60 * 1000;
    sessionStorage.setItem('crmIncomingCallSnoozeUntil', snoozedUntil);
    hideBox();
  }

  function poll() {
    if (Date.now() < snoozedUntil) {
      return;
    }
    fetch(pollUrl, {
      credentials: 'same-origin',
      headers: { 'X-Requested-With': 'XMLHttpRequest' },
    })
      .then((resp) => {
        if (resp.status === 403 || resp.status === 401) {
          clearInterval(timer);
        }
        return resp.json();
      })
      .then((data) => {
        if (data && data.incoming_call) {
          showCall(data.incoming_call);
        }
      })
      .catch(() => {});
  }

  const timer = setInterval(poll, pollIntervalMs);
  poll();
})();
