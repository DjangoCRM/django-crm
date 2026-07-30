from django.forms import models


def fk_field(initial):
    if type(initial) in (str, int):
        return str(initial)
    return str(initial.id)


def m2m_field(initial):
    if type(initial[0]) is int:
        return [str(x) for x in initial]
    return [str(x.id) for x in initial]


field_func = {
    models.ModelChoiceField: fk_field,
    models.ModelMultipleChoiceField: m2m_field,
}


def get_form_initials(form, data: dict):
    for key, value in form.base_fields.items():
        if value.initial is not None:
            if value.__class__ in field_func:
                func = field_func[value.__class__]
                data[key] = func(value.initial)
            else:
                _set_form_initial_value(form, data, key, value.initial)

    if 'token' in data:
        data['token'] = data['token']()
    if getattr(form, 'declared_fields'):
        for key, value in form.declared_fields.items():
            if value.initial is not None:
                data[key] = value.initial
    initials = form.initial
    for key, value in initials.items():
        if value is not None:
            _set_form_initial_value(form, data, key, value)
            if key in form.base_fields and value != []:
                field = form.base_fields[key]
                func = field_func.get(field.__class__, None)
                if func is not None:
                    _set_form_initial_value(form, data, key, func(value))


def get_adminform_initials(response) -> dict:
    context = response.context or response.context_data
    form = context['adminform'].form
    data = {}
    get_form_initials(form, data)
    if 'inline_admin_formsets' in context:
        for inline_admin_formset in context['inline_admin_formsets']:
            formset = inline_admin_formset.formset
            data[f"{formset.prefix}-TOTAL_FORMS"] = str(formset.total_form_count())
            data[f"{formset.prefix}-INITIAL_FORMS"] = str(formset.initial_form_count())

            for form in formset:
                get_form_initials(form, data)
                data[f"{form.prefix}-id"] = str(form.instance.id)

    return data


def _set_form_initial_value(form, data: dict, key: str, value) -> None:
    if form.prefix:
        data[f"{form.prefix}-{key}"] = value
    else:
        data[key] = value
