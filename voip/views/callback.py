import json
from django.conf import settings
from django.http.response import HttpResponse
from django.views.generic.edit import FormView
from django.utils.module_loading import import_string
from django.utils.translation import gettext as _

from voip.forms.connectionform import ConnectionForm
from voip.models import Connection


class ConnectionView(FormView):
    template_name = 'voip/connection.html'
    form_class = ConnectionForm
    
    def get(self, request, *args, **kwargs):
        """Handle GET requests: instantiate a blank version of the form."""
        connections = self.get_connections(request)
        if not connections:
            return HttpResponse(
                _('You do not have a VoiP connection configured. Please contact your administrator.')
            ) 
        to_number = request.GET.get('number')
        connections_num = len(connections)
        if connections_num > 1:
            choises = (
                    (connection.id, f'{connection.callerid} ({connection.provider})') 
                    for connection in connections
            ) 
            self.initial = {'to_number': to_number}
            return self.render_to_response(self.get_context_data(choises=choises))  
        connection = connections.first() 
        
        message = get_callback(connection, to_number)
        return HttpResponse(message)
        
    def get_context_data(self, **kwargs):
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        kwargs['form'].fields['callerid'].choices = kwargs['choises']
        return super().get_context_data(**kwargs)  
    
    def post(self, request, *args, **kwargs):
        """
        Handle POST requests: instantiate a form instance with the passed
        POST variables and then check if it's valid.
        """        
        self.object = None   
        connections = self.get_connections(request)
        choises = (
                (connection.id, f'{connection.callerid} ({connection.provider})') 
                for connection in connections
        )         
        form = self.get_form()
        form.fields['callerid'].choices = choises
        if form.is_valid():
            connection_id = form.cleaned_data['callerid']
            connection = connections.get(id=connection_id)
            to_number = form.cleaned_data['to_number']
            message = get_callback(connection, to_number)
            return HttpResponse(message)
        else:
            return self.form_invalid(form)        

    @staticmethod
    def get_connections(request):
        return Connection.objects.filter(
            owner=request.user,
            active=True
        )


def get_callback(connection: Connection, to_number: str)->str:
    """Make callback through Connection of VoIP backend"""
    backends = settings.VOIP
    backend = next(
        backend for backend in backends 
        if backend["PROVIDER"] == connection.provider
    )
    backend_cls = import_string(backend['BACKEND'])
    # Initialize backend with provided OPTIONS to support multiple providers
    voip = backend_cls(**backend['OPTIONS'])
    response = voip.make_query(connection.number, to_number)
    # Support both string (JSON text) and dict responses
    if isinstance(response, str):
        data = json.loads(response)
    else:
        data = response
    message = _('That something is wrong ((. Notify the administrator.')
    status = data.get('status')
    # Treat both Zadarma ('success') and OnlinePBX ('1') as success
    if status in ('success', '1', 1, True):
        message = _('Expect a call to your smartphone')
    elif status in ('error', 0, '0', False):
        # Zadarma: message in data['message']
        # OnlinePBX: may include comment/errorCode
        err = data.get('message') or data.get('comment') or data.get('errorCode') or ''
        message = f'Error! {err}'

    return message
