from webcrm.voip_config import build_voip_settings

_voip_settings = build_voip_settings()
VOIP = _voip_settings['VOIP']
VOIP_FORWARD_DATA = _voip_settings['VOIP_FORWARD_DATA']
VOIP_FORWARDING_IP = _voip_settings['VOIP_FORWARDING_IP']
VOIP_FORWARD_URL = _voip_settings['VOIP_FORWARD_URL']
ZADARMA_PROVIDER_ALLOWLIST = _voip_settings['ZADARMA_PROVIDER_ALLOWLIST']
