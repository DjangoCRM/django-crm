import logging
import socket
import ssl
import time
from typing import Dict, Iterable, Tuple

from django.utils import timezone

from voip.models import IncomingCall
from voip.utils import find_objects_by_phone
from voip.utils import load_asterisk_config
from voip.utils import normalize_number
from voip.utils import resolve_targets

logger = logging.getLogger(__name__)

AMI_DEFAULTS = {
    'HOST': '127.0.0.1',
    'PORT': 5038,
    'USERNAME': '',
    'SECRET': '',
    'USE_SSL': False,
    'CONNECT_TIMEOUT': 5,
    'RECONNECT_DELAY': 5,
}


class AmiClient:
    def __init__(self, config: Dict):
        self.host = config.get('HOST', AMI_DEFAULTS['HOST'])
        self.port = int(config.get('PORT', AMI_DEFAULTS['PORT']))
        self.username = config.get('USERNAME', AMI_DEFAULTS['USERNAME'])
        self.secret = config.get('SECRET', AMI_DEFAULTS['SECRET'])
        self.use_ssl = config.get('USE_SSL', AMI_DEFAULTS['USE_SSL'])
        self.connect_timeout = config.get(
            'CONNECT_TIMEOUT', AMI_DEFAULTS['CONNECT_TIMEOUT']
        )
        self.socket = None
        self.stream = None

    def connect(self):
        sock = socket.create_connection(
            (self.host, self.port),
            timeout=self.connect_timeout,
        )
        if self.use_ssl:
            context = ssl.create_default_context()
            sock = context.wrap_socket(sock, server_hostname=self.host)
        self.socket = sock
        self.socket.settimeout(None)  # allow blocking reads for event stream
        self.stream = sock.makefile('rb')
        self._login()

    def _login(self):
        self.send_action(
            'Login',
            Username=self.username,
            Secret=self.secret,
            Events='on'
        )

    def close(self):
        try:
            if self.socket:
                self.socket.close()
        finally:
            self.socket = None
            self.stream = None

    def send_action(self, action: str, **headers):
        if not self.socket:
            raise ConnectionError("AMI socket is not connected")
        lines = [f"Action: {action}"]
        for key, value in headers.items():
            lines.append(f"{key}: {value}")
        payload = "\r\n".join(lines) + "\r\n\r\n"
        self.socket.sendall(payload.encode())

    def events(self) -> Iterable[Dict]:
        """
        Yield parsed AMI events until the connection drops.
        """
        buffer = []
        while True:
            raw = self.stream.readline()
            if not raw:
                raise ConnectionError("AMI connection closed")
            line = raw.decode(errors='ignore').strip()
            if not line and buffer:
                yield self._parse_event(buffer)
                buffer = []
                continue
            if not line:
                continue
            buffer.append(line)

    @staticmethod
    def _parse_event(lines: Iterable[str]) -> Dict:
        event = {}
        for line in lines:
            if ':' not in line:
                continue
            key, _, value = line.partition(':')
            event[key.strip()] = value.strip()
        return event


class AmiListener:
    """
    Listens to Asterisk AMI events and creates IncomingCall records.
    """
    def __init__(self):
        config = AMI_DEFAULTS | load_asterisk_config()
        self.config = config
        self.reconnect_delay = config.get(
            'RECONNECT_DELAY',
            AMI_DEFAULTS['RECONNECT_DELAY']
        )

    def run_forever(self, stop_after_one: bool = False):
        while True:
            try:
                self._run_once()
                if stop_after_one:
                    return
            except KeyboardInterrupt:
                logger.info("Stopping AMI listener")
                return
            except Exception as exc:  # noqa: BLE001
                logger.exception("AMI listener error: %s", exc)
                time.sleep(self.reconnect_delay)

    def _run_once(self):
        client = AmiClient(self.config)
        client.connect()
        logger.info(
            "Connected to Asterisk AMI at %s:%s",
            self.config.get('HOST'),
            self.config.get('PORT'),
        )
        try:
            for event in client.events():
                self._handle_event(event)
        finally:
            client.close()
            logger.info("AMI connection closed, reconnecting soon")

    def _handle_event(self, event: Dict):
        if not self._is_relevant(event):
            return
        caller_id, extension = self._extract_numbers(event)
        if not caller_id:
            return

        contact, lead, deal, error = find_objects_by_phone(caller_id)
        if error:
            logger.warning("AMI lookup error: %s", error)
            return
        matched_obj = contact or lead
        if not matched_obj:
            return

        targets = resolve_targets(extension, matched_obj)
        if not targets:
            return

        for user in targets:
            if not user or not user.is_active:
                continue
            if self._has_recent_notification(user.id, caller_id):
                continue
            IncomingCall.objects.create(
                user=user,
                caller_id=caller_id,
                client_name=getattr(matched_obj, 'full_name', str(matched_obj)),
                client_type=str(matched_obj._meta.verbose_name),
                client_id=matched_obj.id,
                client_url=matched_obj.get_absolute_url(),
                raw_payload=event,
            )

    @staticmethod
    def _is_relevant(event: Dict) -> bool:
        """
        Accept only ringing/new-channel style events with caller id present.
        """
        caller = (
            event.get('CallerIDNum')
            or event.get('CallerID')
            or event.get('From')
            or event.get('ConnectedLineNum')
            or ''
        )
        if not caller:
            return False

        event_name = event.get('Event', '').lower()
        if event_name not in {'newchannel', 'newstate', 'dial'}:
            return False

        state = (
            event.get('ChannelStateDesc')
            or event.get('State')
            or ''
        ).lower()
        return state in {'ring', 'ringing', 'down'} or event_name == 'dial'

    @staticmethod
    def _extract_numbers(event: Dict) -> Tuple[str, str]:
        caller = (
            event.get('CallerIDNum')
            or event.get('CallerID')
            or event.get('From')
            or event.get('ConnectedLineNum')
            or ''
        )
        extension = (
            event.get('Exten')
            or event.get('Extension')
            or event.get('DestExten')
            or event.get('DialString')
            or event.get('ConnectedLineNum')
            or ''
        )
        return normalize_number(caller), normalize_number(extension)

    @staticmethod
    def _has_recent_notification(user_id: int, caller_id: str) -> bool:
        five_minutes_ago = timezone.now() - timezone.timedelta(minutes=5)
        return IncomingCall.objects.filter(
            user_id=user_id,
            caller_id=caller_id,
            is_consumed=False,
            created_at__gte=five_minutes_ago
        ).exists()
