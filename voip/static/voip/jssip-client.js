(() => {
  const qs = (id) => document.getElementById(id);
  const statusEl = qs('status');
  const logEl = qs('log');
  const connectBtn = qs('connect_btn');
  const disconnectBtn = qs('disconnect_btn');
  const callBtn = qs('call_btn');
  const hangupBtn = qs('hangup_btn');
  const muteBtn = qs('mute_btn');
  const dtmfBtn = qs('dtmf_btn');
  const dtmfDigits = qs('dtmf_digits');
  const config = window.JSSIP_CONFIG || {};

  let ua = null;
  let session = null;
  let muted = false;

  const setStatus = (text) => {
    statusEl.textContent = text;
  };

  const log = (msg) => {
    const ts = new Date().toISOString();
    logEl.textContent += `[${ts}] ${msg}\n`;
    logEl.scrollTop = logEl.scrollHeight;
  };

  const setButtons = ({ connected, inCall }) => {
    connectBtn.disabled = connected;
    disconnectBtn.disabled = !connected;
    callBtn.disabled = !connected || inCall;
    hangupBtn.disabled = !inCall;
    muteBtn.disabled = !inCall;
    dtmfBtn.disabled = !inCall;
  };

  const resetSession = () => {
    session = null;
    muted = false;
    setButtons({ connected: !!ua && ua.isConnected(), inCall: false });
  };

  const connect = () => {
    const wsUri = (config.ws_uri || '').trim();
    const sipUri = (config.sip_uri || '').trim();
    const password = config.sip_password || '';
    const displayName = config.display_name || '';

    if (!wsUri || !sipUri || !password) {
      log('Missing SIP configuration. Ask admin to fill JsSIP settings in your profile.');
      alert('Missing SIP configuration.');
      return;
    }

    try {
      const socket = new JsSIP.WebSocketInterface(wsUri);
      const configuration = {
        sockets: [socket],
        uri: sipUri,
        password,
        display_name: displayName || undefined,
        session_timers: false,
      };
      ua = new JsSIP.UA(configuration);

      ua.on('connected', () => {
        setStatus('Connected');
        log('UA connected');
        setButtons({ connected: true, inCall: false });
      });
      ua.on('disconnected', () => {
        setStatus('Disconnected');
        log('UA disconnected');
        setButtons({ connected: false, inCall: false });
      });
      ua.on('registered', () => log('Registered'));
      ua.on('unregistered', () => log('Unregistered'));
      ua.on('registrationFailed', (e) => log(`Registration failed: ${e.cause}`));
      ua.on('newRTCSession', (e) => {
        if (session) {
          log('Another session incoming, rejecting');
          e.session.terminate();
          return;
        }
        session = e.session;
        attachSessionHandlers(session);
      });

      ua.start();
    } catch (err) {
      log(`Connect error: ${err}`);
    }
  };

  const disconnect = () => {
    if (session) {
      session.terminate();
    }
    if (ua) {
      ua.stop();
      ua = null;
    }
    setButtons({ connected: false, inCall: false });
    setStatus('Disconnected');
    log('UA stopped');
  };

  const call = () => {
    if (!ua || !ua.isConnected()) {
      alert('UA is not connected');
      return;
    }
    const target = qs('target').value.trim();
    if (!target) {
      alert('Enter target number or SIP URI');
      return;
    }
    const eventHandlers = {};
    const options = {
      mediaConstraints: { audio: true, video: false },
      pcConfig: {
        rtcpMuxPolicy: 'require',
        iceServers: [{ urls: ['stun:stun.l.google.com:19302'] }],
      },
    };
    session = ua.call(target, options, eventHandlers);
    attachSessionHandlers(session);
  };

  const attachSessionHandlers = (sess) => {
    setButtons({ connected: true, inCall: true });
    setStatus('Calling...');
    log(`Session state: ${sess.direction}`);

    sess.on('progress', () => {
      setStatus('Ringing...');
      log('Progress');
    });
    sess.on('accepted', () => {
      setStatus('In call');
      log('Call accepted');
    });
    sess.on('confirmed', () => log('Call confirmed'));
    sess.on('ended', (e) => {
      setStatus('Call ended');
      log(`Call ended: ${e && e.cause ? e.cause : 'normal'}`);
      resetSession();
    });
    sess.on('failed', (e) => {
      setStatus('Call failed');
      log(`Call failed: ${e && e.cause ? e.cause : 'unknown'}`);
      resetSession();
    });
    sess.on('peerconnection', (e) => {
      const pc = e.peerconnection;
      pc.ontrack = (event) => {
        const remoteStream = event.streams[0];
        const audio = new Audio();
        audio.srcObject = remoteStream;
        audio.play().catch(() => {
          log('Autoplay blocked, click to allow audio.');
        });
      };
    });
  };

  const hangup = () => {
    if (session) {
      session.terminate();
    }
  };

  const toggleMute = () => {
    if (!session) return;
    muted = !muted;
    session[muted ? 'mute' : 'unmute']({ audio: true });
    muteBtn.textContent = muted ? 'Unmute' : 'Mute';
    log(muted ? 'Muted microphone' : 'Unmuted microphone');
  };

  const sendDTMF = () => {
    if (!session) return;
    const digits = dtmfDigits.value.trim();
    if (!digits) return;
    session.sendDTMF(digits);
    log(`Sent DTMF: ${digits}`);
  };

  connectBtn.addEventListener('click', connect);
  disconnectBtn.addEventListener('click', disconnect);
  callBtn.addEventListener('click', call);
  hangupBtn.addEventListener('click', hangup);
  muteBtn.addEventListener('click', toggleMute);
  dtmfBtn.addEventListener('click', sendDTMF);

  setButtons({ connected: false, inCall: false });
  setStatus('Disconnected');

  // auto-connect if config is complete
  if (config.ws_uri && config.sip_uri && config.sip_password) {
    connect();
  }
})();
