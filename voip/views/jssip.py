from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.contrib.auth import get_user_model


class JsSipClientView(LoginRequiredMixin, TemplateView):
    template_name = "voip/jssip_client.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        profile = getattr(self.request.user, "profile", None)
        ctx["jssip"] = {
            "ws_uri": getattr(settings, "JSSIP_WS_URI", ""),
            "sip_uri": getattr(settings, "JSSIP_SIP_URI", ""),
            "sip_password": getattr(settings, "JSSIP_SIP_PASSWORD", ""),
            "display_name": getattr(settings, "JSSIP_DISPLAY_NAME", ""),
        }
        if profile:
            ctx["jssip"].update(
                {
                    "ws_uri": profile.jssip_ws_uri or ctx["jssip"]["ws_uri"],
                    "sip_uri": profile.jssip_sip_uri or ctx["jssip"]["sip_uri"],
                    "sip_password": profile.jssip_sip_password or ctx["jssip"]["sip_password"],
                    "display_name": profile.jssip_display_name or ctx["jssip"]["display_name"],
                }
            )
        return ctx
